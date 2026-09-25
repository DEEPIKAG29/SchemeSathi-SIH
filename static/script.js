// Function to change steps in the registration form
function goToStep(stepNumber) {
  var step1 = document.getElementById('step-1');
  var step2 = document.getElementById('step-2');
  var step3 = document.getElementById('step-3');

  // Hide all three steps first
  if (step1) { step1.style.display = 'none'; }
  if (step2) { step2.style.display = 'none'; }
  if (step3) { step3.style.display = 'none'; }

  // Show the selected step
  var currentStep = document.getElementById('step-' + stepNumber);
  if (currentStep) {
    currentStep.style.display = 'block';
  }

  // Update circle indicators
  for (var i = 1; i <= 3; i++) {
    var circle = document.getElementById('indicator-' + i);
    if (circle) {
      if (i <= stepNumber) {
        circle.classList.add('active');
      } else {
        circle.classList.remove('active');
      }
    }
  }

  // Update progress lines between steps
  var line1 = document.getElementById('line-1');
  var line2 = document.getElementById('line-2');

  if (line1) {
    if (stepNumber >= 2) {
      line1.classList.add('active');
    } else {
      line1.classList.remove('active');
    }
  }

  if (line2) {
    if (stepNumber >= 3) {
      line2.classList.add('active');
    } else {
      line2.classList.remove('active');
    }
  }
}

// Function to show loading screen and progress bar before submit
function triggerAnalysis() {
  var form = document.getElementById('scheme-profile-form');
  var stepsBar = document.querySelector('.progress-bar-container');
  var loadingScreen = document.getElementById('analyzing-screen');

  if (form) { form.style.display = 'none'; }
  if (stepsBar) { stepsBar.style.display = 'none'; }
  if (loadingScreen) { loadingScreen.style.display = 'block'; }

  var count = 0;
  var bar = document.getElementById('analysis-fill');
  var text = document.getElementById('analysis-percent');

  // Timer to increase progress percentage
  var timer = setInterval(function () {
    count = count + 2;

    if (bar) { bar.style.width = count + '%'; }
    if (text) { text.innerText = count + '%'; }

    // Update check items during progress
    if (count === 30) {
      var s1 = document.getElementById('status-1');
      if (s1) {
        s1.classList.remove('pending');
        s1.classList.add('done');
      }
    }
    if (count === 65) {
      var s2 = document.getElementById('status-2');
      if (s2) {
        s2.classList.remove('pending');
        s2.classList.add('done');
      }
    }
    if (count === 90) {
      var s3 = document.getElementById('status-3');
      if (s3) {
        s3.classList.remove('pending');
        s3.classList.add('done');
      }
    }

    // Submit form after reaching 100 percent
    if (count >= 100) {
      clearInterval(timer);
      if (form) {
        form.submit();
      }
    }
  }, 25);
}

// Function to fetch scheme data and show inside modal box
function openWhyMatch(schemeId) {
  fetch('/api/scheme/' + schemeId)
    .then(function (response) {
      return response.json();
    })
    .then(function (data) {
      document.getElementById('modal-scheme-title').innerText = data.name;
      document.getElementById('modal-score-val').innerText = data.score + '% Match';
      document.getElementById('modal-explanation').innerText = data.explanation;

      var grid = document.getElementById('modal-checks-grid');
      grid.innerHTML = '';

      // Loop through checks dictionary and create items
      for (var key in data.checks) {
        var status = data.checks[key];
        var box = document.createElement('div');

        if (status === true) {
          box.className = 'check-item pass-item';
          box.innerHTML = '<span>✓</span> <strong>' + key + '</strong>: Criteria Matched';
        } else {
          box.className = 'check-item fail-item';
          box.innerHTML = '<span>✕</span> <strong>' + key + '</strong>: Requirement Not Met';
        }

        grid.appendChild(box);
      }

      var modal = document.getElementById('why-modal-backdrop');
      if (modal) {
        modal.style.display = 'flex';
      }
      
      // Modal khulte hi active language check karke text translate karna
      applyCurrentLanguage();
    })
    .catch(function (error) {
      console.log('Error getting scheme data:', error);
    });
}

// Function to close modal box
function closeWhyMatch() {
  var modal = document.getElementById('why-modal-backdrop');
  if (modal) {
    modal.style.display = 'none';
  }
}

// Close modal if user clicks on background
window.addEventListener('click', function (event) {
  var modal = document.getElementById('why-modal-backdrop');
  if (event.target === modal) {
    closeWhyMatch();
  }
});

// Function to filter schemes by subsidy or loan and sort by match score
function applyFilterAndSort() {
  var filterDropdown = document.getElementById('filter-type');
  var sortDropdown = document.getElementById('sort-type');

  if (!filterDropdown || !sortDropdown) {
    return;
  }

  var selectedFilter = filterDropdown.value.toLowerCase();
  var selectedSort = sortDropdown.value;

  var allCards = Array.from(document.querySelectorAll('.scheme-item-card'));
  var gridContainer = document.getElementById('other-schemes-grid');

  // Filter cards by benefit type
  for (var i = 0; i < allCards.length; i++) {
    var card = allCards[i];
    var benefitInfo = (card.getAttribute('data-benefit') || '').toLowerCase();

    if (selectedFilter === 'all') {
      card.style.display = '';
    } else if (selectedFilter === 'subsidy' && (benefitInfo.indexOf('subsidy') > -1 || benefitInfo.indexOf('margin') > -1)) {
      card.style.display = '';
    } else if (selectedFilter === 'loan' && (benefitInfo.indexOf('loan') > -1 || benefitInfo.indexOf('credit') > -1)) {
      card.style.display = '';
    } else {
      card.style.display = 'none';
    }
  }

  // Sort other schemes cards
  if (gridContainer) {
    var otherCards = Array.from(gridContainer.querySelectorAll('.scheme-grid-card'));

    otherCards.sort(function (a, b) {
      var scoreA = Number(a.dataset.score);
      var scoreB = Number(b.dataset.score);
      var nameA = a.dataset.name;
      var nameB = b.dataset.name;

      if (selectedSort === 'match_desc') {
        return scoreB - scoreA;
      }
      if (selectedSort === 'match_asc') {
        return scoreA - scoreB;
      }
      if (selectedSort === 'name_asc') {
        return nameA.localeCompare(nameB);
      }
      return 0;
    });

    for (var j = 0; j < otherCards.length; j++) {
      gridContainer.appendChild(otherCards[j]);
    }
  }
}

// Function to search scheme by typing name in search box
function liveSearchSchemes() {
  var searchBox = document.getElementById('scheme-search-input');
  var searchText = searchBox.value.toLowerCase();
  var cards = document.querySelectorAll('.scheme-item-card');

  for (var i = 0; i < cards.length; i++) {
    var schemeName = (cards[i].getAttribute('data-name') || '').toLowerCase();
    var schemeBenefit = (cards[i].getAttribute('data-benefit') || '').toLowerCase();

    if (schemeName.indexOf(searchText) > -1 || schemeBenefit.indexOf(searchText) > -1) {
      cards[i].style.display = '';
    } else {
      cards[i].style.display = 'none';
    }
  }
}

// Function to calculate checklist progress percentage
function updateDocumentReadiness() {
  var allBoxes = document.querySelectorAll('.doc-checkbox');
  if (allBoxes.length === 0) {
    return;
  }

  var total = allBoxes.length;
  var checked = 0;

  for (var i = 0; i < allBoxes.length; i++) {
    if (allBoxes[i].checked === true) {
      checked = checked + 1;
    }
  }

  var percentage = Math.round((checked / total) * 100);
  var fillBar = document.getElementById('readiness-progress-fill');
  var resultText = document.getElementById('readiness-score-text');

  if (fillBar) {
    fillBar.style.width = percentage + '%';
  }
  if (resultText) {
    resultText.innerText = percentage + '% Ready (' + checked + '/' + total + ')';
  }
}

// Complete Dictionary for English to Hindi translation
var siteTranslations = {
  // Navigation & Common Buttons
  "Home": "होम",
  "About": "के बारे में",
  "About Us": "हमारे बारे में",
  "How It Works": "यह कैसे काम करता है",
  "Compare": "तुलना करें",
  "Find Schemes →": "योजनाएं खोजें →",
  "Find My Schemes →": "मेरी योजनाएं खोजें →",
  "FIND MY SCHEMES →": "मेरी योजनाएं खोजें →",
  "Back to Recommendations": "परिणामों पर वापस जाएं",
  "← Back to Results": "← परिणामों पर वापस जाएं",
  "Compare Schemes": "योजनाओं की तुलना करें",
  "Visit Official Portal →": "आधिकारिक पोर्टल पर जाएं →",
  "VISIT OFFICIAL PORTAL →": "आधिकारिक पोर्टल पर जाएं →",
  "Full Architecture →": "पूरी वास्तुकला देखें →",
  "Start Finding Schemes →": "योजनाएं खोजना शुरू करें →",

  // Home Page
  "GOVERNMENT-BACKED INITIATIVES": "सरकार समर्थित पहल",
  "FIND THE RIGHT GOVERNMENT SCHEME FOR YOUR BUSINESS": "अपने व्यवसाय के लिए सही सरकारी योजना खोजें",
  "Simple. Personalized. Government-backed.": "सरल। व्यक्तिगत। सरकार समर्थित।",
  "Discover Schemes": "योजनाएं खोजें",
  "Browse central and state government schemes curated for your enterprise sector.": "अपने उद्योग क्षेत्र के अनुसार केंद्र और राज्य सरकार की योजनाओं को देखें।",
  "Check Eligibility": "पात्रता जांचें",
  "Instantly evaluate age, category, location, and turnover against official guidelines.": "सरकारी नियमों के अनुसार अपनी आयु, वर्ग, राज्य और आय का तुरंत मिलान करें।",
  "Compare benefits, loan amounts, subsidies, and required documents side-by-side.": "ऋण राशि, सब्सिडी और आवश्यक दस्तावेजों की आमने-सामने तुलना करें।",
  "HOW IT WORKS": "यह कैसे काम करता है",
  "Profile": "प्रोफ़ाइल",
  "Match": "मिलान",
  "Apply": "आवेदन",

  // Profile Form (Stepper)
  "About You": "व्यक्तिगत विवरण",
  "Tell us about your background to determine basic qualification.": "बुनियादी पात्रता निर्धारित करने के लिए अपनी जानकारी दर्ज करें।",
  "Age": "आयु",
  "Gender": "लिंग",
  "Female": "महिला",
  "Male": "पुरुष",
  "Other": "अन्य",
  "State": "राज्य",
  "Category": "सामाजिक वर्ग",
  "Annual Family Income (₹)": "वार्षिक पारिवारिक आय (₹)",
  "Next Step →": "अगला कदम →",
  "← Back": "← वापस",
  "Your Business": "आपका व्यवसाय",
  "Enter details about your current enterprise or idea.": "अपने मौजूदा व्यवसाय या विचार का विवरण दर्ज करें।",
  "Business Status": "व्यवसाय की स्थिति",
  "New Idea": "नया विचार / उद्यम",
  "Existing Enterprise": "मौजूदा उद्यम",
  "Sector": "उद्योग क्षेत्र",
  "Handicraft": "हस्तशिल्प / कारीगर",
  "Manufacturing": "विनिर्माण (Manufacturing)",
  "Services": "सेवाएं (Services)",
  "Retail": "खुदरा (Retail)",
  "Business Stage": "व्यवसाय का चरण",
  "Starting": "शुरुआती चरण",
  "Scaling / Expanding": "विस्तार / विकास",
  "Your Requirements": "आपकी आवश्यकताएं",
  "Final parameters to pinpoint specialized incentives.": "विशेष लाभों और सब्सिडी स्तर की पुष्टि करें।",
  "Area / Location Type": "क्षेत्र का प्रकार",
  "Rural": "ग्रामीण",
  "Urban": "शहरी",
  "Disability / PwD Status": "दिव्यांगता (PwD) स्थिति",
  "No": "नहीं",
  "Yes": "हाँ",

  // Analyzing Screen
  "ANALYZING YOUR PROFILE": "आपकी प्रोफ़ाइल का विश्लेषण हो रहा है",
  "Analyzing Your Profile": "आपकी प्रोफ़ाइल का विश्लेषण हो रहा है",
  "Checking verified government schemes...": "सत्यापित सरकारी योजनाओं की जाँच हो रही है...",
  "Cross-referencing verified government portals...": "सरकारी पोर्टलों के नियमों से मिलान किया जा रहा है...",
  "Demographic parameters parsed": "डेमोग्राफिक विवरण सत्यापित",
  "Evaluating ministry criteria": "मंत्रालय के नियमों का मूल्यांकन",
  "Generating compatibility match scores": "संगतता स्कोर की गणना पूर्ण",

  // Results & Modal Common UI
  "Targeted Government Schemes": "लक्षित सरकारी योजनाएं",
  "Found recommendations sorted by highest qualification compatibility.": "आपकी योग्यता और सर्वाधिक संगतता के अनुसार छांटे गए परिणाम।",
  "Benefit:": "लाभ प्रकार:",
  "Sort:": "क्रम:",
  "All Benefits": "सभी लाभ",
  "Subsidies": "सब्सिडी",
  "Loans": "ऋण",
  "Match Score (Highest First)": "मिलान स्कोर (अधिक से कम)",
  "Match Score (Lowest First)": "मिलान स्कोर (कम से अधिक)",
  "Scheme Name (A-Z)": "योजना का नाम (A-Z)",
  "TOP COMPATIBILITY MATCH": "सर्वश्रेष्ठ संगत योजना",
  "EXCELLENT MATCH": "उत्कृष्ट मिलान",
  "Why This Match?": "यह मिलान क्यों?",
  "Why Match?": "यह मिलान क्यों?",
  "Explore Details →": "पूरा विवरण देखें →",
  "Explore →": "विवरण देखें →",
  "Other Eligible Schemes": "अन्य पात्र योजनाएं",
  "Scheme Eligibility": "योजना पात्रता",
  "VERIFICATION BREAKDOWN": "सत्यापन विवरण",
  "AI REASONING": "सिफारिश का कारण",
  "Criteria Matched": "मापदंड योग्य",
  "Requirement Not Met": "आवश्यकता पूरी नहीं",

  // Compare & Details UI Labels
  "Compare Scheme Options": "योजनाओं की तुलना करें",
  "Analyze parameters side-by-side to choose the best fit for your venture.": "सही निर्णय लेने के लिए दोनों योजनाओं की आमने-सामने तुलना करें।",
  "Select Scheme 1:": "योजना 1 चुनें:",
  "Select Scheme 2:": "योजना 2 चुनें:",
  "Feature / Requirement": "विशेषता / आवश्यकता",
  "Compatibility Score": "संगतता स्कोर",
  "Ministry / Authority": "मंत्रालय / विभाग",
  "Target Category": "लक्षित वर्ग",
  "Target Category:": "लक्षित वर्ग:",
  "Annual Income Limit": "वार्षिक आय सीमा",
  "Eligible Stages": "पात्र चरण",
  "Key Benefits": "मुख्य लाभ",
  "Documentation": "दस्तावेज़ आवश्यकता",
  "Action": "कार्यवाही",
  "View Full Details →": "पूरा विवरण देखें →",
  "Export / Print Summary": "प्रिंट / सारांश डाउनलोड करें",
  "Why This Scheme Matches You": "यह योजना आपसे क्यों मेल खाती है",
  "Core Eligibility Criteria": "मुख्य पात्रता मानदंड",
  "Target Gender:": "लक्षित लिंग:",
  "Applicable State:": "लागू राज्य:",
  "Age Limit:": "आयु सीमा:",
  "Max Annual Income:": "अधिकतम वार्षिक आय:",
  "Area Type:": "क्षेत्र का प्रकार:",
  "Benefits & Support": "लाभ और सहायता",
  "Required Documents & Readiness Tracker": "आवश्यक दस्तावेज़ और तैयारी ट्रैकर",
  "Document Preparation Status": "दस्तावेज़ तैयारी की स्थिति",
  "Application Process": "आवेदन प्रक्रिया",

  // ==========================================
  // SCHEMES DATA TRANSLATIONS (Names & Ministries)
  // ==========================================
  "PM Mudra Yojana": "प्रधानमंत्री मुद्रा योजना",
  "Stand-Up India": "स्टैंड-अप इंडिया योजना",
  "PMEGP Scheme": "पीएमईजीपी (PMEGP) योजना",
  "PM SVANidhi": "पीएम स्वनिधि योजना",
  "Uttarakhand MSME Self-Employment": "उत्तराखंड एमएसएमई स्वरोजगार योजना",
  "PM Vishwakarma Scheme": "प्रधानमंत्री विश्वकर्मा योजना",
  "Credit Guarantee Scheme for Micro Enterprises (CGTMSE)": "क्रेडिट गारंटी योजना (CGTMSE)",
  "National SC-ST Hub Scheme": "राष्ट्रीय एससी-एसटी हब योजना",

  "Ministry of Finance": "वित्त मंत्रालय, भारत सरकार",
  "Ministry of MSME": "सूक्ष्म, लघु एवं मध्यम उद्यम मंत्रालय (MSME)",
  "Ministry of Housing & Urban Affairs": "आवासन और शहरी कार्य मंत्रालय",
  "Govt of Uttarakhand": "उत्तराखंड सरकार",

  // ==========================================
  // SCHEMES DATA TRANSLATIONS (Benefits Content)
  // ==========================================
  "Collateral-free micro loans up to Rs 10 Lakhs.": "बिना किसी गारंटी के 10 लाख रुपये तक का सूक्ष्म ऋण।",
  "Bank loans between 10 Lakhs and 1 Crore for greenfield units.": "नई इकाइयों की स्थापना के लिए 10 लाख से 1 करोड़ रुपये तक का बैंक ऋण।",
  "Capital subsidy up to 35 percent on project cost.": "परियोजना लागत पर 35 प्रतिशत तक की पूंजीगत सब्सिडी।",
  "Working capital loan up to Rs 50,000 with interest subsidy.": "ब्याज सब्सिडी के साथ 50,000 रुपये तक का कार्यशील पूंजी ऋण।",
  "15 to 25 percent capital margin subsidy for local enterprises.": "स्थानीय उद्यमों के लिए 15 से 25 प्रतिशत पूंजीगत मार्जिन सब्सिडी।",
  "Collateral-free enterprise loan up to 3 Lakhs at 5 percent interest plus toolkit incentive.": "5 प्रतिशत ब्याज पर 3 लाख रुपये तक का गारंटी-मुक्त ऋण और टूलकिट सहायता।",
  "Collateral-free credit facility up to Rs 5 Crore through Member Lending Institutions.": "बैंकों और वित्तीय संस्थानों के माध्यम से 5 करोड़ रुपये तक की गारंटी-मुक्त क्रेडिट सुविधा।",
  "Special subsidy reimbursement on registration, testing, and technology upgradation.": "पंजीकरण, परीक्षण और तकनीकी उन्नयन पर विशेष सब्सिडी प्रतिपूर्ति।",

  // ==========================================
  // SCHEMES DATA TRANSLATIONS (Required Documents)
  // ==========================================
  "Identity Card": "पहचान पत्र (आधार / वोटर आईडी)",
  "PAN Card": "पैन कार्ड (PAN Card)",
  "Bank Statement": "बैंक खाता विवरण (Bank Statement)",
  "Bank Account": "बैंक खाता पासबुक",
  "Bank Passbook": "बैंक पासबुक प्रति",
  "Caste Certificate": "जाति प्रमाण पत्र (SC/ST/OBC)",
  "Project Report": "व्यवसाय प्रोजेक्ट रिपोर्ट",
  "Rural Certificate": "ग्रामीण क्षेत्र प्रमाण पत्र",
  "Vending Certificate": "स्ट्रीट वेंडिंग प्रमाण पत्र / विक्रय पहचान पत्र",
  "Uttarakhand Domicile": "उत्तराखंड मूल निवास प्रमाण पत्र",
  "Skill Trade Verification": "पारंपरिक कौशल / कारीगर सत्यापन",
  "Business PAN": "व्यवसाय पैन कार्ड (Business PAN)",
  "Project Balance Sheet": "प्रोजेक्ट बैलेंस शीट विवरण",
  "Udyam Registration": "उद्यम पंजीकरण प्रमाण पत्र",

  // ==========================================
  // SCHEMES DATA TRANSLATIONS (Application Process)
  // ==========================================
  "Apply at bank branch or Udyamimitra portal.": "नजदीकी बैंक शाखा या उद्यमीमित्र पोर्टल के माध्यम से आवेदन करें।",
  "Register on Stand-Up Mitra portal.": "स्टैंड-अप मित्र आधिकारिक पोर्टल पर जाकर ऑनलाइन पंजीकरण करें।",
  "Apply online at KVIC e-portal.": "केवीआईसी (KVIC) के आधिकारिक ई-पोर्टल पर ऑनलाइन आवेदन करें।",
  "Apply via PM SVANidhi portal or urban local body.": "पीएम स्वनिधि पोर्टल या स्थानीय नगर निकाय के माध्यम से आवेदन करें।",
  "Apply at state MSME single window portal.": "राज्य सरकार के एमएसएमई सिंगल विंडो पोर्टल पर ऑनलाइन आवेदन करें।",
  "Apply at Common Services Centre (CSC).": "नजदीकी जन सेवा केंद्र (CSC) पर जाकर बायोमेट्रिक आवेदन करें।",
  "Apply directly through participating scheduled commercial banks.": "योजना से जुड़े वाणिज्यिक बैंकों के माध्यम से सीधे आवेदन करें।",
  "Register on NSSHO portal or NSIC office.": "एनएसएसएचओ पोर्टल पर पंजीकरण करें या एनएसआईसी कार्यालय में संपर्क करें।",

  // About Us Page
  "SMART INDIA HACKATHON 2026": "स्मार्ट इंडिया हैकाथॉन 2026",
  "Democratizing Welfare Access": "सरकारी योजनाओं का सरल और पारदर्शी उपयोग",
  "SchemeSathi is an open-source, rule-based scheme discovery platform built to eliminate administrative friction for India's grassroots entrepreneurs.": "स्कीमसाथी भारत के छोटे उद्यमियों और कारीगरों के लिए सरकारी योजनाओं तक पहुंच को आसान और पारदर्शी बनाने वाला एक मंच है।",
  "THE PROBLEM": "समस्या",
  "Information Asymmetry": "जानकारी का अभाव",
  "Over 60 million micro-enterprises operate in India, yet less than 15% successfully access central or state financial incentives. Fragmented portals, complex criteria, and bureaucratic terminology leave the most deserving entrepreneurs behind.": "भारत में 6 करोड़ से अधिक सूक्ष्म उद्यम हैं, लेकिन 15% से भी कम सरकारी वित्तीय सहायता का लाभ ले पाते हैं। अलग-अलग पोर्टल और कठिन सरकारी भाषा की वजह से पात्र उद्यमी पीछे रह जाते हैं।",
  "OUR PURPOSE": "हमारा उद्देश्य",
  "Deterministic Matching": "पारदर्शी और सटीक मिलान",
  "We replace confusing PDF notifications with an intelligent eligibility engine that parses sector, demographics, and income boundaries into clean compatibility scores and actionable application paths.": "हम कठिन पीडीएफ अधिसूचनाओं की जगह एक स्मार्ट पात्रता इंजन प्रदान करते हैं जो उद्योग, राज्य और आय के आधार पर सटीक मिलान स्कोर और आवेदन का सीधा रास्ता दिखाता है।",
  "Zero Guesswork": "शून्य भ्रम",
  "Every recommendation comes with a point-by-point verification breakdown.": "प्रत्येक सिफारिश के साथ चरण-दर-चरण पात्रता सत्यापन विवरण मिलता है।",
  "Bilingual by Default": "द्विभाषी समर्थन",
  "Accessible in both English and Hindi across the entire user journey.": "पूरे पोर्टल पर अंग्रेजी और हिंदी दोनों भाषाओं में सहज अनुभव उपलब्ध है।",
  "Instant Verification": "तुरंत सत्यापन",
  "Deterministic checks run client- and server-side in milliseconds.": "नियम-आधारित जांच कुछ ही मिलीसेकंड में परिणाम तैयार कर देती है।",
  "PROJECT CREATORS": "परियोजना निर्माता",
  "BCA First Year Students • Developers & Designers": "बीसीए प्रथम वर्ष के छात्र • डेवलपर्स और डिजाइनर्स",

  // How It Works Page
  "SYSTEM WORKFLOW": "सिस्टम कार्यप्रणाली",
  "A transparent, rule-based approach to connecting businesses with the right government support.": "व्यवसायों को सही सरकारी सहायता से जोड़ने का एक पारदर्शी और नियम-आधारित तरीका।",
  "The Problem": "समस्या",
  "Entrepreneurs and small business owners often miss out on available government subsidies and schemes due to fragmented information across multiple portals.": "अलग-अलग वेबसाइटों पर बंटी जानकारी के कारण छोटे व्यापारी और उद्यमी सरकारी सब्सिडी और योजनाओं का लाभ उठाने से चूक जाते हैं।",
  "Our Solution": "हमारा समाधान",
  "SchemeSathi matches verified eligibility criteria against an entrepreneur's specific demographics, location, and business parameters using a deterministic scoring engine.": "स्कीमसाथी एक सटीक स्कोरिंग इंजन के माध्यम से उद्यमी के राज्य, श्रेणी और व्यवसाय के अनुसार सत्यापित सरकारी योजनाओं का मिलान करता है।",
  "System Architecture Pipeline": "सिस्टम आर्किटेक्चर पाइपलाइन",
  "Step-by-step workflow from input to discovery": "डेटा इनपुट से लेकर योजना मिलने तक की चरण-दर-चरण प्रक्रिया",
  "Step 1": "चरण 1",
  "User Profile": "उपयोगकर्ता प्रोफ़ाइल",
  "Demographic criteria, business sector, location category, and income bracket inputs.": "जनसांख्यिकीय विवरण, उद्योग क्षेत्र, स्थान और वार्षिक आय इनपुट।",
  "Step 2": "चरण 2",
  "Criteria Match Engine": "पात्रता मिलान इंजन",
  "Evaluates mandatory government conditions and applies dynamic compatibility weights.": "सरकारी नियमों का मूल्यांकन करता है और पात्रता के आधार पर अंक तय करता है।",
  "Step 3": "चरण 3",
  "Ranked Recommendations": "क्रमबद्ध सिफारिशें",
  "Generates match scores, detailed criteria breakdown, and direct application routes.": "सटीक मिलान स्कोर, पात्रता विवरण और आवेदन के सीधे लिंक प्रस्तुत करता है।",
  "Step 4": "चरण 4",
  "Side-by-Side Comparison": "आमने-सामने तुलना",
  "Allows entrepreneurs to compare loan limits, subsidies, and required documents.": "उद्यमियों को ऋण सीमा, सब्सिडी और आवश्यक दस्तावेजों की एक साथ तुलना करने की सुविधा देता है।"
};

// Reverse dictionary for translating Hindi back to English
var reverseTranslations = {};
for (var key in siteTranslations) {
  reverseTranslations[siteTranslations[key]] = key;
}

// Function to replace words inside text elements
function translateAllTextNodes(node, dictionary) {
  if (node.nodeType === Node.TEXT_NODE) {
    var textValue = node.nodeValue.trim();
    if (textValue && dictionary[textValue]) {
      node.nodeValue = node.nodeValue.replace(textValue, dictionary[textValue]);
    }
  } else {
    if (node.nodeName !== 'SCRIPT' && node.nodeName !== 'STYLE') {
      for (var i = 0; i < node.childNodes.length; i++) {
        translateAllTextNodes(node.childNodes[i], dictionary);
      }
    }
  }
}

// Function to handle language button click
function toggleLanguage() {
  var savedLanguage = localStorage.getItem('schemesathi_lang') || 'en';
  var targetLanguage = 'en';

  if (savedLanguage === 'en') {
    targetLanguage = 'hi';
  } else {
    targetLanguage = 'en';
  }

  localStorage.setItem('schemesathi_lang', targetLanguage);
  applyCurrentLanguage();
}

// Function to apply saved language on page
function applyCurrentLanguage() {
  var savedLanguage = localStorage.getItem('schemesathi_lang') || 'en';
  var button = document.getElementById('lang-toggle');

  if (savedLanguage === 'hi') {
    translateAllTextNodes(document.body, siteTranslations);
    if (button) {
      button.innerText = 'English';
    }
  } else {
    translateAllTextNodes(document.body, reverseTranslations);
    if (button) {
      button.innerText = 'हिंदी';
    }
  }
}

// Run functions when HTML page finishes loading
document.addEventListener('DOMContentLoaded', function () {
  applyCurrentLanguage();

  // Event listener for all Why Match buttons
  document.addEventListener('click', function (event) {
    if (event.target && event.target.classList.contains('btn-why-match')) {
      var schemeId = event.target.getAttribute('data-scheme-id');
      if (schemeId) {
        openWhyMatch(schemeId);
      }
    }
  });

  // Event listener for modal close button
  var closeButton = document.getElementById('modal-close-button');
  if (closeButton) {
    closeButton.addEventListener('click', closeWhyMatch);
  }
});
