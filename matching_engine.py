# matching_engine.py
# Hybrid Engine: Demographic Rule Evaluation + NLP Semantic Similarity (TF-IDF)

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from schemes_data import SCHEMES

def compute_nlp_relevance(user_text, scheme_texts):
    """
    Computes mathematical cosine similarity between user's business description 
    and government scheme profiles using TF-IDF Vectorization.
    """
    if not user_text or not user_text.strip():
        return [0.0] * len(scheme_texts)

    corpus = [user_text] + scheme_texts
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    # Calculate cosine similarity of user profile against all schemes
    similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    return similarity_scores

def calculate_match_score(user_profile, scheme, nlp_similarity=0.0):
    checks = {
        "Age": False,
        "Gender": False,
        "Category": False,
        "Income": False,
        "Location": False,
        "Business Status": False,
        "Sector": False
    }

    # 1. Age Rule
    user_age = int(user_profile.get("age", 0))
    if scheme["min_age"] <= user_age <= scheme["max_age"]:
        checks["Age"] = True

    # 2. Gender Rule
    user_gender = user_profile.get("gender", "")
    if user_gender in scheme["gender"] or "Other" in scheme["gender"]:
        checks["Gender"] = True

    # 3. Category Rule (with Stand-Up India special condition)
    user_cat = user_profile.get("category", "")
    if user_cat in scheme["categories"]:
        checks["Category"] = True

    if scheme["id"] == "standup_india" and user_gender == "Male":
        checks["Gender"] = user_cat in ["SC", "ST"]

    # 4. Income Rule
    user_income = float(user_profile.get("income", 0))
    if user_income <= scheme["max_income"]:
        checks["Income"] = True

    # 5. Location Rule (Rural vs Urban)
    user_area = user_profile.get("area", "")
    if "All" in scheme["area"] or user_area in scheme["area"]:
        checks["Location"] = True

    # 6. Business Status Rule (New vs Existing)
    user_b_status = user_profile.get("business_status", "")
    if user_b_status in scheme["business_status"]:
        checks["Business Status"] = True

    # 7. Sector Rule
    user_sector = user_profile.get("sector", "")
    if user_sector in scheme["sectors"]:
        checks["Sector"] = True

    # Rule base weights (Total: 80 points)
    weights = {
        "Category": 15,
        "Sector": 15,
        "Income": 15,
        "Business Status": 15,
        "Location": 10,
        "Gender": 5,
        "Age": 5
    }

    base_rule_score = sum(weights[c] for c, passed in checks.items() if passed)
    
    # NLP semantic similarity weight (Up to 20 bonus points)
    nlp_bonus = min(20, round(float(nlp_similarity) * 30))
    
    total_score = min(100, base_rule_score + nlp_bonus)

    # Explanation text
    matched_count = sum(1 for passed in checks.values() if passed)
    if total_score >= 80:
        summary = f"High compatibility ({total_score}%). Matched {matched_count}/7 demographic rules with positive NLP alignment to {scheme['name']}."
    elif total_score >= 50:
        summary = f"Moderate eligibility ({total_score}%). Good fit, but verify specific operational guidelines for {user_b_status.lower()} units."
    else:
        summary = f"Low alignment ({total_score}%). Key eligibility conditions in sector or category thresholds were not satisfied."

    return {
        "score": total_score,
        "checks": checks,
        "explanation": summary,
        "nlp_score": nlp_bonus
    }

def match_all_schemes(user_profile):
    user_business_desc = user_profile.get("description", "")
    
    # Create scheme contextual corpus for NLP comparison
    scheme_texts = [
        f"{s['name']} {' '.join(s['sectors'])} {s['benefits']} {' '.join(s['area'])}"
        for s in SCHEMES
    ]

    nlp_similarities = compute_nlp_relevance(user_business_desc, scheme_texts)

    results = []
    for idx, scheme in enumerate(SCHEMES):
        sim = nlp_similarities[idx] if idx < len(nlp_similarities) else 0.0
        match_info = calculate_match_score(user_profile, scheme, nlp_similarity=sim)

        if match_info["score"] >= 35:
            results.append({
                **scheme,
                "score": match_info["score"],
                "checks": match_info["checks"],
                "explanation": match_info["explanation"],
                "nlp_bonus": match_info["nlp_score"]
            })

    # Sort descending by match score
    return sorted(results, key=lambda x: x["score"], reverse=True)