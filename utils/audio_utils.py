"""Audio validation and metadata utilities."""
from pathlib import Path
from typing import BinaryIO

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4"}


def validate_upload(name: str, size: int, max_size_mb: int) -> None:
    if not name or Path(name).suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError("Please upload an MP3, WAV, M4A, or MP4 recording.")
    if size <= 0:
        raise ValueError("The uploaded audio file is empty.")
    if size > max_size_mb * 1024 * 1024:
        raise ValueError(f"The file exceeds the {max_size_mb} MB upload limit.")


def audio_duration_seconds(path: str) -> float | None:
    """Read duration when pydub/FFmpeg can decode the recording."""
    try:
        from pydub import AudioSegment
        return len(AudioSegment.from_file(path)) / 1000
    except Exception:
        return None


def format_duration(seconds: float | None) -> str:
    if seconds is None:
        return "Not available"
    minutes, secs = divmod(round(seconds), 60)
    return f"{minutes // 60:02d}:{minutes % 60:02d}:{secs:02d}"
