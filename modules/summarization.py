"""Hierarchical Hugging Face summarization without transcript truncation."""
from typing import Any
from utils.text_utils import chunk_text


def _summarize(text: str, pipeline: Any, max_length: int = 160) -> str:
    words = len(text.split())
    if words < 35:
        return text
    result = pipeline(text, max_length=min(max_length, max(40, words // 2)),
                      min_length=min(35, max(10, words // 8)), do_sample=False,
                      truncation=True)
    return result[0]["summary_text"].strip()


def summarize_long_transcript(text: str, pipeline: Any, chunk_words: int) -> str:
    """Map-reduce summary preserving content beyond a model context window."""
    chunks = chunk_text(text, chunk_words)
    partials = [_summarize(chunk, pipeline) for chunk in chunks]
    combined = " ".join(partials)
    # Recurse only when the map output remains too large for the model.
    while len(combined.split()) > chunk_words:
        combined = " ".join(_summarize(c, pipeline) for c in chunk_text(combined, chunk_words))
    return _summarize(combined, pipeline, max_length=220)
