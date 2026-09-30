import io
import json
import math
import os
from flask import Flask, Response, jsonify, redirect, render_template, request, session, url_for, send_file

# Optional ReportLab import with fallback
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

# Safe import for external docket_generator if present
try:
    import docket_generator
    HAS_DOCKET = True
except ImportError:
    HAS_DOCKET = False

app = Flask(__name__)
app.secret_key = "schemesathi_secret_key"

BASE_DIR = os.path.dirname(__file__)

# Standard JSON dataset paths with fallback
SCHEMES_FILE_PATH = os.path.join(BASE_DIR, "schemes.json")
PARTNERS_FILE_PATH = os.path.join(BASE_DIR, "channel_partners.json")


def load_schemes_from_json():
    """Reads official MoSJE/NSFDC statutory schemes from JSON dataset."""
    target_path = SCHEMES_FILE_PATH
    if not os.path.exists(target_path):
        target_path = os.path.join(BASE_DIR, "data", "schemes.json")
    if not os.path.exists(target_path):
        target_path = os.path.join(BASE_DIR, "schemes_2.json")

    if not os.path.exists(target_path):
        return []

    with open(target_path, mode="r", encoding="utf-8") as f:
        try:
            raw_schemes = json.load(f)
        except json.JSONDecodeError:
            return []

    standardized = []
    for idx, row in enumerate(raw_schemes, start=1):
        if not row or not row.get("scheme_name"):
            continue

        scheme_item = {
            "id": idx,
            "scheme_id": row.get("scheme_id", f"SCHEME-{idx}"),
            "name": row.get("scheme_name", "Unnamed Scheme").strip(),
            "ministry": row.get("official_corporation", "Ministry of Social Justice and Empowerment").strip(),
            "category": [row.get("target_category", "SC").lower()],
            "gender": row.get("target_gender", "ALL"),
            "min_age": 18,
            "max_age": 70,
            "state": "All",
            "max_income": float(row.get("max_family_income", 500000)),
            "income_ceiling": float(row.get("max_family_income", 500000)),
            "business_stage": ["Starting", "Scaling"],
            "sector": row.get("purpose_keywords", []),
            "area": "All",
            "benefit_type": "Concessional Loan",
            "benefits": row.get("description", "Concessional credit assistance under MoSJE guidelines."),
            "min_project_cost": float(row.get("min_project_cost", 10000)),
            "max_project_cost": float(row.get("max_project_cost", 5000000)),
            "govt_share_pct": float(row.get("loan_coverage_pct", 90.0)),
            "promoter_share_pct": float(row.get("promoter_margin_pct", 10.0)),
            "interest_rate": float(row.get("interest_rate_pct", 6.5)),
            "moratorium_months": int(row.get("moratorium_months", 3)),
            "max_tenure_months": int(row.get("tenure_months", 36)),
            "documents": row.get("required_documents", []),
            "application_process": "Apply via State Channelising Agency (SCA) or designated healthy bank branch.",
            "official_url": "https://nsfdc.nic.in",
        }
        standardized.append(scheme_item)

    return standardized


def load_channel_partners():
    """Reads 75 official Channel Partners and their Net NPA metrics from JSON."""
    target_path = PARTNERS_FILE_PATH
    if not os.path.exists(target_path):
        target_path = os.path.join(BASE_DIR, "data", "channel_partners.json")
    if not os.path.exists(target_path):
        target_path = os.path.join(BASE_DIR, "channel_partners_2.json")

    if not os.path.exists(target_path):
        return []

    with open(target_path, mode="r", encoding="utf-8") as f:
        try:
            raw_partners = json.load(f)
        except json.JSONDecodeError:
            return []

    standardized = []
    for p in raw_partners:
        net_npa = float(p.get("net_npa_pct", 4.0))
        quota = bool(p.get("quota_active", True))
        is_active = quota and (net_npa < 8.0)

        item = {
            "id": p.get("id"),
            "name": p.get("name"),
            "type": p.get("type", "SCA"),
            "district": p.get("district", "Almora"),
            "state": p.get("state", "Uttarakhand"),
            "address": p.get("address", "N/A"),
            "lat": float(p.get("lat", 29.597)),
            "lng": float(p.get("lng", 79.659)),
            "net_npa_pct": net_npa,
            "quota_active": quota,
            "fund_status": "Active" if is_active else "Blocked",
            "npa_level": f"{net_npa}%",
            "contact": p.get("contact", "N/A"),
            "nodal_officer": p.get("nodal_officer", "Branch In-charge"),
            "status_note": "MoSJE approved active branch." if is_active else "Application suspended due to high Net NPA (>= 8%) or quota freeze.",
        }
        standardized.append(item)

    return standardized


def calculate_match(user_profile, scheme):
    """
    Evaluates profile compatibility against statutory rules:
    Supports SC, Safai Karamchari, OBC, ST, and EWS General Category (Income <= 5L).
    Returns: score, checks, explanation, is_fully_eligible
    """
    checks = {}
    reasons = []

    if not user_profile:
        return 0, {"Profile": False}, "General recommendation.", False

    # 1. Statutory Category & EWS Match
    raw_user_cat = str(user_profile.get("category", "General")).strip().lower()
    scheme_categories = [str(c).strip().lower() for c in scheme.get("category", [])]

    is_scheme_for_sc = any("sc" in c for c in scheme_categories)
    is_scheme_for_safai = any("safai" in c for c in scheme_categories)
    is_scheme_for_general = any("general" in c or "ews" in c for c in scheme_categories)
    is_scheme_for_all = any(c in ["all", "any"] for c in scheme_categories)

    try:
        user_income = float(user_profile.get("income", user_profile.get("annual_income", 250000)))
    except (ValueError, TypeError):
        user_income = 250000.0

    category_passed = False

    if is_scheme_for_all:
        category_passed = True
        reasons.append("Open social category eligibility under inclusive MoSJE norms.")
    elif raw_user_cat == "sc" and is_scheme_for_sc:
        category_passed = True
        reasons.append("Eligible under targeted SC welfare quota.")
    elif raw_user_cat in ["safai", "safai_karamchari"] and is_scheme_for_safai:
        category_passed = True
        reasons.append("Eligible under Safai Karamchari rehabilitation quota.")
    elif raw_user_cat == "general":
        if is_scheme_for_general:
            if user_income <= 500000:
                category_passed = True
                reasons.append("Eligible under Economically Weaker Section (EWS - General Category) quota.")
            else:
                reasons.append("EWS quota requires family income <= ₹5,00,000.")
        else:
            reasons.append("Scheme reserved for targeted social groups.")
    elif raw_user_cat in scheme_categories:
        category_passed = True
        reasons.append(f"Eligible under {raw_user_cat.upper()} social quota.")
    else:
        reasons.append("Social category criteria not met.")

    checks["Social Category / EWS Norm"] = category_passed

    # 2. Statutory Income Ceiling (<= 5L)
    scheme_income_cap = float(scheme.get("income_ceiling", scheme.get("max_income", 500000)))
    income_passed = (user_income <= scheme_income_cap)
    checks["Income Cap (<= 5L)"] = income_passed
    if income_passed:
        reasons.append(f"Income satisfies statutory ₹{int(scheme_income_cap):,} cap.")
    else:
        reasons.append("Annual income exceeds the statutory ceiling.")

    # 3. Project Cost & Scale Alignment
    try:
        user_cost = float(user_profile.get("project_cost", 85000))
    except (ValueError, TypeError):
        user_cost = 85000.0

    scheme_min_cost = float(scheme.get("min_project_cost", 10000))
    scheme_max_cost = float(scheme.get("max_project_cost", 5000000))
    cost_passed = (scheme_min_cost <= user_cost <= scheme_max_cost)
    checks["Project Cost Scale"] = cost_passed
    if cost_passed:
        reasons.append(f"Project cost ₹{int(user_cost):,} fits allowed range.")
    else:
        reasons.append("Project budget is outside scheme limits.")

    # 4. Gender Filter Check
    user_gender = str(user_profile.get("gender", "ALL")).upper().strip()
    scheme_gender = str(scheme.get("gender", "ALL")).upper().strip()
    gender_passed = True
    if scheme_gender == "FEMALE" and user_gender != "FEMALE":
        gender_passed = False
        reasons.append("Exclusive to women entrepreneurs.")
    checks["Gender Match"] = gender_passed

    is_fully_eligible = category_passed and income_passed and cost_passed and gender_passed
    if not is_fully_eligible:
        return 0, checks, "Mandatory MoSJE criteria not satisfied.", False

    # Dynamic Compatibility Scoring
    score = 82
    if category_passed: score += 4
    if income_passed: score += 4
    if cost_passed: score += 4
    if scheme_gender == "FEMALE" and user_gender == "FEMALE": score += 3
    if user_profile.get("disability") == "Yes": score += 2

    final_score = min(98, score)
    explanation = " ".join(reasons) if reasons else "Eligible under concessional financing criteria."

    return final_score, checks, explanation, True


# ===================== ROUTES =====================

@app.route("/")
def home():
    index_path = os.path.join(BASE_DIR, "templates", "index.html")
    if os.path.exists(index_path):
        return render_template("index.html")
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        session["profile"] = {
            "age": int(request.form.get("age", 24)),
            "gender": request.form.get("gender", "Female"),
            "state": request.form.get("state", "Uttarakhand"),
            "district": request.form.get("district", "Almora"),
            "category": request.form.get("category", "SC").strip(),
            "income": float(request.form.get("income", 180000)),
            "intent": request.form.get("intent", "micro"),
            "project_cost": float(request.form.get("project_cost", 85000)),
            "purpose": request.form.get("purpose", "silai boutique and tailoring unit"),
            "business_status": request.form.get("business_status", "New"),
            "sector": request.form.get("sector", "Micro"),
            "business_stage": request.form.get("business_stage", "Starting"),
            "area": request.form.get("area", "Rural"),
            "disability": request.form.get("disability", "No"),
        }
        return redirect(url_for("recommendations"))

    pre_cat = request.args.get("pre_cat", "sc")
    pre_gender = request.args.get("pre_gender", "female")
    pre_cost = request.args.get("pre_cost", "85000")

    return render_template(
        "profile.html",
        user=session.get("profile", {}),
        pre_cat=pre_cat,
        pre_gender=pre_gender,
        pre_cost=pre_cost,
    )


@app.route("/recommendations")
def recommendations():
    user_profile = session.get("profile")

    if not user_profile:
        return redirect(url_for("profile"))

    schemes_pool = load_schemes_from_json()
    ranked_schemes = []

    for item in schemes_pool:
        score, checks, explanation, is_eligible = calculate_match(user_profile, item)

        if is_eligible:
            scheme_copy = item.copy()
            scheme_copy["score"] = score
            scheme_copy["checks"] = checks
            scheme_copy["explanation"] = explanation
            ranked_schemes.append(scheme_copy)

    ranked_schemes.sort(key=lambda x: (x["interest_rate"], -x["score"]))

    top_match = ranked_schemes[0] if len(ranked_schemes) > 0 else None
    other_matches = ranked_schemes[1:] if len(ranked_schemes) > 1 else []

    return render_template(
        "recommendations.html",
        profile=user_profile,
        top_match=top_match,
        other_matches=other_matches,
        all_ranked=ranked_schemes,
    )


@app.route("/calculator")
def calculator():
    scheme_id = request.args.get("scheme_id", type=int)
    schemes_pool = load_schemes_from_json()
    selected_scheme = None

    if scheme_id:
        selected_scheme = next((s for s in schemes_pool if s["id"] == scheme_id), None)
    if not selected_scheme and schemes_pool:
        selected_scheme = schemes_pool[0]

    user_profile = session.get("profile", {})
    return render_template(
        "calculator.html",
        scheme=selected_scheme,
        schemes=schemes_pool,
        user=user_profile,
    )


@app.route("/locator")
def locator():
    partners = load_channel_partners()
    user_profile = session.get("profile", {})
    raw_district = user_profile.get("district", "ALL")

    clean_district = raw_district.split("(")[0].strip() if raw_district else "ALL"
    district_filter = request.args.get("district", clean_district)

    if district_filter and district_filter != "ALL":
        filtered = [
            p for p in partners 
            if district_filter.lower() in p.get("district", "").lower() or 
               p.get("district", "").lower() in district_filter.lower()
        ]
        if filtered:
            partners = filtered

    return render_template(
        "locator.html",
        partners=partners,
        active_district=district_filter,
    )


@app.route("/api/download-docket", methods=["POST"])
def download_docket():
    # Priority 1: Use external docket_generator if available
    if HAS_DOCKET:
        try:
            data = request.get_json() or {}
            applicant_name = data.get("applicant_name", "Artisan Beneficiary (SC Category)")
            scheme_data = data.get("scheme_data", {})
            partner_data = data.get("partner_data", {})
            emi_data = data.get("emi_data", {})
            reference_id = data.get("reference_id", "MoSJE-2026-7782")

            pdf_path = os.path.join(BASE_DIR, "MoSJE_PreScreening_Docket.pdf")
            docket_generator.generate_docket_pdf(
                applicant_name=applicant_name,
                scheme_data=scheme_data,
                partner_data=partner_data,
                emi_data=emi_data,
                reference_id=reference_id,
                output_path=pdf_path
            )
            return send_file(pdf_path, as_attachment=True, download_name=f"MoSJE_PreScreening_Docket_{reference_id}.pdf")
        except Exception:
            pass  # Fallback to direct ReportLab logic

    # Priority 2: In-memory ReportLab Generator
    if HAS_REPORTLAB:
        try:
            data = request.get_json() or {}
            applicant_name = data.get("applicant_name", "Artisan Beneficiary (SC Category)")
            scheme = data.get("scheme_data", {})
            partner = data.get("partner_data", {})
            emi = data.get("emi_data", {})

            pdf_buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                pdf_buffer, 
                pagesize=letter, 
                rightMargin=36, 
                leftMargin=36, 
                topMargin=36, 
                bottomMargin=36
            )
            
            styles = getSampleStyleSheet()
            header_style = ParagraphStyle(
                'HeaderStyle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=14,
                leading=18,
                textColor=colors.HexColor('#0F172A'),
                alignment=1
            )
            sub_style = ParagraphStyle(
                'SubStyle',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=9,
                leading=12,
                textColor=colors.HexColor('#64748B'),
                alignment=1
            )
            section_title = ParagraphStyle(
                'SectionTitle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=10.5,
                leading=14,
                textColor=colors.HexColor('#1E3A8A')
            )
            body_style = ParagraphStyle(
                'Body',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=8.5,
                leading=11.5,
                textColor=colors.HexColor('#334155')
            )

            story = []
            story.append(Paragraph("MINISTRY OF SOCIAL JUSTICE &amp; EMPOWERMENT", header_style))
            story.append(Paragraph("STATUTORY CREDIT PRE-SCREENING DOSSIER (SIH26092)", sub_style))
            story.append(Spacer(1, 14))

            # Table 1: Summary
            summary_data = [
                [Paragraph("<b>Beneficiary Profile</b>", body_style), Paragraph(str(applicant_name), body_style)],
                [Paragraph("<b>Matched Scheme</b>", body_style), Paragraph(f"<b>{scheme.get('scheme_name', 'Mahila Samriddhi Yojana (MSY)')}</b>", body_style)],
                [Paragraph("<b>Statutory Concessional Rate</b>", body_style), Paragraph(f"{scheme.get('interest_rate', '4.0')}% per annum", body_style)],
                [Paragraph("<b>Validated Project Budget</b>", body_style), Paragraph(f"INR {int(scheme.get('project_cost', 85000)):,}", body_style)],
                [Paragraph("<b>Grace Moratorium Window</b>", body_style), Paragraph(f"{emi.get('moratorium_grace_months', 3)} Months (Zero EMI Period)", body_style)],
                [Paragraph("<b>Estimated Monthly EMI</b>", body_style), Paragraph(f"INR {int(emi.get('monthly_emi', 2218)):,} / month", body_style)]
            ]
            t1 = Table(summary_data, colWidths=[200, 340])
            t1.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(t1)
            story.append(Spacer(1, 12))

            # Table 2: Channel Bank
            story.append(Paragraph("DESIGNATED CHANNEL LENDING DESK (SAFE NPA &lt; 8.0%)", section_title))
            story.append(Spacer(1, 4))
            bank_data = [
                [Paragraph("<b>Approved Bank / Channel Desk</b>", body_style), Paragraph(partner.get('name', 'Uttarakhand Bahujan Kalyan Nigam (SCA)'), body_style)],
                [Paragraph("<b>Branch Office Address</b>", body_style), Paragraph(partner.get('address', 'Mall Road, Almora, Uttarakhand'), body_style)],
                [Paragraph("<b>Desk Officer &amp; Helpline</b>", body_style), Paragraph(f"{partner.get('nodal_officer', 'Welfare Officer')} (Tel: {partner.get('contact', '05962-230111')})", body_style)],
                [Paragraph("<b>Audited Net NPA Ratio</b>", body_style), Paragraph(f"{partner.get('net_npa_pct', 2.1)}% (Statutorily Eligible for Loan Disbursal)", body_style)]
            ]
            t2 = Table(bank_data, colWidths=[200, 340])
            t2.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFFFF')),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(t2)
            story.append(Spacer(1, 12))

            # Table 3: Clean Documentation Status Table
            story.append(Paragraph("MANDATORY DOCUMENTATION STATUS", section_title))
            story.append(Spacer(1, 4))
            
            raw_docs = scheme.get('required_documents', [
                "Identity Card",
                "Target Social Category Caste / Community Certificate",
                "Family Income Certificate (<= INR 5,00,000 p.a.)",
                "Trade Machinery / Raw Material Quotation Estimate"
            ])
            
            doc_rows = []
            for d in raw_docs:
                clean_name = str(d).replace("[✓]", "").replace("[ ]", "").replace("(Attached)", "").replace("(Pending)", "").strip()
                is_attached = "(Attached)" in str(d) or "[✓]" in str(d)
                
                status_color = "#15803D" if is_attached else "#94A3B8"
                status_text = "<b>ATTACHED</b>" if is_attached else "PENDING"
                
                row = [
                    Paragraph(f"• {clean_name}", body_style),
                    Paragraph(f'<font color="{status_color}">{status_text}</font>', ParagraphStyle('DocStatus', parent=body_style, alignment=2))
                ]
                doc_rows.append(row)
                
            t3 = Table(doc_rows, colWidths=[420, 120])
            t3.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(t3)
            story.append(Spacer(1, 12))

            # Notice
            notice_text = (
                "<b>Statutory Pre-Screening Assurance:</b> This document certifies provisional eligibility under "
                "MoSJE/NSFDC operational guidelines. Carry this dossier along with original supporting certificates "
                "to the designated channel desk. No intermediary or processing fee is required."
            )
            story.append(Paragraph(notice_text, ParagraphStyle('Notice', parent=body_style, fontSize=7.5, leading=10, textColor=colors.HexColor('#64748B'))))

            doc.build(story)
            pdf_buffer.seek(0)
            
            return send_file(
                pdf_buffer, 
                as_attachment=True, 
                download_name="SchemeSathi_PreScreening_Docket.pdf", 
                mimetype="application/pdf"
            )
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "error", "message": "ReportLab or docket generator not available."}), 500


@app.route("/api/scheme/<int:scheme_id>")
def api_scheme_details(scheme_id):
    user_profile = session.get("profile", {
        "category": "SC",
        "income": 180000,
        "project_cost": 85000,
        "sector": "Micro",
        "intent": "micro",
    })
    schemes_pool = load_schemes_from_json()

    selected_scheme = next((s for s in schemes_pool if s["id"] == scheme_id), None)
    if not selected_scheme:
        return jsonify({"error": "Scheme not found"}), 404

    score, checks, explanation, _ = calculate_match(user_profile, selected_scheme)

    return jsonify({
        "id": selected_scheme["id"],
        "name": selected_scheme["name"],
        "score": score,
        "checks": checks,
        "explanation": explanation,
        "interest_rate": selected_scheme.get("interest_rate", 6.5),
        "moratorium_months": selected_scheme.get("moratorium_months", 3),
        "govt_share_pct": selected_scheme.get("govt_share_pct", 90),
        "promoter_share_pct": selected_scheme.get("promoter_share_pct", 10),
    })


@app.route("/scheme/<int:scheme_id>")
def scheme_details(scheme_id):
    user_profile = session.get("profile", {})
    schemes_pool = load_schemes_from_json()

    selected_scheme = next((s for s in schemes_pool if s["id"] == scheme_id), None)
    if not selected_scheme:
        return "Scheme not found", 404

    score, checks, explanation, _ = calculate_match(user_profile, selected_scheme)

    return render_template(
        "details.html",
        scheme=selected_scheme,
        score=score,
        checks=checks,
        explanation=explanation,
        user=user_profile,
    )


@app.route("/compare")
def compare():
    user_profile = session.get("profile", {})
    schemes_pool = load_schemes_from_json()

    if not schemes_pool:
        return "No schemes available to compare", 404

    try:
        id1 = int(request.args.get("id1", schemes_pool[0]["id"]))
        id2 = int(
            request.args.get(
                "id2", schemes_pool[1]["id"] if len(schemes_pool) > 1 else id1
            )
        )
    except (ValueError, TypeError):
        id1 = schemes_pool[0]["id"]
        id2 = schemes_pool[1]["id"] if len(schemes_pool) > 1 else id1

    scheme1 = next((s for s in schemes_pool if s["id"] == id1), schemes_pool[0]).copy()
    scheme2 = next((s for s in schemes_pool if s["id"] == id2), schemes_pool[1] if len(schemes_pool) > 1 else scheme1).copy()

    scheme1["score"], _, _, _ = calculate_match(user_profile, scheme1)
    scheme2["score"], _, _, _ = calculate_match(user_profile, scheme2)

    return render_template(
        "compare.html", s1=scheme1, s2=scheme2, all_schemes=schemes_pool
    )


@app.route("/robots.txt")
def robots():
    content = "User-agent: *\nAllow: /\nSitemap: https://schemesathi-sih.onrender.com/sitemap.xml"
    return Response(content, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url><loc>https://schemesathi-sih.onrender.com/</loc><priority>1.0</priority></url>
        <url><loc>https://schemesathi-sih.onrender.com/profile</loc><priority>0.8</priority></url>
        <url><loc>https://schemesathi-sih.onrender.com/calculator</loc><priority>0.8</priority></url>
        <url><loc>https://schemesathi-sih.onrender.com/locator</loc><priority>0.8</priority></url>
    </urlset>"""
    return Response(xml, mimetype="application/xml")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
