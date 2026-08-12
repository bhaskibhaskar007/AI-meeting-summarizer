# MeetMind AI

MeetMind AI is a local-first Streamlit meeting intelligence application. It transcribes uploaded recordings with Whisper, creates a hierarchical Transformer summary, extracts evidence-linked meeting details, and exports a PDF report.

## Features

- MP3, WAV, M4A, and MP4 upload validation, player, duration, and progress feedback
- Real local Whisper transcription; no transcript or AI-result fixtures
- Long-transcript map/reduce summarization using Hugging Face Transformers
- Transcript-grounded key points, decisions, action items, topics, risks, and next steps
- Search, session chat, CSV/TXT/PDF exports, Plotly analytics, and session history
- Dark, responsive Streamlit dashboard and modular Python architecture

## Architecture

`Audio → FFmpeg/pydub metadata → Whisper transcript → chunked Transformer summary → evidence extraction/analytics → UI and exports`.

The extractor only returns sentences from the transcript. Where evidence is absent it reports “Not mentioned in the meeting.” The chat is extractive and searches only the transcript/derived insights, so it cannot use outside knowledge.

## Installation (Windows)

Install Python 3.10 or 3.11, then install FFmpeg and place it on `PATH`:

```powershell
winget install Gyan.FFmpeg
cd meetmind-ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

For a CPU-friendly first run set `WHISPER_MODEL=tiny`; `base` is the default. Models download on first use.

```powershell
$env:WHISPER_MODEL="tiny"
streamlit run app.py
```

## Configuration

Use environment variables locally or Streamlit secrets/environment configuration in deployment. Never commit keys.

| Variable | Default | Purpose |
|---|---|---|
| `WHISPER_MODEL` | `base` | Whisper model: tiny/base/small |
| `SUMMARY_MODEL` | `sshleifer/distilbart-cnn-12-6` | Hugging Face summary model |
| `MAX_UPLOAD_MB` | `500` | File upload cap |
| `CHUNK_WORDS` | `750` | Map/reduce chunk size |
| `WHISPER_FP16` | `false` | Enable on supported CUDA hosts |

## Project structure

```text
meetmind-ai/
  app.py  config.py  requirements.txt  packages.txt
  modules/       # transcription, summary, extraction, QA, analytics, PDF
  utils/         # audio and text helpers
  tests/         # pytest smoke tests
  .streamlit/config.toml
```

## Testing

```powershell
pytest -q
```

## Deployment

### GitHub

Create a repository, commit this project (excluding files in `.gitignore`), then push. Do not upload recordings or secrets.

### Streamlit Community Cloud / Hugging Face Spaces

`packages.txt` requests FFmpeg and `requirements.txt` installs Python packages. Both can run the app, but free CPU instances may be slow or memory-constrained for Whisper plus Transformers. Start with `tiny` Whisper and a compact summary model; this is suitable only for short recordings and demonstrations, not a reliable production workload.

### Production architecture

Deploy Streamlit as the frontend, a FastAPI worker/API for upload orchestration, object storage for recordings/reports, a GPU-backed Whisper inference service, and a separate GPU/managed Transformers inference service. Send job IDs through a queue and use signed storage URLs; retain recordings only for the required period. This lets the full real-AI pipeline scale without exposing credentials in the UI.

## Limitations and future improvements

Speaker diarization, semantic-vector retrieval, asynchronous job queues, OAuth, persistent history, encrypted object storage, multilingual quality evaluation, and human review workflows are logical additions. Current action extraction intentionally avoids guessing assignees and dates.

## Viva / interview explanation

The app keeps expensive models in Streamlit resource caches. Whisper decodes the recording into text. The transcript is divided at sentence boundaries; every chunk is summarized, then those summaries are summarized again, avoiding a lossy prefix truncation. Pattern extraction retains original transcript sentences as evidence, and the report uses ReportLab flowables so text paginates safely. The UI has no secret values: configuration is injected at runtime.
