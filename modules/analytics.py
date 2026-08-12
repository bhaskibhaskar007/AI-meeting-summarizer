"""Analytics values and meaningful Plotly figures."""
import plotly.graph_objects as go
from utils.text_utils import word_count


def calculate_analytics(transcript: str, summary: str, insights: dict, duration: float | None) -> dict:
    transcript_words, summary_words = word_count(transcript), word_count(summary)
    return {"duration": duration, "transcript_words": transcript_words, "summary_words": summary_words,
            "reduction": round((1 - summary_words / max(transcript_words, 1)) * 100, 1),
            "key_points": len(insights["key_points"]) if "Not mentioned" not in insights["key_points"] else 0,
            "actions": len(insights["action_items"]),
            "decisions": len(insights["decisions"]) if "Not mentioned" not in insights["decisions"] else 0,
            "topics": len(insights["topics"]) if "Not mentioned" not in insights["topics"] else 0}


def word_count_figure(values: dict):
    fig = go.Figure(go.Bar(x=["Transcript", "Summary"], y=[values["transcript_words"], values["summary_words"]], marker_color=["#7185ff", "#9b6dff"]))
    fig.update_layout(template="plotly_dark", title="Transcript compression", height=280, margin=dict(l=20,r=20,t=45,b=20))
    return fig
