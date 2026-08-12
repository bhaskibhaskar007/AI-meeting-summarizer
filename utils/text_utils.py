"""Transcript-safe text processing."""
import re
from collections.abc import Iterable


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+[\w'-]*\b", text))


def sentence_split(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", text) if part.strip()]


def chunk_text(text: str, max_words: int) -> list[str]:
    """Split by sentence boundaries, preserving all transcript content."""
    if max_words < 50:
        raise ValueError("Chunk size must be at least 50 words.")
    chunks, current, current_words = [], [], 0
    for sentence in sentence_split(text):
        words = sentence.split()
        if current and current_words + len(words) > max_words:
            chunks.append(" ".join(current))
            current, current_words = [], 0
        # Split an unusually long sentence rather than silently dropping it.
        while len(words) > max_words:
            if current:
                chunks.append(" ".join(current)); current, current_words = [], 0
            chunks.append(" ".join(words[:max_words])); words = words[max_words:]
        if words:
            current.append(" ".join(words)); current_words += len(words)
    if current:
        chunks.append(" ".join(current))
    return chunks


def relevant_sentences(text: str, query: str, limit: int = 6) -> list[str]:
    terms = {term.lower() for term in re.findall(r"\w+", query) if len(term) > 2}
    scored = [(sum(term in sentence.lower() for term in terms), sentence)
              for sentence in sentence_split(text)]
    return [sentence for score, sentence in sorted(scored, reverse=True) if score][:limit]
