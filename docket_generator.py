import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_docket_pdf(applicant_name, scheme_data, partner_data, emi_data, reference_id="MoSJE-GUIDE-2026", output_path="docket.pdf"):
    """
    Generates a clean, 1-page Scheme Information Sheet & Bank Desk Guide.
    Strictly for public informational reference and physical bank desk guidance.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=26,
        bottomMargin=26
    )

    styles = getSampleStyleSheet()

    # Brand Colors matching Web UI
    c_navy = colors.HexColor("#0F172A")       # Primary Header
    c_blue = colors.HexColor("#1E40AF")       # Section Header
    c_border = colors.HexColor("#CBD5E1")     # Border Line
    c_light = colors.HexColor("#F8FAFC")      # Card Background
    c_green = colors.HexColor("#15803D")      # Accent Green
    c_green_bg = colors.HexColor("#F0FDF4")   # Highlight Box

    # Clean Typography
    t_title = ParagraphStyle('Title', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=14, textColor=colors.white, alignment=1)
    t_sub = ParagraphStyle('Sub', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=colors.HexColor("#E2E8F0"), alignment=1)
    t_ref = ParagraphStyle('Ref', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor("#93C5FD"), alignment=1)
    
    sec_title = ParagraphStyle('SecTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=10.5, textColor=c_blue)
    lbl = ParagraphStyle('Lbl', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.6, leading=9.5, textColor=colors.HexColor("#475569"))
    val = ParagraphStyle('Val', parent=styles['Normal'], fontName='Helvetica', fontSize=7.6, leading=9.5, textColor=c_navy)

    story = []

    # 1. Official Header Box (Informational Reference)
    banner_rows = [
        [Paragraph("SCHEMESATHI &bull; STATUTORY SCHEME INFORMATION SHEET", t_title)],
        [Paragraph("Public Credit Guidance &amp; MoSJE Statutory Norms Reference Guide", t_sub)],
        [Paragraph("FOR BENEFICIARY REFERENCE &amp; BANK DESK ORIENTATION ONLY", t_ref)]
    ]
    t_banner = Table(banner_rows, colWidths=[540])
    t_banner.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_navy),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_banner)
    story.append(Spacer(1, 8))

    # 2. Block 1: Scheme Overview & Policy Parameters
    story.append(Paragraph("1. SCHEME OVERVIEW &amp; ELIGIBILITY PARAMETERS", sec_title))
    story.append(Spacer(1, 2))

    p_cost = scheme_data.get('project_cost', 85000)
    b1_data = [
        [
            Paragraph("Scheme Name:", lbl),
            Paragraph(f"<b>{scheme_data.get('scheme_name', 'N/A')}</b>", val),
            Paragraph("Corporation / Nodal Agency:", lbl),
            Paragraph(f"{scheme_data.get('scheme_id', 'MoSJE / NSFDC')}", val)
        ],
        [
            Paragraph("Target Beneficiaries:", lbl),
            Paragraph("SC / OBC / EWS / Safai Karamchari", val),
            Paragraph("Statutory Income Norm:", lbl),
            Paragraph("Annual Family Income &le; Rs 5,00,000", val)
        ],
        [
            Paragraph("Concessional Rate:", lbl),
            Paragraph(f"<b>{scheme_data.get('interest_rate', 4.0)}% per annum</b>", val),
            Paragraph("Project Budget Range:", lbl),
            Paragraph(f"Up to Rs {int(p_cost):,} (Benchmarked)", val)
        ]
    ]
    t_b1 = Table(b1_data, colWidths=[110, 180, 120, 130])
    t_b1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light),
        ('BOX', (0,0), (-1,-1), 0.75, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_b1)
    story.append(Spacer(1, 8))

    # 3. Block 2: Key Financial Benefits & Concessional Rules
    story.append(Paragraph("2. STATUTORY CONCESSIONAL CREDIT NORMS", sec_title))
    story.append(Spacer(1, 2))

    b2_data = [
        [
            Paragraph("Government Loan Share:", lbl),
            Paragraph("Up to 90% &ndash; 95% of Project Cost", val),
            Paragraph("Promoter Margin Contribution:", lbl),
            Paragraph("5% to 10% Only", val)
        ],
        [
            Paragraph("Business Grace Window:", lbl),
            Paragraph(f"<b>{emi_data.get('moratorium_grace_months', 3)} Months Moratorium</b> (0 EMI)", val),
            Paragraph("Collateral / Security:", lbl),
            Paragraph("<b>No Third-Party Collateral Mandate</b> (&le; 5.0L)", val)
        ]
    ]
    t_b2 = Table(b2_data, colWidths=[120, 170, 130, 120])
    t_b2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light),
        ('BOX', (0,0), (-1,-1), 0.75, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_b2)
    story.append(Spacer(1, 3))

    # General Financial Advantage Note
    savings_amt = emi_data.get('family_total_savings', 11219)
    save_html = (
        f"<b>Statutory Benefit Note:</b> Concessional interest under this scheme ({scheme_data.get('interest_rate', 4.0)}%) "
        f"saves approximately <b>Rs {int(savings_amt):,} in interest</b> compared to standard commercial credit (14% p.a.)."
    )
    t_save = Table([[Paragraph(f'<font color="{c_green}">{save_html}</font>', val)]], colWidths=[540])
    t_save.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_green_bg),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor("#BBF7D0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(t_save)
    story.append(Spacer(1, 8))

    # 4. Block 3: Authorized Channeling Institutions
    story.append(Paragraph("3. WHERE TO APPLY &bull; CHANNEL AGENCIES &amp; HEALTHY BANK DESKS", sec_title))
    story.append(Spacer(1, 2))

    b3_data = [
        [
            Paragraph("Channel Agency / Desk:", lbl),
            Paragraph(f"<b>{partner_data.get('name', 'State Channelising Agency (SCA)')}</b>", val)
        ],
        [
            Paragraph("Designated Office Address:", lbl),
            Paragraph(partner_data.get('address', 'District Office / Designated Nodal Branch'), val)
        ],
        [
            Paragraph("Prudential Safety Check:", lbl),
            Paragraph(f"Branch Net NPA: <b>{partner_data.get('net_npa_pct', 2.1)}%</b> (Eligible lending threshold &lt; 8.0%) &bull; Nodal Officer: {partner_data.get('nodal_officer', 'Welfare Officer')}", val)
        ]
    ]
    t_b3 = Table(b3_data, colWidths=[130, 410])
    t_b3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 0.75, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_b3)
    story.append(Spacer(1, 8))

    # 5. Block 4: Standard Mandatory Physical Checklist
    story.append(Paragraph("4. MANDATORY APPLICATION DOCUMENTS REQUIRED AT BANK DESK", sec_title))
    story.append(Spacer(1, 2))

    raw_docs = scheme_data.get("required_documents", [
        "Identity Proof Document",
        "Target Social Category / Caste / EWS Certificate",
        "Family Income Certificate (<= Rs 5.00 Lakh)",
        "Trade Machinery / Equipment Quotation Invoice"
    ])

    doc_rows = []
    for raw_doc in raw_docs:
        raw_str = str(raw_doc)
        clean_text = raw_str.replace("[✓]", "").replace("[ ]", "").replace("(Attached)", "").replace("(Pending)", "").replace("- Attached", "").replace("- Pending", "").strip()

        doc_rows.append([
            Paragraph(f"• <b>{clean_text}</b>", val),
            Paragraph('<font color="#64748B">[ Keep Original &amp; 2 Self-Attested Photocopies ]</font>', ParagraphStyle('ST', parent=val, alignment=2))
        ])

    t_b4 = Table(doc_rows, colWidths=[360, 180])
    t_b4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light),
        ('BOX', (0,0), (-1,-1), 0.75, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_b4)
    story.append(Spacer(1, 6))

    # 6. Counter Inquiry Guidance Box
    counter_guide = (
        "<b>Beneficiary Bank Counter Help:</b> Take this printout to the designated channel branch and ask for the "
        f"official MoSJE application form for <b>{scheme_data.get('scheme_name', 'this scheme')}</b>. "
        "Inform the desk officer that your income meets the statutory guidelines (&le; 5 Lakh) and your required documents are ready."
    )
    t_guide = Table([[Paragraph(counter_guide, val)]], colWidths=[540])
    t_guide.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor("#BFDBFE")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_guide)
    story.append(Spacer(1, 10))

    # 7. Non-Sanction Legal Disclaimer Footer
    disclaimer_text = (
        "<b>Important Notice:</b> This document is generated for public informational and guidance purposes only. "
        "It does not constitute a loan sanction, loan guarantee, or financial approval. Actual loan evaluation, "
        "form filling, and credit disbursal are conducted exclusively by authorized banking institutions and State Channelising Agencies (SCAs)."
    )
    story.append(Paragraph(
        disclaimer_text,
        ParagraphStyle('Foot', parent=val, fontSize=6.5, leading=8.5, textColor=colors.HexColor("#64748B"), alignment=1)
    ))

    doc.build(story)
    return output_path