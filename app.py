"""MeetMind AI Streamlit application."""
import os
import tempfile
import time
from datetime import datetime
import pandas as pd
import streamlit as st
from config import settings
from modules.transcription import transcribe_audio
from modules.summarization import summarize_long_transcript
from modules.meeting_analysis import extract_meeting_insights
from modules.question_answering import answer_question
from modules.analytics import calculate_analytics, word_count_figure
from modules.report_generator import generate_report
from utils.audio_utils import validate_upload, audio_duration_seconds, format_duration
from utils.text_utils import word_count, relevant_sentences

st.set_page_config(page_title="MeetMind AI", page_icon="🎙️", layout="wide")
st.markdown("""<style>
 .stApp {background:#0b1020;color:#e8ecff}.block-container{padding-top:2rem;max-width:1300px}
 [data-testid='stMetric']{background:#151d38;border:1px solid #29355e;padding:14px;border-radius:14px}
 .hero{padding:28px;border-radius:20px;background:linear-gradient(110deg,#17234d,#28194d);margin-bottom:20px}
 .hero h1{margin:0;color:#fff}.muted{color:#b6c1e6}</style>""", unsafe_allow_html=True)

@st.cache_resource(show_spinner=False)
def load_whisper():
    try:
        import whisper
        return whisper.load_model(settings.whisper_model)
    except Exception as exc:
        raise RuntimeError("Could not load Whisper. Install requirements and FFmpeg, then try a smaller model.") from exc

@st.cache_resource(show_spinner=False)
def load_summarizer():
    try:
        from transformers import pipeline
        return pipeline("summarization", model=settings.summary_model)
    except Exception as exc:
        raise RuntimeError("Could not load the summarization model. Check model download/network access.") from exc

def init_state():
    for key, default in {"result":None, "history":[], "chat":[]}.items():
        if key not in st.session_state: st.session_state[key] = default

def process(upload):
    validate_upload(upload.name, upload.size, settings.max_upload_mb)
    suffix = os.path.splitext(upload.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
        temp.write(upload.getbuffer()); path = temp.name
    start = time.perf_counter()
    try:
        progress = st.progress(0, text="Preparing audio…")
        duration = audio_duration_seconds(path); progress.progress(20, text="Transcribing with Whisper…")
        transcript_data = transcribe_audio(path, load_whisper(), settings.use_fp16)
        progress.progress(55, text="Generating an evidence-based summary…")
        summary = summarize_long_transcript(transcript_data["text"], load_summarizer(), settings.chunk_words)
        progress.progress(75, text="Extracting meeting insights…")
        insights = extract_meeting_insights(transcript_data["text"])
        analytics = calculate_analytics(transcript_data["text"], summary, insights, duration)
        progress.progress(100, text="Analysis complete.")
        return {"filename":upload.name, "transcript":transcript_data["text"], "segments":transcript_data["segments"], "summary":summary, "insights":insights, "analytics":analytics, "elapsed":round(time.perf_counter()-start,1), "date":datetime.now().strftime("%Y-%m-%d %H:%M")}
    finally:
        try: os.unlink(path)
        except OSError: pass

init_state()
with st.sidebar:
    st.title("🎙️ MeetMind AI")
    st.caption("Intelligent Meeting Summarizer")
    page = st.radio("Navigation", ["🏠 Dashboard", "📄 Meeting Analysis", "💬 Ask Meeting", "📊 Analytics", "📚 Meeting History", "⚙️ Settings"])

if page == "⚙️ Settings":
    st.header("Settings")
    st.info("Configure models using environment variables: WHISPER_MODEL, SUMMARY_MODEL, MAX_UPLOAD_MB, and CHUNK_WORDS.")
    st.code(f"Whisper: {settings.whisper_model}\nSummary: {settings.summary_model}\nUpload limit: {settings.max_upload_mb} MB\nChunk size: {settings.chunk_words} words")
elif page == "📚 Meeting History":
    st.header("Session Meeting History")
    st.dataframe(pd.DataFrame(st.session_state.history) if st.session_state.history else pd.DataFrame(columns=["Filename","Date","Action items","Decisions","Summary"]), use_container_width=True)
else:
    if page == "🏠 Dashboard":
        st.markdown("<div class='hero'><h1>Turn Meetings into Action</h1><p class='muted'>Upload a recording to produce a transcript, grounded summary, decisions, action items, and report.</p></div>", unsafe_allow_html=True)
        upload = st.file_uploader("Upload a meeting recording", type=["mp3","wav","m4a","mp4"])
        if upload:
            st.audio(upload); st.caption(f"{upload.name} · {upload.size / 1024 / 1024:.1f} MB")
            if st.button("🚀 Analyze Meeting", type="primary"):
                try:
                    st.session_state.result = process(upload)
                    r = st.session_state.result
                    st.session_state.history.insert(0, {"Filename":r["filename"],"Date":r["date"],"Action items":r["analytics"]["actions"],"Decisions":r["analytics"]["decisions"],"Summary":r["summary"][:160]})
                    st.success("Meeting analyzed successfully.")
                except Exception as exc:
                    st.error("Something went wrong while processing your meeting.")
                    st.caption(str(exc))
    r = st.session_state.result
    if not r:
        if page != "🏠 Dashboard": st.info("Analyze a recording from Dashboard first.")
    elif page in ("🏠 Dashboard", "📄 Meeting Analysis"):
        st.header("Executive Summary"); st.write(r["summary"])
        tabs = st.tabs(["📄 Transcript", "📝 Meeting Insights", "📌 Action Items", "⬇️ Exports"])
        with tabs[0]:
            needle = st.text_input("🔎 Search Transcript")
            if needle:
                matches = relevant_sentences(r["transcript"], needle, 50); st.caption(f"{len(matches)} matching sections")
                for match in matches: st.markdown(match.replace(needle, f"**{needle}**"))
            else: st.text_area("Full transcript", r["transcript"], height=360)
            st.caption(f"{word_count(r['transcript'])} words · {format_duration(r['analytics']['duration'])} · {r['elapsed']}s processing")
        with tabs[1]:
            for label, key in [("Key Points","key_points"),("Decisions Made","decisions"),("Important Topics","topics"),("Risks / Concerns","risks"),("Next Steps","next_steps")]:
                st.subheader(label); st.markdown("\n".join(f"- {x}" for x in r["insights"][key]))
        with tabs[2]: st.dataframe(pd.DataFrame(r["insights"]["action_items"], columns=["Task","Person","Deadline","Priority"]), use_container_width=True)
        with tabs[3]:
            pdf = generate_report(r["filename"], r["transcript"], r["summary"], r["insights"], r["analytics"])
            st.download_button("📥 Download Meeting Report (PDF)", pdf, "meeting-report.pdf", "application/pdf")
            st.download_button("Download transcript (TXT)", r["transcript"], "transcript.txt")
            st.download_button("Download summary (TXT)", r["summary"], "summary.txt")
            st.download_button("Download action items (CSV)", pd.DataFrame(r["insights"]["action_items"]).to_csv(index=False), "action-items.csv", "text/csv")
    elif page == "📊 Analytics":
        a = r["analytics"]; cols = st.columns(4)
        for col, label, value in zip(cols, ["Duration","Total words","Summary words","Reduction"], [format_duration(a["duration"]),a["transcript_words"],a["summary_words"],f"{a['reduction']}%"]): col.metric(label, value)
        cols = st.columns(4)
        for col, label, value in zip(cols, ["Key points","Action items","Decisions","Topics"], [a["key_points"],a["actions"],a["decisions"],a["topics"]]): col.metric(label, value)
        st.plotly_chart(word_count_figure(a), use_container_width=True)
    elif page == "💬 Ask Meeting":
        st.header("💬 Ask Your Meeting")
        for message in st.session_state.chat: st.chat_message(message["role"]).write(message["content"])
        if prompt := st.chat_input("Ask a question grounded in this meeting…"):
            st.session_state.chat += [{"role":"user","content":prompt}]
            reply = answer_question(prompt, r["transcript"], r["insights"])
            st.session_state.chat += [{"role":"assistant","content":reply}]
            st.rerun()
