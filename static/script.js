// Step Navigation Handler
function goToStep(stepNumber) {
  // Hide all steps
  document.getElementById('step-1').style.display = 'none';
  document.getElementById('step-2').style.display = 'none';
  document.getElementById('step-3').style.display = 'none';

  // Show target step
  document.getElementById('step-' + stepNumber).style.display = 'block';

  // Update progress indicators
  for (let i = 1; i <= 3; i++) {
    const indicator = document.getElementById('indicator-' + i);
    if (i <= stepNumber) {
      indicator.classList.add('active');
    } else {
      indicator.classList.remove('active');
    }
  }

  // Update connecting lines
  if (stepNumber >= 2) {
    document.getElementById('line-1').classList.add('active');
  } else {
    document.getElementById('line-1').classList.remove('active');
  }

  if (stepNumber >= 3) {
    document.getElementById('line-2').classList.add('active');
  } else {
    document.getElementById('line-2').classList.remove('active');
  }
}

// Page 3 Analyzing Simulation Transition
function triggerAnalysis() {
  // Hide the step form and progress bar
  document.getElementById('scheme-profile-form').style.display = 'none';
  document.querySelector('.progress-bar-container').style.display = 'none';

  // Show analyzing screen
  const analyzingScreen = document.getElementById('analyzing-screen');
  analyzingScreen.style.display = 'block';

  let progress = 0;
  const fill = document.getElementById('analysis-fill');
  const percentText = document.getElementById('analysis-percent');

  const timer = setInterval(() => {
    progress += 2;
    fill.style.width = progress + '%';
    percentText.innerText = progress + '%';

    if (progress === 30) {
      document.getElementById('status-1').className = 'done';
    }
    if (progress === 65) {
      document.getElementById('status-2').className = 'done';
    }
    if (progress === 90) {
      document.getElementById('status-3').className = 'done';
    }

    if (progress >= 100) {
      clearInterval(timer);
      // Submit form to Flask backend
      document.getElementById('scheme-profile-form').submit();
    }
  }, 35);
}

// Page 5: Why This Match Modal Logic
function openWhyMatch(schemeId) {
  if (typeof schemesData === 'undefined') return;
  
  const targetScheme = schemesData.find(s => s.id === schemeId);
  if (!targetScheme) return;

  document.getElementById('modal-scheme-title').innerText = targetScheme.name;
  document.getElementById('modal-score-val').innerText = targetScheme.score + '% Match';
  document.getElementById('modal-explanation').innerText = targetScheme.explanation;

  const checksGrid = document.getElementById('modal-checks-grid');
  checksGrid.innerHTML = '';

  for (const [key, passed] of Object.entries(targetScheme.checks)) {
    const item = document.createElement('div');
    item.className = 'check-item ' + (passed ? 'pass-item' : 'fail-item');
    item.innerHTML = `<span>${passed ? '✓' : '✕'}</span> <strong>${key}</strong>: ${passed ? 'Criteria Matched' : 'Requirement Not Met'}`;
    checksGrid.appendChild(item);
  }

  document.getElementById('why-modal-backdrop').style.display = 'flex';
}

function closeWhyMatch() {
  document.getElementById('why-modal-backdrop').style.display = 'none';
}

// Language Translations Dictionary
const translations = {
  en: {
    brand_sub: "Smart Scheme Discovery",
    nav_about: "About",
    nav_how: "How It Works",
    nav_compare: "Compare",
    nav_find: "Find Schemes",
    hero_badge: "Built for Marginalized Entrepreneurs",
    hero_title: "FIND THE RIGHT GOVERNMENT SCHEME FOR YOUR BUSINESS",
    hero_sub: "Simple. Personalized. Government-backed.",
    btn_find_schemes: "FIND MY SCHEMES →",
    card_discover: "Discover Schemes",
    card_discover_p: "Browse verified Central and State initiatives mapped directly to your business category.",
    card_eligibility: "Check Eligibility",
    card_eligibility_p: "Instant rule-based scoring based on your age, category, sector, and location criteria.",
    card_compare: "Compare Schemes",
    card_compare_p: "Evaluate benefits, subsidies, loan terms, and application channels side by side.",
    step_1: "Personal",
    step_2: "Business",
    step_3: "Requirements",
    btn_next: "Next →",
    btn_back: "← Back",
    analyzing_title: "ANALYZING YOUR PROFILE",
    analyzing_sub: "Checking verified government schemes against your criteria..."
  },
  hi: {
    brand_sub: "सरकारी योजना खोज पोर्टल",
    nav_about: "परिचय",
    nav_how: "यह कैसे काम करता है",
    nav_compare: "तुलना करें",
    nav_find: "योजनाएं खोजें",
    hero_badge: "वंचित एवं ग्रामीण उद्यमियों के लिए समर्पित",
    hero_title: "अपने व्यवसाय के लिए सही सरकारी योजना चुनें",
    hero_sub: "सरल। व्यक्तिगत। सरकारी समर्थन प्राप्त।",
    btn_find_schemes: "मेरी योजनाएं खोजें →",
    card_discover: "योजनाएं खोजें",
    card_discover_p: "अपने व्यवसाय श्रेणी से जुड़ी सत्यापित केंद्र और राज्य योजनाओं की सूची देखें।",
    card_eligibility: "पात्रता जांचें",
    card_eligibility_p: "अपनी आयु, वर्ग, क्षेत्र और स्थान के आधार पर तुरंत पात्रता स्कोर जानें।",
    card_compare: "योजनाओं की तुलना करें",
    card_compare_p: "अनुदान (सब्सिडी), ऋण शर्तें और आवेदन प्रक्रिया की आमने-सामने तुलना करें।",
    step_1: "व्यक्तिगत",
    step_2: "व्यवसाय",
    step_3: "आवश्यकताएं",
    btn_next: "आगे बढ़ें →",
    btn_back: "← पीछे जाएं",
    analyzing_title: "आपकी प्रोफाइल का विश्लेषण हो रहा है",
    analyzing_sub: "सरकारी नियमों और योजनाओं के साथ आपकी जानकारी का मिलान जारी है..."
  }
};

let currentLang = localStorage.getItem('schemesathi_lang') || 'en';

function applyLanguage(lang) {
  currentLang = lang;
  localStorage.setItem('schemesathi_lang', lang);
  
  // Toggle button label
  const btnText = document.getElementById('current-lang-text');
  if (btnText) {
    btnText.innerText = (lang === 'en') ? 'हिन्दी' : 'English';
  }

  // Translate all elements with data-i18n attribute
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (translations[lang] && translations[lang][key]) {
      el.innerText = translations[lang][key];
    }
  });
}

function toggleLanguage() {
  const nextLang = (currentLang === 'en') ? 'hi' : 'en';
  applyLanguage(nextLang);
}

// Initial application on page load
document.addEventListener('DOMContentLoaded', () => {
  applyLanguage(currentLang);
});
