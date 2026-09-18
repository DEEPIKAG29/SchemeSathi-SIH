# app.py
from flask import Flask, render_template, request, session, redirect, url_for
from schemes_data import SCHEMES
from matching_engine import match_all_schemes

app = Flask(__name__)
app.secret_key = "schemesathi_sih_secret_key"  # Session store karne ke liye

@app.route('/')
def home():
    # Page 1: Home Screen
    return render_template('index.html')

@app.route('/profile')
def profile():
    # Page 2 & 3: 3-step Profile Form & Analyzing
    return render_template('profile.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # User ke profile inputs lena
    user_profile = {
        "age": request.form.get("age", 25),
        "gender": request.form.get("gender", "Female"),
        "state": request.form.get("state", "All"),
        "category": request.form.get("category", "General"),
        "income": request.form.get("income", 300000),
        "business_status": request.form.get("business_status", "New"),
        "sector": request.form.get("sector", "Handicraft"),
        "stage": request.form.get("stage", "Starting"),
        "area": request.form.get("area", "Rural"),
        "disability": request.form.get("disability", "No"),
        "description": request.form.get("description", "") 
    }
    
    # Session me save karo taaki baki pages par use ho sake
    session['user_profile'] = user_profile
    
    # Matching algorithm run karo
    matched_schemes = match_all_schemes(user_profile)
    session['matched_schemes'] = matched_schemes

    return redirect(url_for('results'))

@app.route('/results')
def results():
    # Page 4 & 5: Recommendations & Why Match
    user_profile = session.get('user_profile', {})
    matched_schemes = session.get('matched_schemes', [])
    return render_template('details.html', scheme=scheme, profile=user_profile)

@app.route('/scheme/<scheme_id>')
def scheme_details(scheme_id):
    # Page 6: Deep dive details
    scheme = next((s for s in SCHEMES if s["id"] == scheme_id), None)
    user_profile = session.get('user_profile', {})
    return render_template('details.html', scheme=scheme, profile=user_profile)

@app.route('/compare')
def compare():
    # Page 7: Compare Schemes
    return render_template('compare.html', schemes=SCHEMES)

@app.route('/about')
def about():
    # Page 8: How It Works / Architecture
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)