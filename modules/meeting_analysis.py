"""Evidence-first meeting information extraction."""
import re
from utils.text_utils import sentence_split

NOT_MENTIONED = "Not mentioned in the meeting."


def _sentences_matching(sentences: list[str], patterns: tuple[str, ...]) -> list[str]:
    return [s for s in sentences if any(re.search(p, s, re.I) for p in patterns)]


def _bullets(items: list[str]) -> list[str]:
    return items[:8] or [NOT_MENTIONED]


def extract_meeting_insights(transcript: str) -> dict:
    sentences = sentence_split(transcript)
    decisions = _sentences_matching(sentences, (r"\b(decided|decision|agree[ds]?|approved|will go with)\b",))
    risks = _sentences_matching(sentences, (r"\b(risk|blocker|blocked|concern|issue|problem|delay)\b",))
    next_steps = _sentences_matching(sentences, (r"\b(next step|follow[- ]?up|move forward|then we)\b",))
    actions = _sentences_matching(sentences, (r"\b(I('| wi)ll|we('| wi)ll|need to|action item|assigned to|todo|task)\b",))
    topic_words = re.findall(r"\b[A-Za-z][A-Za-z-]{4,}\b", transcript.lower())
    stop = {"about", "their", "there", "which", "would", "should", "could", "meeting", "because", "people", "we'll", "they"}
    frequency: dict[str, int] = {}
    for word in topic_words:
        if word not in stop: frequency[word] = frequency.get(word, 0) + 1
    topics = [word.title() for word, count in sorted(frequency.items(), key=lambda x: x[1], reverse=True) if count > 1][:8]
    action_rows = []
    for sentence in actions[:12]:
        deadline = re.search(r"\b(by|before|on)\s+([^,.!;]+)", sentence, re.I)
        person = re.search(r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:will|needs to)", sentence)
        action_rows.append({"Task": sentence, "Person": person.group(1) if person else "Not specified",
                            "Deadline": deadline.group(2).strip() if deadline else "Not specified",
                            "Priority": "Not specified"})
    return {"key_points": _bullets(sentences[:6]), "decisions": _bullets(decisions),
            "action_items": action_rows, "topics": topics or [NOT_MENTIONED],
            "risks": _bullets(risks), "next_steps": _bullets(next_steps)}
