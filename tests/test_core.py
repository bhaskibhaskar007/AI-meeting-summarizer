from modules.meeting_analysis import extract_meeting_insights
from modules.report_generator import generate_report
from utils.audio_utils import validate_upload
from utils.text_utils import chunk_text
import pytest

def test_audio_validation():
    validate_upload("meeting.mp3", 100, 1)
    with pytest.raises(ValueError): validate_upload("meeting.exe", 100, 1)

def test_chunking_preserves_words():
    text = " ".join(["This is a sentence."] * 100)
    assert " ".join(chunk_text(text, 50)).split() == text.split()

def test_extraction_is_transcript_based():
    output = extract_meeting_insights("Alex will send the budget by Friday. We decided to approve the plan.")
    assert output["action_items"] and "approve" in output["decisions"][0].lower()

def test_pdf_generation():
    data = generate_report("test.wav", "Hello meeting.", "Brief summary.", extract_meeting_insights("Hello meeting."), {})
    assert data.startswith(b"%PDF")
