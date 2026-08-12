"""Central application configuration; values may be overridden with environment variables."""
from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    whisper_model: str = os.getenv("WHISPER_MODEL", "base")
    summary_model: str = os.getenv("SUMMARY_MODEL", "sshleifer/distilbart-cnn-12-6")
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "500"))
    chunk_words: int = int(os.getenv("CHUNK_WORDS", "750"))
    use_fp16: bool = os.getenv("WHISPER_FP16", "false").lower() == "true"


settings = Settings()
