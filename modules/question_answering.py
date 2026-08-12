"""Grounded extractive question answering."""
from utils.text_utils import relevant_sentences


def answer_question(question: str, transcript: str, insights: dict) -> str:
    q = question.lower()
    if "decision" in q: candidates = insights["decisions"]
    elif "action" in q or "task" in q: candidates = [x["Task"] for x in insights["action_items"]]
    elif "risk" in q or "problem" in q or "concern" in q: candidates = insights["risks"]
    elif "next" in q: candidates = insights["next_steps"]
    else: candidates = relevant_sentences(transcript, question)
    candidates = [x for x in candidates if "Not mentioned" not in x]
    return "\n\n".join(candidates[:5]) if candidates else "I couldn't find that information in the meeting."
