"""
NISHA Voice Manager — October 2026
Handles TTS (text-to-speech) and STT (speech-to-text) for all agents.
Primary: Gemini 3.8 Flash TTS (free, 130 languages, 30 studio voices).
"""

import os
import json
import wave
import struct
import logging
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger("nisha.voice_manager")

VOICE_CONFIG_PATH = Path(__file__).parent.parent / "config" / "voice_config.json"

# ─────────────────────────────────────────────
# Voice config loader
# ─────────────────────────────────────────────
def _load_voice_config() -> dict:
    return json.loads(VOICE_CONFIG_PATH.read_text())

_voice_cfg = _load_voice_config()


def get_agent_voice(agent_name: str) -> dict:
    """Return the full voice config for a given agent."""
    return _voice_cfg["agents"].get(agent_name.lower(), {
        "voice": "Sulafat",
        "style": "Warm",
        "fallback_voice": "Aoede",
        "persona_prompt": "Speak naturally and clearly.",
    })


# ─────────────────────────────────────────────
# TTS — Gemini 3.8 Flash TTS
# ─────────────────────────────────────────────
class VoiceManager:
    """
    Manages TTS and STT for all NISHA agents.
    Each agent speaks with its own assigned voice and persona.
    """

    def __init__(self):
        self._cfg        = _voice_cfg
        self._tts_model  = self._cfg["tts_settings"]["model"]
        self._tts_fb     = self._cfg["tts_settings"]["fallback_model"]
        self._sample_rate = self._cfg["tts_settings"]["sample_rate"]
        self._api_key    = os.environ.get("GEMINI_API_KEY", "")

    # ── Public TTS ──────────────────────────────────────────────────────────
    def speak(
        self,
        text: str,
        agent_name: str = "nisha",
        output_path: Optional[str] = None,
        use_fallback_voice: bool = False,
    ) -> Optional[str]:
        """
        Convert text to speech using the agent's assigned voice.
        Returns path to audio file, or None on failure.
        """
        voice_cfg = get_agent_voice(agent_name)
        voice     = voice_cfg["fallback_voice"] if use_fallback_voice else voice_cfg["voice"]
        persona   = voice_cfg.get("persona_prompt", "")

        # Build full text with style direction embedded
        styled_text = self._apply_style(text, persona, voice_cfg)

        logger.info(f"[VoiceManager] {agent_name} speaking as '{voice}' — {len(text)} chars")

        audio_data = self._call_gemini_tts(styled_text, voice)
        if not audio_data:
            # Try fallback voice
            if not use_fallback_voice:
                logger.warning(f"[VoiceManager] Primary voice {voice} failed, trying fallback")
                return self.speak(text, agent_name, output_path, use_fallback_voice=True)
            logger.error(f"[VoiceManager] TTS completely failed for {agent_name}")
            return None

        # Save to file
        path = output_path or tempfile.mktemp(suffix=".wav", prefix=f"nisha_{agent_name}_")
        self._save_wav(audio_data, path)
        return path

    # ── Internal TTS call ───────────────────────────────────────────────────
    def _apply_style(self, text: str, persona: str, voice_cfg: dict) -> str:
        """Prepend delivery style as speech_metadata for Gemini TTS."""
        style = voice_cfg.get("style", "")
        pace  = voice_cfg.get("pace", "measured")
        if persona:
            # Gemini TTS respects inline style instructions in the text
            return f"[{persona}]\n\n{text}"
        return text

    def _call_gemini_tts(self, text: str, voice: str) -> Optional[bytes]:
        """Call Gemini 3.8 Flash TTS API. Returns raw PCM audio bytes."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self._api_key)
            client = genai.Client()
            response = client.models.generate_content(
                model=self._tts_model,
                contents=text,
                config={
                    "response_modalities": ["AUDIO"],
                    "speech_config": [{"voice": voice}],
                }
            )
            # Extract audio bytes from response
            for part in response.candidates[0].content.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    return part.inline_data.data
            return None
        except ImportError:
            return self._call_gemini_tts_rest(text, voice)
        except Exception as e:
            logger.error(f"[VoiceManager] Gemini TTS error: {e}")
            return None

    def _call_gemini_tts_rest(self, text: str, voice: str) -> Optional[bytes]:
        """REST fallback if google-generativeai not installed."""
        try:
            import urllib.request
            import urllib.error
            import base64

            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"{self._tts_model}:generateContent?key={self._api_key}"
            )
            payload = json.dumps({
                "contents": [{"parts": [{"text": text}]}],
                "generationConfig": {
                    "responseModalities": ["AUDIO"],
                    "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}
                }
            }).encode()

            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
                b64  = data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
                return base64.b64decode(b64)
        except Exception as e:
            logger.error(f"[VoiceManager] REST TTS fallback error: {e}")
            return None

    def _save_wav(self, pcm_data: bytes, path: str):
        """Wrap raw PCM in a WAV container."""
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)           # 16-bit
            wf.setframerate(self._sample_rate)
            wf.writeframes(pcm_data)
        logger.info(f"[VoiceManager] Audio saved → {path}")

    # ── STT ─────────────────────────────────────────────────────────────────
    def transcribe(self, audio_path: str) -> Optional[str]:
        """
        Convert audio file to text using Gemini 3.5 Transcribe.
        Returns transcript string or None on failure.
        """
        try:
            import google.generativeai as genai
            genai.configure(api_key=self._api_key)
            client = genai.Client()

            audio_file = client.files.upload(path=audio_path)
            response   = client.models.generate_content(
                model="gemini-3.5-transcribe",
                contents=[
                    "Transcribe this audio accurately.",
                    audio_file
                ]
            )
            transcript = response.text.strip()
            logger.info(f"[VoiceManager] Transcribed {len(transcript)} chars")
            return transcript
        except Exception as e:
            logger.error(f"[VoiceManager] STT error: {e}")
            return None

    # ── Voice info ───────────────────────────────────────────────────────────
    def voice_summary(self) -> dict:
        """Return all agent voice assignments."""
        return {
            agent: {
                "voice": cfg["voice"],
                "style": cfg["style"],
                "fallback": cfg["fallback_voice"],
            }
            for agent, cfg in self._cfg["agents"].items()
        }


# Singleton
_vm: Optional[VoiceManager] = None

def get_voice_manager() -> VoiceManager:
    global _vm
    if _vm is None:
        _vm = VoiceManager()
    return _vm

def speak(text: str, agent: str = "nisha", output_path: Optional[str] = None) -> Optional[str]:
    """Convenience shortcut — call from anywhere."""
    return get_voice_manager().speak(text, agent, output_path)

def transcribe(audio_path: str) -> Optional[str]:
    """Convenience shortcut for STT."""
    return get_voice_manager().transcribe(audio_path)


if __name__ == "__main__":
    vm = VoiceManager()
    print("Voice assignments:")
    for agent, cfg in vm.voice_summary().items():
        print(f"  {agent:10} → {cfg['voice']:15} ({cfg['style']}) | fallback: {cfg['fallback']}")
