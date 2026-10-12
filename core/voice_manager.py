"""
NISHA Voice Manager — October 2026
TTS and STT for all agents. Primary: Gemini 3.8 Flash TTS (free, 130 langs, 30 voices).
"""
import os, json, wave, logging, tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger("nisha.voice_manager")
VOICE_CFG_PATH = Path(__file__).parent.parent / "config" / "voice_config.json"

def _load() -> dict:
    return json.loads(VOICE_CFG_PATH.read_text())

_cfg = _load()

def get_agent_voice(agent_name: str) -> dict:
    return _cfg["agents"].get(agent_name.lower(), {
        "voice": "Sulafat", "style": "Warm", "fallback_voice": "Aoede",
        "persona_prompt": "Speak naturally and clearly.",
    })


class VoiceManager:
    def __init__(self):
        self._cfg        = _cfg
        self._tts_model  = _cfg["tts_settings"]["model"]
        self._sample_rate = _cfg["tts_settings"]["sample_rate"]
        self._api_key    = os.environ.get("GEMINI_API_KEY", "")

    def speak(self, text: str, agent_name: str = "nisha",
              output_path: Optional[str] = None, use_fallback: bool = False) -> Optional[str]:
        vc    = get_agent_voice(agent_name)
        voice = vc["fallback_voice"] if use_fallback else vc["voice"]
        styled = f"[{vc.get('persona_prompt','')}]\n\n{text}" if vc.get("persona_prompt") else text
        logger.info(f"[VoiceManager] {agent_name} → voice={voice} ({len(text)} chars)")
        data = self._call_tts(styled, voice)
        if not data:
            if not use_fallback:
                return self.speak(text, agent_name, output_path, use_fallback=True)
            logger.error(f"[VoiceManager] TTS failed for {agent_name}")
            return None
        path = output_path or tempfile.mktemp(suffix=".wav", prefix=f"nisha_{agent_name}_")
        self._save_wav(data, path)
        return path

    def _call_tts(self, text: str, voice: str) -> Optional[bytes]:
        try:
            import google.generativeai as genai
            genai.configure(api_key=self._api_key)
            client = genai.Client()
            response = client.models.generate_content(
                model=self._tts_model, contents=text,
                config={"response_modalities": ["AUDIO"], "speech_config": [{"voice": voice}]}
            )
            for part in response.candidates[0].content.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    return part.inline_data.data
            return None
        except ImportError:
            return self._call_tts_rest(text, voice)
        except Exception as e:
            logger.error(f"[VoiceManager] TTS error: {e}")
            return None

    def _call_tts_rest(self, text: str, voice: str) -> Optional[bytes]:
        try:
            import urllib.request, base64
            url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
                   f"{self._tts_model}:generateContent?key={self._api_key}")
            payload = json.dumps({
                "contents": [{"parts": [{"text": text}]}],
                "generationConfig": {"responseModalities": ["AUDIO"],
                    "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}
            }).encode()
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                d = json.loads(resp.read())
                return base64.b64decode(d["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
        except Exception as e:
            logger.error(f"[VoiceManager] REST TTS error: {e}")
            return None

    def _save_wav(self, pcm: bytes, path: str):
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(self._sample_rate)
            wf.writeframes(pcm)
        logger.info(f"[VoiceManager] Saved → {path}")

    def transcribe(self, audio_path: str) -> Optional[str]:
        try:
            import google.generativeai as genai
            genai.configure(api_key=self._api_key)
            client = genai.Client()
            audio_file = client.files.upload(path=audio_path)
            response = client.models.generate_content(
                model="gemini-3.5-transcribe",
                contents=["Transcribe this audio accurately.", audio_file]
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"[VoiceManager] STT error: {e}")
            return None

    def voice_summary(self) -> dict:
        return {a: {"voice": c["voice"], "style": c["style"], "fallback": c["fallback_voice"]}
                for a, c in self._cfg["agents"].items()}


_vm: Optional[VoiceManager] = None

def get_voice_manager() -> VoiceManager:
    global _vm
    if _vm is None: _vm = VoiceManager()
    return _vm

def speak(text: str, agent: str = "nisha", output_path: Optional[str] = None) -> Optional[str]:
    return get_voice_manager().speak(text, agent, output_path)

def transcribe(audio_path: str) -> Optional[str]:
    return get_voice_manager().transcribe(audio_path)


if __name__ == "__main__":
    vm = VoiceManager()
    print("Voice assignments:")
    for agent, cfg in vm.voice_summary().items():
        print(f"  {agent:10} → {cfg['voice']:15} ({cfg['style']}) | fallback: {cfg['fallback']}")
