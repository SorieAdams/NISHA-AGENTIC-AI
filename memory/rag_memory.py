"""
rag_memory.py — NISHA Vector/RAG Memory System
ZOEY-inspired: Long-term contextual memory using embedding similarity.
Local-first: uses simple TF-IDF cosine similarity (no external API required).
Upgrade path: swap _embed() for a real embedding model when available.
"""
import json
import math
import re
import datetime
from pathlib import Path
from typing import Optional
import sys


def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()
RAG_PATH = BASE_DIR / "memory" / "rag_store.json"


def _tokenize(text: str) -> list[str]:
    return re.findall(r'\b\w+\b', text.lower())


def _tfidf_vector(tokens: list[str], vocab: dict) -> dict:
    tf: dict = {}
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1
    n = len(tokens) or 1
    return {word: tf.get(word, 0) / n for word in vocab}


def _cosine(a: dict, b: dict, vocab: set) -> float:
    dot = sum(a.get(w, 0) * b.get(w, 0) for w in vocab)
    mag_a = math.sqrt(sum(v ** 2 for v in a.values()))
    mag_b = math.sqrt(sum(v ** 2 for v in b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


class RAGMemory:
    """
    Retrieval-Augmented Generation memory store.
    Stores episodic entries (task, result, evidence, correction, outcome).
    Retrieves relevant entries by similarity to a query.
    """

    def __init__(self):
        self._store: list[dict] = []
        self._load()

    def _load(self):
        if RAG_PATH.exists():
            try:
                self._store = json.loads(RAG_PATH.read_text(encoding="utf-8"))
            except Exception:
                self._store = []

    def _save(self):
        RAG_PATH.parent.mkdir(parents=True, exist_ok=True)
        RAG_PATH.write_text(
            json.dumps(self._store, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def add(self, task: str, result: str, agent: str = "nisha",
            evidence: str = "", correction: str = "", outcome: str = "") -> None:
        """Add an episodic memory entry."""
        entry = {
            "task":       task,
            "result":     result,
            "agent":      agent,
            "evidence":   evidence,
            "correction": correction,
            "outcome":    outcome,
            "timestamp":  datetime.datetime.now().isoformat(),
        }
        self._store.append(entry)
        # Keep last 500 entries max
        if len(self._store) > 500:
            self._store = self._store[-500:]
        self._save()

    def retrieve(self, query: str, top_k: int = 5, threshold: float = 0.1) -> list[dict]:
        """Retrieve the top_k most relevant memories for a query."""
        if not self._store:
            return []

        query_tokens = _tokenize(query)

        # Build vocab from store + query
        all_text = [_tokenize(e["task"] + " " + e["result"]) for e in self._store]
        vocab = set(query_tokens)
        for tokens in all_text:
            vocab.update(tokens)

        query_vec = _tfidf_vector(query_tokens, vocab)
        scored = []
        for i, (entry, tokens) in enumerate(zip(self._store, all_text)):
            entry_vec = _tfidf_vector(tokens, vocab)
            score = _cosine(query_vec, entry_vec, vocab)
            if score >= threshold:
                scored.append((score, i, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [e for _, _, e in scored[:top_k]]

    def format_for_prompt(self, query: str, top_k: int = 3) -> str:
        """Format retrieved memories for injection into system prompt."""
        memories = self.retrieve(query, top_k=top_k)
        if not memories:
            return ""
        lines = ["[RELEVANT PAST CONTEXT]"]
        for m in memories:
            ts = m.get("timestamp", "")[:10]
            lines.append(f"  [{ts}] Task: {m['task'][:80]}")
            if m.get("result"):
                lines.append(f"          Result: {m['result'][:80]}")
            if m.get("outcome"):
                lines.append(f"          Outcome: {m['outcome'][:60]}")
        return "\n".join(lines)

    def search(self, query: str) -> list[dict]:
        return self.retrieve(query, top_k=10)

    def clear(self) -> None:
        self._store = []
        self._save()


# Module-level singleton
_rag: Optional[RAGMemory] = None

def get_rag() -> RAGMemory:
    global _rag
    if _rag is None:
        _rag = RAGMemory()
    return _rag
