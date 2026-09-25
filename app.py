import csv
import os
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "schemesathi_secret_key"

# Path for the schemes CSV file
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), "schemes.csv")


# Function to read schemes from CSV file and return a list
def load_schemes_from_csv():
    schemes_list = []

    # Check if file exists
    if not os.path.exists(CSV_FILE_PATH):
        print("CSV file not found:", CSV_FILE_PATH)
        return schemes_list

    # Open and read the CSV file
    with open(CSV_FILE_PATH, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            # Skip empty rows
            if not row or not row.get("name"):
                continue

            # Convert comma or semicolon separated text into python lists
            category_text = row.get("category", "All")
            stage_text = row.get("business_stage", "Starting")
            sector_text = row.get("sector", "")
            docs_text = row.get("documents", "")

            categories = [
                c.strip()
                for c in category_text.replace(";", ",").split(",")
                if c.strip()
            ]
            stages = [
                s.strip() for s in stage_text.replace(";", ",").split(",") if s.strip()
            ]
            sectors = [
                sec.strip()
                for sec in sector_text.replace(";", ",").split(",")
                if sec.strip()
            ]
            documents = [
                d.strip() for d in docs_text.replace(";", ",").split(",") if d.strip()
            ]

            # Convert numbers safely using simple try except
            try:
                scheme_id = int(row.get("id", 1))
            except ValueError:
                scheme_id = 1

            try:
                min_age = int(row.get("min_age", 18))
            except ValueError:
                min_age = 18

            try:
                max_age = int(row.get("max_age", 70))
            except ValueError:
                max_age = 70

            try:
                max_income = int(row.get("max_income", 1000000))
            except ValueError:
                max_income = 1000000

            # Create simple scheme dictionary
            scheme_item = {
                "id": scheme_id,
                "name": row.get("name", "Unnamed Scheme"),
                "ministry": row.get("ministry", "Govt of India"),
                "category": categories if categories else ["All"],
                "gender": row.get("gender", "All"),
                "min_age": min_age,
                "max_age": max_age,
                "state": row.get("state", "All"),
                "max_income": max_income,
                "business_stage": stages if stages else ["Starting"],
                "sector": sectors,
                "area": row.get("area", "All"),
                "benefit_type": row.get("benefit_type", "Subsidy"),
                "benefits": row.get("benefits", "Financial and enterprise support."),
                "documents": documents,
                "application_process": row.get(
                    "application_process", "Apply via official portal."
                ),
                "official_url": row.get("official_url", "#"),
            }

            schemes_list.append(scheme_item)

    return schemes_list


# Function to calculate match score for a scheme based on user profile
def calculate_match(user_profile, scheme):
    score = 40  # Base qualification score
    checks = {}

    if not user_profile:
        return score, {"Profile": False}, "General recommendation."

    # 1. State / Location Match (+15)
    scheme_state = scheme.get("state", "All").strip().lower()
    user_state = user_profile.get("state", "").strip().lower()
    user_state_clean = user_state.replace("(nct)", "").strip()

    if (
        "all" in scheme_state
        or "india" in scheme_state
        or user_state == ""
        or user_state_clean in scheme_state
        or scheme_state in user_state_clean
    ):
        checks["Location"] = True
        score += 15
    else:
        checks["Location"] = False

    # 2. Category Match (+15)
    # Fix: CSV tags like "MSME", "Self-Employment", "Credit" are universal schemes open to all
    user_category = user_profile.get("category", "General").strip().lower()
    raw_categories = scheme.get("category", ["All"])
    if isinstance(raw_categories, str):
        raw_categories = raw_categories.replace(";", ",").split(",")
    scheme_categories = [c.strip().lower() for c in raw_categories]

    is_exclusive_sc_st = any(c in ["sc", "st"] for c in scheme_categories) and not any(
        c in ["all", "msme", "self-employment", "general"] for c in scheme_categories
    )

    if is_exclusive_sc_st:
        if user_category in ["sc", "st"]:
            checks["Category"] = True
            score += 15
        else:
            checks["Category"] = False
    else:
        # Generic schemes (MSME, Credit, Self-Employment, All, General) match everyone
        checks["Category"] = True
        score += 15

    # 3. Sector Match (+15)
    user_sector = user_profile.get("sector", "").strip().lower()
    raw_sectors = scheme.get("sector", [])
    if isinstance(raw_sectors, str):
        raw_sectors = raw_sectors.replace(";", ",").split(",")
    scheme_sectors = [s.strip().lower() for s in raw_sectors]

    sector_matched = False
    for sec in scheme_sectors:
        s_clean = (
            sec.replace("industries", "industry")
            .replace("crafts", "craft")
            .replace("textiles", "textile")
        )
        u_clean = (
            user_sector.replace("industries", "industry")
            .replace("crafts", "craft")
            .replace("textiles", "textile")
        )

        if (
            "all" in sec
            or u_clean in s_clean
            or s_clean in u_clean
            or (
                user_sector == "retail"
                and ("trading" in sec or "business" in sec or "vending" in sec)
            )
            or (
                user_sector == "handicraft"
                and ("traditional" in sec or "artisan" in sec or "craft" in sec)
            )
            or (
                user_sector == "traditional industries"
                and ("artisan" in sec or "handicraft" in sec or "village" in sec)
            )
        ):
            sector_matched = True
            break

    if sector_matched:
        checks["Sector"] = True
        score += 15
    else:
        checks["Sector"] = False

    # 4. Income Match (+10)
    try:
        user_income = int(user_profile.get("income", 0))
    except (ValueError, TypeError):
        user_income = 0

    scheme_max_income = scheme.get("max_income", 1000000)
    try:
        scheme_max_income = int(scheme_max_income)
    except (ValueError, TypeError):
        scheme_max_income = 1000000

    if user_income <= scheme_max_income:
        checks["Income"] = True
        score += 10
    else:
        checks["Income"] = False

    # Cap match score at 98%
    if score > 98:
        score = 98

    explanation = (
        f"Matches your background in {user_profile.get('sector')} and location"
        f" eligibility for {user_profile.get('state')}."
    )
    return score, checks, explanation


# Route for home page
@app.route("/")
def home():
    return render_template("home.html")


# Route for about us page
@app.route("/about")
def about():
    return render_template("about.html")


# Route for how it works page
@app.route("/how-it-works")
def how_it_works():
    return render_template("how_it_works.html")


# Route for user registration form
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        session["profile"] = {
            "age": int(request.form.get("age", 24)),
            "gender": request.form.get("gender", "All"),
            "state": request.form.get("state", "Uttarakhand"),
            "category": request.form.get("category", "General"),
            "income": int(request.form.get("income", 250000)),
            "business_status": request.form.get("business_status", "New"),
            "sector": request.form.get("sector", "Manufacturing"),
            "business_stage": request.form.get("business_stage", "Starting"),
            "area": request.form.get("area", "Rural"),
            "disability": request.form.get("disability", "No"),
        }
        return redirect(url_for("recommendations"))

    return render_template("profile.html")


# Route for displaying ranked scheme recommendations (Strictly >= 90% matches)
@app.route("/recommendations")
def recommendations():
    user_profile = session.get("profile")

    if not user_profile:
        return redirect(url_for("profile"))

    schemes_pool = load_schemes_from_csv()
    ranked_schemes = []

    for item in schemes_pool:
        score, checks, explanation = calculate_match(user_profile, item)

        # STRICT 90%+ FILTER
        if score >= 90:
            scheme_copy = item.copy()
            scheme_copy["score"] = score
            scheme_copy["checks"] = checks
            scheme_copy["explanation"] = explanation
            ranked_schemes.append(scheme_copy)

    ranked_schemes.sort(key=lambda x: x["score"], reverse=True)

    top_match = None
    other_matches = []

    if len(ranked_schemes) > 0:
        top_match = ranked_schemes[0]
    if len(ranked_schemes) > 1:
        other_matches = ranked_schemes[1:]

    return render_template(
        "recommendations.html",
        profile=user_profile,
        top_match=top_match,
        other_matches=other_matches,
        all_ranked=ranked_schemes,
    )


# API endpoint to send scheme details to modal popup
@app.route("/api/scheme/<int:scheme_id>")
def api_scheme_details(scheme_id):
    user_profile = session.get("profile", {})
    schemes_pool = load_schemes_from_csv()

    selected_scheme = None
    for s in schemes_pool:
        if s["id"] == scheme_id:
            selected_scheme = s
            break

    if not selected_scheme:
        return jsonify({"error": "Scheme not found"}), 404

    score, checks, explanation = calculate_match(user_profile, selected_scheme)

    return jsonify({
        "id": selected_scheme["id"],
        "name": selected_scheme["name"],
        "score": score,
        "checks": checks,
        "explanation": explanation,
    })


# Route to show full details of a single scheme
@app.route("/scheme/<int:scheme_id>")
def scheme_details(scheme_id):
    user_profile = session.get("profile", {})
    schemes_pool = load_schemes_from_csv()

    selected_scheme = None
    for s in schemes_pool:
        if s["id"] == scheme_id:
            selected_scheme = s
            break

    if not selected_scheme:
        return "Scheme not found", 404

    score, checks, explanation = calculate_match(user_profile, selected_scheme)

    return render_template(
        "details.html",
        scheme=selected_scheme,
        score=score,
        checks=checks,
        explanation=explanation,
    )


# Route to compare two schemes side by side
@app.route("/compare")
def compare():
    user_profile = session.get("profile", {})
    schemes_pool = load_schemes_from_csv()

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

    scheme1 = None
    scheme2 = None

    for s in schemes_pool:
        if s["id"] == id1:
            scheme1 = s.copy()
        if s["id"] == id2:
            scheme2 = s.copy()

    if not scheme1:
        scheme1 = schemes_pool[0].copy()
    if not scheme2:
        scheme2 = schemes_pool[1].copy() if len(schemes_pool) > 1 else scheme1

    scheme1["score"], _, _ = calculate_match(user_profile, scheme1)
    scheme2["score"], _, _ = calculate_match(user_profile, scheme2)

    return render_template(
        "compare.html", s1=scheme1, s2=scheme2, all_schemes=schemes_pool
    )


# Start Flask server
if __name__ == "__main__":
    app.run(debug=True)