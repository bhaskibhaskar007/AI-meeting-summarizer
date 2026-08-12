"""PDF generation with flowables to prevent text overflow."""
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors


def generate_report(filename: str, transcript: str, summary: str, insights: dict, analytics: dict) -> bytes:
    out = BytesIO(); styles = getSampleStyleSheet(); story = []
    def heading(value): story.extend([Paragraph(value, styles["Heading2"]), Spacer(1, 8)])
    def section(title, values):
        heading(title)
        for value in values: story.append(Paragraph("• " + value, styles["BodyText"]))
        story.append(Spacer(1, 10))
    story += [Paragraph("MeetMind AI — Meeting Report", styles["Title"]), Spacer(1, 12), Paragraph(f"Recording: {filename}", styles["BodyText"]), Spacer(1, 12)]
    heading("Executive Summary"); story += [Paragraph(summary, styles["BodyText"]), Spacer(1, 10)]
    section("Key Points", insights["key_points"]); section("Decisions", insights["decisions"])
    heading("Action Items")
    rows = [["Task", "Person", "Deadline", "Priority"]] + [[a[k] for k in ["Task","Person","Deadline","Priority"]] for a in insights["action_items"]]
    if len(rows) == 1: rows.append(["Not mentioned in the meeting.", "", "", ""])
    table = Table(rows, colWidths=[2.7*inch, 1.15*inch, 1.15*inch, .9*inch], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#202a55")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.25,colors.grey),("VALIGN",(0,0),(-1,-1),"TOP"),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),6)])); story += [table, Spacer(1,12)]
    section("Important Topics", insights["topics"]); section("Risks / Concerns", insights["risks"]); section("Next Steps", insights["next_steps"])
    story += [PageBreak(), Paragraph("Full Transcript", styles["Heading1"]), Spacer(1,8)]
    for para in transcript.split("\n"): story.append(Paragraph(para or " ", styles["BodyText"]))
    def footer(canvas, doc): canvas.drawRightString(A4[0]-36, 24, f"Page {doc.page}")
    SimpleDocTemplate(out, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=42, bottomMargin=36).build(story, onFirstPage=footer, onLaterPages=footer)
    return out.getvalue()
