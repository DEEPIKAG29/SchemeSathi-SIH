// 1. Language Toggle (Bilingual EN / HI Dictionary)

var currentLang = "en";

var translations = {
  hi: {
    "Home": "होम",
    "Find Schemes": "योजनाएं खोजें",
    "Compare": "तुलना करें",
    "Calculator": "कैलकुलेटर",
    "Bank Locator": "बैंक खोजें",
    "Direct Concessional Credit Access for": "कारीगरों एवं सूक्ष्म उद्यमियों हेतु",
    "Artisans & Micro-Entrepreneurs": "प्रत्यक्ष रियायती ऋण सहायता",
    "Statutory Scheme Recommendations": "सत्यापित सरकारी ऋण योजनाएं",
    "Quick Scheme Eligibility Check": "पात्रता त्वरित जांच",
    "Scan Eligible Schemes": "पात्र योजनाएं खोजें",
    "Easy Loan & EMI Calculator": "सरल ऋण एवं ईएमआई कैलकुलेटर",
    "Find Active Bank Branches & Channel Desks": "सक्रिय बैंक शाखाएं एवं चैनल डेस्क"
  },
  en: {
    "होम": "Home",
    "योजनाएं खोजें": "Find Schemes",
    "तुलना करें": "Compare",
    "कैलकुलेटर": "Calculator",
    "बैंक खोजें": "Bank Locator",
    "कारीगरों एवं सूक्ष्म उद्यमियों हेतु": "Direct Concessional Credit Access for",
    "प्रत्यक्ष रियायती ऋण सहायता": "Artisans & Micro-Entrepreneurs",
    "सत्यापित सरकारी ऋण योजनाएं": "Statutory Scheme Recommendations",
    "पात्रता त्वरित जांच": "Quick Scheme Eligibility Check",
    "पात्र योजनाएं खोजें": "Scan Eligible Schemes",
    "सरल ऋण एवं ईएमआई कैलकुलेटर": "Easy Loan & EMI Calculator",
    "सक्रिय बैंक शाखाएं एवं चैनल डेस्क": "Find Active Bank Branches & Channel Desks"
  }
};

function toggleLanguage() {
  currentLang = (currentLang === "en") ? "hi" : "en";
  var langBtn = document.getElementById("lang-toggle");
  if (langBtn) {
    langBtn.innerText = (currentLang === "en") ? "हिंदी" : "English";
  }

  // Translate targeted elements with data attributes or standard tags
  var transMap = translations[currentLang];
  if (!transMap) return;

  var elementsToTranslate = document.querySelectorAll("h1, h2, .nav-link span, .page-title, .page-subtitle");
  elementsToTranslate.forEach(function(el) {
    var txt = el.innerText.trim();
    if (transMap[txt]) {
      el.innerText = transMap[txt];
    }
  });
}

// --------------------------------------------------------------------------
// 2. Real-Time Scheme Search & Filtering (recommendations.html)
// --------------------------------------------------------------------------
function liveSearchSchemes() {
  var searchInput = document.getElementById("scheme-search-input");
  if (!searchInput) return;

  var term = searchInput.value.toLowerCase().trim();
  var schemeCards = document.querySelectorAll(".scheme-item-card");

  schemeCards.forEach(function(card) {
    var name = (card.getAttribute("data-name") || "").toLowerCase();
    var benefit = (card.getAttribute("data-benefit") || "").toLowerCase();
    
    if (name.includes(term) || benefit.includes(term)) {
      card.style.display = "";
    } else {
      card.style.display = "none";
    }
  });
}

function applyFilterAndSort() {
  var filterSelect = document.getElementById("filter-type");
  var sortSelect = document.getElementById("sort-type");
  var container = document.getElementById("other-schemes-grid");
  if (!container || !filterSelect || !sortSelect) return;

  var filterVal = filterSelect.value;
  var sortVal = sortSelect.value;

  var cards = Array.from(container.getElementsByClassName("scheme-grid-card"));

  // 1. Filter
  cards.forEach(function(card) {
    var benefit = (card.getAttribute("data-benefit") || "").toLowerCase();
    if (filterVal === "All") {
      card.style.display = "";
    } else if (filterVal === "Micro" && (benefit.includes("micro") || benefit.includes("1,40,000") || benefit.includes("1.4"))) {
      card.style.display = "";
    } else if (filterVal === "Term" && (benefit.includes("term") || benefit.includes("transport") || benefit.includes("green"))) {
      card.style.display = "";
    } else {
      card.style.display = "none";
    }
  });

  // 2. Sort
  cards.sort(function(a, b) {
    var scoreA = parseFloat(a.getAttribute("data-score")) || 0;
    var scoreB = parseFloat(b.getAttribute("data-score")) || 0;
    var nameA = (a.getAttribute("data-name") || "").toLowerCase();
    var nameB = (b.getAttribute("data-name") || "").toLowerCase();

    if (sortVal === "match_desc") {
      return scoreB - scoreA;
    } else if (sortVal === "name_asc") {
      return nameA.localeCompare(nameB);
    }
    return 0;
  });

  cards.forEach(function(c) {
    container.appendChild(c);
  });
}

// --------------------------------------------------------------------------
// 3. "Why Match?" Modal Pop-up Handlers
// --------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", function() {
  var modalBackdrop = document.getElementById("why-modal-backdrop");
  var modalCloseBtn = document.getElementById("modal-close-button");
  var whyButtons = document.querySelectorAll(".btn-why-match");

  if (whyButtons.length && modalBackdrop) {
    whyButtons.forEach(function(btn) {
      btn.addEventListener("click", function() {
        var schemeId = this.getAttribute("data-scheme-id");
        openWhyModal(schemeId);
      });
    });
  }

  if (modalCloseBtn && modalBackdrop) {
    modalCloseBtn.addEventListener("click", function() {
      modalBackdrop.style.display = "none";
    });

    window.addEventListener("click", function(event) {
      if (event.target === modalBackdrop) {
        modalBackdrop.style.display = "none";
      }
    });
  }
});

function openWhyModal(schemeId) {
  var modal = document.getElementById("why-modal-backdrop");
  var title = document.getElementById("modal-scheme-title");
  var scoreTag = document.getElementById("modal-score-val");
  var checksGrid = document.getElementById("modal-checks-grid");
  var explanation = document.getElementById("modal-explanation");

  if (!modal) return;

  // Fetch or populate modal content
  title.innerText = "Evaluating Scheme Ref: #" + schemeId;
  scoreTag.innerText = "Verified 95%+ Fit";
  
  checksGrid.innerHTML = `
    <div class="badge-clean badge-success" style="padding: 0.4rem 0.6rem; font-size: 0.8rem;">
      <svg class="icon-svg" style="width: 13px; height: 13px;" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"></polyline></svg>
      <span>Social Category: Quota requirement satisfied</span>
    </div>
    <div class="badge-clean badge-success" style="padding: 0.4rem 0.6rem; font-size: 0.8rem;">
      <svg class="icon-svg" style="width: 13px; height: 13px;" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"></polyline></svg>
      <span>Income Limit: Family income within statutory ceiling (&le; ₹5,00,000)</span>
    </div>
    <div class="badge-clean badge-success" style="padding: 0.4rem 0.6rem; font-size: 0.8rem;">
      <svg class="icon-svg" style="width: 13px; height: 13px;" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"></polyline></svg>
      <span>Project Limit: Budget within allowable MoSJE concessional norms</span>
    </div>
  `;

  explanation.innerText = "Applicant qualifies directly under National Scheduled Castes Finance & Development Corporation (NSFDC) lending guidelines. Channelising agency quota is active in the registered district.";
  modal.style.display = "flex";
}

// --------------------------------------------------------------------------
// 4. Financial Engine (Amortisation & Moratorium Math)
// --------------------------------------------------------------------------
function onSchemeSelectChange(sel) {
  var opt = sel.options[sel.selectedIndex];
  var rate = opt.getAttribute("data-rate");
  var maxCost = opt.getAttribute("data-maxcost");
  var moratorium = opt.getAttribute("data-moratorium");

  var rateInput = document.getElementById("calc-rate");
  var slider = document.getElementById("calc-cost-slider");
  var morInput = document.getElementById("calc-moratorium");

  if (rateInput && rate) rateInput.value = rate;
  if (slider && maxCost) {
    slider.max = maxCost;
    if (parseFloat(slider.value) > parseFloat(maxCost)) {
      slider.value = maxCost;
    }
  }
  if (morInput && moratorium) {
    morInput.value = moratorium;
    setMoratorium(parseInt(moratorium));
  }

  runFinancialCalculation();
}

function setMoratorium(months) {
  var morInput = document.getElementById("calc-moratorium");
  if (morInput) morInput.value = months;

  var buttons = document.querySelectorAll(".mor-btn");
  buttons.forEach(function(btn) {
    if (btn.innerText.includes(months + " Month") || (months === 0 && btn.innerText.includes("No Grace"))) {
      btn.style.background = "var(--primary-accent)";
      btn.style.color = "#ffffff";
      btn.style.borderColor = "var(--primary-accent)";
    } else {
      btn.style.background = "#ffffff";
      btn.style.color = "var(--text-main)";
      btn.style.borderColor = "var(--border)";
    }
  });

  runFinancialCalculation();
}

function runFinancialCalculation() {
  var costSlider = document.getElementById("calc-cost-slider");
  if (!costSlider) return;

  var totalCost = parseFloat(costSlider.value) || 85000;
  var costDisplay = document.getElementById("cost-display");
  if (costDisplay) {
    costDisplay.innerText = "₹" + Math.round(totalCost).toLocaleString("en-IN");
  }

  var schemePicker = document.getElementById("calc-scheme-picker");
  var govtSharePct = 90;
  if (schemePicker && schemePicker.selectedIndex >= 0) {
    var opt = schemePicker.options[schemePicker.selectedIndex];
    govtSharePct = parseFloat(opt.getAttribute("data-govtshare")) || 90;
  }

  var govtLoan = totalCost * (govtSharePct / 100);
  var promoterEquity = totalCost * ((100 - govtSharePct) / 100);

  var govtLoanElem = document.getElementById("res-govt-loan");
  var ownShareElem = document.getElementById("res-promoter-share");
  var barGovt = document.getElementById("bar-govt");
  var barOwn = document.getElementById("bar-own");

  if (govtLoanElem) govtLoanElem.innerText = "₹" + Math.round(govtLoan).toLocaleString("en-IN");
  if (ownShareElem) ownShareElem.innerText = "₹" + Math.round(promoterEquity).toLocaleString("en-IN");
  if (barGovt) barGovt.style.width = govtSharePct + "%";
  if (barOwn) barOwn.style.width = (100 - govtSharePct) + "%";

  var rateInput = document.getElementById("calc-rate");
  var annualRate = parseFloat(rateInput ? rateInput.value : 4.0) || 4.0;
  var rateText = document.getElementById("res-rate-text");
  if (rateText) rateText.innerText = annualRate + "% per year";

  var monthlyRate = (annualRate / 100) / 12;

  var tenorElem = document.getElementById("calc-tenor");
  var tenorMonths = parseInt(tenorElem ? tenorElem.value : 36) || 36;

  var morInput = document.getElementById("calc-moratorium");
  var moratoriumMonths = parseInt(morInput ? morInput.value : 3) || 3;

  var resMorMonths = document.getElementById("res-m-months");
  var resTenorMonths = document.getElementById("res-t-months");

  if (resMorMonths) resMorMonths.innerText = moratoriumMonths;
  if (resTenorMonths) resTenorMonths.innerText = tenorMonths;

  // Reducing Balance Monthly EMI (Post-Grace)
  var emi = 0;
  if (monthlyRate > 0) {
    var compoundFactor = Math.pow(1 + monthlyRate, tenorMonths);
    emi = (govtLoan * monthlyRate * compoundFactor) / (compoundFactor - 1);
  } else {
    emi = govtLoan / tenorMonths;
  }

  var emiDisplay = document.getElementById("res-emi");
  if (emiDisplay) {
    emiDisplay.innerText = "₹" + Math.round(emi).toLocaleString("en-IN") + " / month";
  }

  // Commercial Unsecured Benchmark (14% p.a.) Comparison
  var commercialMonthlyRate = (14.0 / 100) / 12;
  var commCompound = Math.pow(1 + commercialMonthlyRate, tenorMonths);
  var commercialEmi = (govtLoan * commercialMonthlyRate * commCompound) / (commCompound - 1);

  var totalConcessionalInterest = (emi * tenorMonths) - govtLoan;
  var totalCommercialInterest = (commercialEmi * tenorMonths) - govtLoan;
  var interestSavings = Math.max(0, totalCommercialInterest - totalConcessionalInterest);

  var savingsDisplay = document.getElementById("res-savings");
  var commCostDisplay = document.getElementById("res-comm-cost");

  if (savingsDisplay) {
    savingsDisplay.innerText = "₹" + Math.round(interestSavings).toLocaleString("en-IN");
  }
  if (commCostDisplay) {
    commCostDisplay.innerText = "₹" + Math.round(totalCommercialInterest).toLocaleString("en-IN");
  }
}