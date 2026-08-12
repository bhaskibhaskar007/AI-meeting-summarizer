"""Local Whisper transcription adapter."""
from typing import Any


def transcribe_audio(path: str, model: Any, use_fp16: bool = False) -> dict:
    result = model.transcribe(path, fp16=use_fp16, verbose=False)
    text = (result.get("text") or "").strip()
    if not text:
        raise RuntimeError("Speech recognition completed but produced an empty transcript.")
    segments = result.get("segments", [])
    return {"text": text, "segments": segments, "language": result.get("language", "unknown")}
