import io
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_compliance_pdf(scan_data: Dict[str, Any], card_data: Dict[str, Any]) -> bytes:
    """
    Generates a professional enterprise PDF audit report for an AI Agent.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#0f172a")
    )
    
    h2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155")
    )

    story = []

    # Header
    story.append(Paragraph("<b>AgentGuard AI</b> – Enterprise Compliance Card", title_style))
    story.append(Paragraph(f"Official Audit & Governance Certificate | Agent: <b>{scan_data.get('agent_name', 'Agent')}</b>", body_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#3b82f6"), spaceAfter=15))

    # Executive Overview Metrics Table
    comp_score = scan_data.get("compliance_score", 85)
    risk_score = scan_data.get("risk_score", 20)
    risk_tier = scan_data.get("risk_tier", "Low")

    overview_data = [
        [Paragraph("<b>Metric</b>", body_style), Paragraph("<b>Value</b>", body_style), Paragraph("<b>Status</b>", body_style)],
        ["Compliance Score", f"{comp_score}%", "PASSED" if comp_score >= 70 else "ACTION REQUIRED"],
        ["Security Risk Score", f"{risk_score}/100", f"{risk_tier.upper()} RISK"],
        ["Framework", scan_data.get("framework", "Custom Python"), "AUDITED"],
        ["EU AI Act Status", "Minimal Risk" if risk_score < 50 else "High Risk Assessment", "REVIEWED"]
    ]

    t = Table(overview_data, colWidths=[180, 180, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # Compliance Card Section
    story.append(Paragraph("AI Agent Compliance Card Specifications", h2_style))
    
    card_table_data = [
        [Paragraph("<b>Attribute</b>", body_style), Paragraph("<b>Specification</b>", body_style)],
        [Paragraph("Agent Purpose", body_style), Paragraph(str(card_data.get("agent_purpose", "N/A")), body_style)],
        [Paragraph("LLM Engine", body_style), Paragraph(str(card_data.get("llm_and_version", "N/A")), body_style)],
        [Paragraph("Decision Authority", body_style), Paragraph(str(card_data.get("decision_authority", "N/A")), body_style)],
        [Paragraph("Human Oversight", body_style), Paragraph(str(card_data.get("human_oversight", "N/A")), body_style)],
        [Paragraph("Data Sources", body_style), Paragraph(", ".join(scan_data.get("data_sources", ["None"])), body_style)],
        [Paragraph("Incident Contact", body_style), Paragraph(str(card_data.get("incident_contact", "N/A")), body_style)]
    ]

    t2 = Table(card_table_data, colWidths=[150, 360])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t2)
    story.append(Spacer(1, 15))

    # Detected Tools Section
    story.append(Paragraph("Discovered Tools & Security Capabilities", h2_style))
    tools = scan_data.get("tools_detected", [])
    if tools:
        tool_rows = [[Paragraph("<b>Tool Name</b>", body_style), Paragraph("<b>Category</b>", body_style), Paragraph("<b>Risk Tier</b>", body_style)]]
        for tool in tools:
            tool_rows.append([
                Paragraph(tool.get("name", "Tool"), body_style),
                Paragraph(tool.get("category", "Custom"), body_style),
                Paragraph(tool.get("risk", "Low"), body_style)
            ])
        t3 = Table(tool_rows, colWidths=[180, 200, 130])
        t3.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(t3)
    else:
        story.append(Paragraph("No custom execution tools detected.", body_style))

    story.append(Spacer(1, 20))
    story.append(Paragraph("<i>Report generated automatically by AgentGuard AI Enterprise Governance Platform.</i>", body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
