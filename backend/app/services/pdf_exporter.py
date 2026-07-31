import io
import html
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def safe_text(val: Any) -> str:
    """Escapes special XML/HTML characters to prevent ReportLab markup parsing crashes."""
    if val is None:
        return "N/A"
    if isinstance(val, (list, set, tuple)):
        val = ", ".join(str(x) for x in val)
    s = str(val)
    return html.escape(s)


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
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a")
    )
    
    h2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )

    story = []

    # Header
    agent_name_esc = safe_text(scan_data.get('agent_name', 'Agent'))
    story.append(Paragraph("<b>Agent Compliance Card Generator</b> – Enterprise Certificate", title_style))
    story.append(Paragraph(f"Official Audit & Governance Certificate | Agent: <b>{agent_name_esc}</b>", body_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#3b82f6"), spaceAfter=15))

    # Executive Overview Metrics Table
    comp_score = scan_data.get("compliance_score", 85)
    risk_score = scan_data.get("risk_score", 20)
    risk_tier = safe_text(scan_data.get("risk_tier", "Low"))
    framework_esc = safe_text(scan_data.get("framework", "Custom Python"))

    overview_data = [
        [Paragraph("<b>Metric</b>", body_style), Paragraph("<b>Value</b>", body_style), Paragraph("<b>Status</b>", body_style)],
        [Paragraph("Compliance Score", body_style), Paragraph(f"{comp_score}%", body_style), Paragraph("PASSED" if comp_score >= 70 else "ACTION REQUIRED", body_style)],
        [Paragraph("Security Risk Score", body_style), Paragraph(f"{risk_score}/100", body_style), Paragraph(f"{risk_tier.upper()} RISK", body_style)],
        [Paragraph("Framework", body_style), Paragraph(framework_esc, body_style), Paragraph("AUDITED", body_style)],
        [Paragraph("EU AI Act Status", body_style), Paragraph("Minimal Risk" if risk_score < 50 else "High Risk Assessment", body_style), Paragraph("REVIEWED", body_style)]
    ]

    t = Table(overview_data, colWidths=[180, 180, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # Compliance Card Section
    story.append(Paragraph("AI Agent Compliance Card Specifications", h2_style))
    
    card_table_data = [
        [Paragraph("<b>Attribute</b>", body_style), Paragraph("<b>Specification</b>", body_style)],
        [Paragraph("Agent Purpose", body_style), Paragraph(safe_text(card_data.get("agent_purpose", "N/A")), body_style)],
        [Paragraph("LLM Engine", body_style), Paragraph(safe_text(card_data.get("llm_and_version", "N/A")), body_style)],
        [Paragraph("Decision Authority", body_style), Paragraph(safe_text(card_data.get("decision_authority", "N/A")), body_style)],
        [Paragraph("Human Oversight", body_style), Paragraph(safe_text(card_data.get("human_oversight", "N/A")), body_style)],
        [Paragraph("Data Sources", body_style), Paragraph(safe_text(scan_data.get("data_sources", ["None"])), body_style)],
        [Paragraph("Incident Contact", body_style), Paragraph(safe_text(card_data.get("incident_contact", "N/A")), body_style)]
    ]

    t2 = Table(card_table_data, colWidths=[150, 360])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t2)
    story.append(Spacer(1, 15))

    # Detected Tools Section
    story.append(Paragraph("Discovered Tools & Security Capabilities", h2_style))
    tools = scan_data.get("tools_detected", [])
    if tools:
        tool_rows = [[Paragraph("<b>Tool Name</b>", body_style), Paragraph("<b>Category</b>", body_style), Paragraph("<b>Risk Tier</b>", body_style)]]
        for tool in tools:
            t_name = safe_text(tool.get("name", "Tool") if isinstance(tool, dict) else str(tool))
            t_cat = safe_text(tool.get("category", "Custom") if isinstance(tool, dict) else "Custom")
            t_risk = safe_text(tool.get("risk", "Low") if isinstance(tool, dict) else "Low")
            tool_rows.append([
                Paragraph(t_name, body_style),
                Paragraph(t_cat, body_style),
                Paragraph(t_risk, body_style)
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
    story.append(Paragraph("<i>Report generated automatically by Agent Compliance Card Generator Platform.</i>", body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_diff_pdf(diff_data: Dict[str, Any]) -> bytes:
    """
    Generates a professional enterprise PDF Comparison & Regulatory Reassessment Report.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DiffTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a")
    )
    
    h2_style = ParagraphStyle(
        'DiffH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=10,
        spaceAfter=5
    )
    
    body_style = ParagraphStyle(
        'DiffBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155")
    )

    story = []

    # Header Title
    agent_name = safe_text(diff_data.get("agent_name", "AI Agent"))
    v1 = safe_text(diff_data.get("baseline_version", "V1"))
    v2 = safe_text(diff_data.get("target_version", "V2"))
    story.append(Paragraph(f"AI Agent Compliance Card Diff Report: <b>{agent_name}</b>", title_style))
    story.append(Paragraph(f"Comparative Version Analysis | Baseline <b>{v1}</b> vs Target <b>{v2}</b>", body_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2563eb"), spaceAfter=12))

    # Executive Summary Table
    summary_data = [
        [Paragraph("<b>Metric</b>", body_style), Paragraph("<b>Baseline (V1)</b>", body_style), Paragraph("<b>Target (V2)</b>", body_style), Paragraph("<b>Delta / Impact</b>", body_style)],
        [Paragraph("Compliance Score", body_style), Paragraph(f"{diff_data.get('compliance_score_baseline', 0)}%", body_style), Paragraph(f"{diff_data.get('compliance_score_target', 0)}%", body_style), Paragraph(f"{diff_data.get('compliance_score_delta', 0)}%", body_style)],
        [Paragraph("Security Risk Score", body_style), Paragraph(f"{diff_data.get('risk_score_baseline', 0)}/100", body_style), Paragraph(f"{diff_data.get('risk_score_target', 0)}/100", body_style), Paragraph(f"+{diff_data.get('risk_score_delta', 0)}", body_style)],
        [Paragraph("Risk Tier", body_style), Paragraph(safe_text(diff_data.get('risk_tier_baseline', 'Low')), body_style), Paragraph(safe_text(diff_data.get('risk_tier_target', 'High')), body_style), Paragraph(safe_text(diff_data.get('overall_status', 'Modified')).upper(), body_style)],
        [Paragraph("Fields Changed", body_style), Paragraph(str(diff_data.get('fields_changed_count', 0)), body_style), Paragraph(str(diff_data.get('critical_changes_count', 0)) + " Critical", body_style), Paragraph(f"{diff_data.get('frameworks_impacted_count', 0)} Frameworks", body_style)]
    ]

    t_summary = Table(summary_data, colWidths=[130, 120, 120, 150])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 10))

    # AI Executive Summary Box
    story.append(Paragraph("AI Executive Auditor Summary", h2_style))
    ai_text = safe_text(diff_data.get("ai_explanation", "No critical changes detected."))
    story.append(Paragraph(f"<i>\"{ai_text}\"</i>", body_style))
    story.append(Spacer(1, 10))

    # Enterprise Diff Table
    story.append(Paragraph("Field Comparison & Regulatory Reassessment Matrix", h2_style))
    diff_table = diff_data.get("diff_table", [])
    if diff_table:
        table_rows = [[
            Paragraph("<b>Field</b>", body_style),
            Paragraph("<b>Old Value</b>", body_style),
            Paragraph("<b>New Value</b>", body_style),
            Paragraph("<b>Status</b>", body_style),
            Paragraph("<b>Severity</b>", body_style),
            Paragraph("<b>Framework</b>", body_style)
        ]]
        for row in diff_table:
            table_rows.append([
                Paragraph(safe_text(row.get("field", "")), body_style),
                Paragraph(safe_text(row.get("old_value", "")), body_style),
                Paragraph(safe_text(row.get("new_value", "")), body_style),
                Paragraph(safe_text(row.get("status", "")), body_style),
                Paragraph(safe_text(row.get("severity", "")), body_style),
                Paragraph(safe_text(row.get("framework", "")), body_style)
            ])
        t_diff = Table(table_rows, colWidths=[100, 100, 100, 80, 60, 80])
        t_diff.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t_diff)

    story.append(Spacer(1, 15))
    story.append(Paragraph("<i>Generated automatically by Agent Compliance Card Generator Platform (PS-6.1 Card Diff Engine).</i>", body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
