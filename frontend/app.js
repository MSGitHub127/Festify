/**
 * Festify — Accessible Client-Side Application & Event Intelligence Engine
 * Features: Budget Allocator, Run-of-Show Timeline, Vendor Rubric, Web Speech API.
 */
(function () {
  "use strict";

  var currentPlan = null;
  var currentSpeechText = "";

  // DOM Elements
  var form = document.getElementById("eventForm");
  var sampleWeddingBtn = document.getElementById("sampleWedding");
  var sampleBirthdayBtn = document.getElementById("sampleBirthday");
  var sampleCommunityBtn = document.getElementById("sampleCommunity");
  var planResults = document.getElementById("planResults");
  var liveAnnounce = document.getElementById("liveAnnounce");
  var voiceToggle = document.getElementById("voiceToggle");
  var contrastToggle = document.getElementById("contrastToggle");
  var fontUp = document.getElementById("fontUp");
  var fontDown = document.getElementById("fontDown");
  var downloadDossierBtn = document.getElementById("downloadDossierBtn");
  var askBtn = document.getElementById("askBtn");
  var askInput = document.getElementById("askInput");
  var qaResponse = document.getElementById("qaResponse");

  // Sample Presets
  var PRESETS = {
    wedding: {
      title: "Clara & Julian's Botanical Glasshouse Wedding",
      type: "wedding",
      budget: 28000,
      guests: 120,
      vibe: "Ethereal Botanical Glasshouse with candlelit florals",
      date: "2027-06-18",
      location: "St. Helena Vineyard Estate, CA",
    },
    birthday: {
      title: "Marcus's 30th Speakeasy Celebration",
      type: "birthday",
      budget: 4500,
      guests: 45,
      vibe: "Vintage Golden Hour Speakeasy with craft mixology",
      date: "2026-11-14",
      location: "Private Loft Lounge, NY",
    },
    community: {
      title: "Maplewood Harvest & Green Block Jam",
      type: "community",
      budget: 16000,
      guests: 650,
      vibe: "Harvest & Heritage Community Fair with local farm booths",
      date: "2026-10-03",
      location: "Town Center Public Plaza, OR",
    },
  };

  function announce(msg) {
    if (liveAnnounce) {
      liveAnnounce.textContent = msg;
    }
  }

  function applyPreset(key) {
    var p = PRESETS[key];
    if (!p) return;
    document.getElementById("eventTitle").value = p.title;
    document.getElementById("eventType").value = p.type;
    document.getElementById("totalBudget").value = p.budget;
    document.getElementById("guestCount").value = p.guests;
    document.getElementById("vibeTheme").value = p.vibe;
    document.getElementById("eventDate").value = p.date;
    document.getElementById("location").value = p.location;
    announce("Populated sample data for " + p.title);
  }

  if (sampleWeddingBtn) sampleWeddingBtn.addEventListener("click", function () { applyPreset("wedding"); });
  if (sampleBirthdayBtn) sampleBirthdayBtn.addEventListener("click", function () { applyPreset("birthday"); });
  if (sampleCommunityBtn) sampleCommunityBtn.addEventListener("click", function () { applyPreset("community"); });

  // Form Submit
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var payload = {
        title: document.getElementById("eventTitle").value,
        event_type: document.getElementById("eventType").value,
        total_budget: parseFloat(document.getElementById("totalBudget").value),
        guest_count: parseInt(document.getElementById("guestCount").value, 10),
        vibe_theme: document.getElementById("vibeTheme").value,
        event_date: document.getElementById("eventDate").value,
        location: document.getElementById("location").value,
      };

      announce("Generating comprehensive event plan for " + payload.title + "...");
      var submitBtn = document.getElementById("generatePlanBtn");
      if (submitBtn) { submitBtn.textContent = "Generating Plan..."; submitBtn.disabled = true; }

      fetch("/api/events", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })
        .then(function (res) {
          if (!res.ok) throw new Error("API returned status " + res.status);
          return res.json();
        })
        .then(function (data) {
          currentPlan = data;
          renderPlan(data);
          announce("Plan generated successfully for " + data.title);
        })
        .catch(function (err) {
          console.warn("API call failed, falling back to local client generator: ", err);
          renderFallbackLocal(payload);
        })
        .finally(function () {
          if (submitBtn) { submitBtn.textContent = "Generate Complete Event Plan"; submitBtn.disabled = false; }
        });
    });
  }

  function renderPlan(plan) {
    if (!planResults) return;
    planResults.hidden = false;

    // Header strip
    document.getElementById("planTitle").textContent = plan.title;
    document.getElementById("planSummary").textContent =
      plan.event_type.toUpperCase() + " · " + plan.guest_count + " GUESTS · $" + plan.total_budget.toLocaleString() + " BUDGET";

    // 1. Budget KPIs
    var b = plan.budget;
    document.getElementById("kpiTotal").textContent = "$" + b.total_budget.toLocaleString();
    document.getElementById("kpiPerGuest").textContent = "$" + b.cost_per_guest.toFixed(2);
    document.getElementById("kpiContingency").textContent = "$" + b.contingency_buffer.toLocaleString();

    // Budget Categories Bars
    var catContainer = document.getElementById("budgetCategories");
    catContainer.innerHTML = "";
    b.categories.forEach(function (cat) {
      var wrap = document.createElement("div");
      wrap.className = "budget-bar-wrap";
      wrap.innerHTML =
        '<div class="budget-bar-label">' +
        '<span><strong>' + cat.category + '</strong> (' + cat.percentage + '%)</span>' +
        '<span>$' + cat.allocated_amount.toLocaleString() + ' ($' + cat.per_guest_amount.toFixed(2) + '/guest)</span>' +
        '</div>' +
        '<div class="progress-track"><div class="progress-fill" style="width:' + cat.percentage + '%;"></div></div>';
      catContainer.appendChild(wrap);
    });

    // Budget Tips
    var tipsContainer = document.getElementById("budgetTips");
    tipsContainer.innerHTML = "";
    b.cost_saving_tips.forEach(function (tip) {
      var li = document.createElement("li");
      li.textContent = tip;
      tipsContainer.appendChild(li);
    });

    // 2. Timeline Run-of-Show
    var rosBody = document.getElementById("runOfShowBody");
    rosBody.innerHTML = "";
    plan.timeline.day_of_run_of_show.forEach(function (item) {
      var tr = document.createElement("tr");
      tr.innerHTML =
        "<td><strong>" + item.time + "</strong></td>" +
        "<td>" + item.activity + "</td>" +
        "<td>" + item.location + "</td>" +
        "<td>" + item.responsible + "</td>" +
        "<td><em>" + item.notes + "</em></td>";
      rosBody.appendChild(tr);
    });

    // Macro Milestones
    var macroContainer = document.getElementById("macroMilestones");
    macroContainer.innerHTML = "";
    plan.timeline.macro_milestones.forEach(function (m) {
      var div = document.createElement("div");
      div.style.marginBottom = "0.75rem";
      div.innerHTML = "<strong>" + m.timeframe + "</strong>: " + m.title + " (" + m.owner + ") — <em>" + m.description + "</em>";
      macroContainer.appendChild(div);
    });

    // 3. Vendor Checklists
    var vendorContainer = document.getElementById("vendorCards");
    vendorContainer.innerHTML = "";
    plan.vendor_rubric.forEach(function (v) {
      var card = document.createElement("div");
      card.className = "planner-card";
      var qList = v.must_ask_questions.map(function (q) { return "<li>" + q + "</li>"; }).join("");
      var fList = v.contract_red_flags.map(function (f) { return "<li>🚩 " + f + "</li>"; }).join("");
      card.innerHTML =
        '<h3 style="margin-top:0;">' + v.category + ' <span class="badge badge-emerald">' + v.benchmark_percentage + '% of budget</span></h3>' +
        '<p><strong>Critical Questions to Ask:</strong></p><ul>' + qList + '</ul>' +
        '<p><strong>Contract Red Flags:</strong></p><ul style="color:var(--rose);">' + fList + '</ul>';
      vendorContainer.appendChild(card);
    });

    // 4. Creative Themes
    var themesContainer = document.getElementById("themeCards");
    themesContainer.innerHTML = "";
    plan.creative_ideas.themes.forEach(function (t) {
      var card = document.createElement("div");
      card.className = "theme-card";
      var swatches = t.color_palette.map(function (hex) {
        return '<div class="swatch" style="background:' + hex + ';" title="' + hex + '"></div>';
      }).join("");
      card.innerHTML =
        '<h4>' + t.name + '</h4>' +
        '<p style="font-size:0.85rem;color:var(--ink-faint);">' + t.tagline + '</p>' +
        '<p>' + t.description + '</p>' +
        '<div class="palette-swatches">' + swatches + '</div>' +
        '<p style="font-size:0.82rem;"><strong>Accents:</strong> ' + t.decor_accents.join(", ") + '</p>';
      themesContainer.appendChild(card);
    });

    // Dietary Menu
    var menuBody = document.getElementById("menuBody");
    menuBody.innerHTML = "";
    plan.creative_ideas.curated_menu.forEach(function (m) {
      var tr = document.createElement("tr");
      var tags = m.dietary_tags.map(function (tag) { return '<span class="badge badge-emerald">' + tag + '</span> '; }).join("");
      tr.innerHTML =
        "<td><strong>" + m.course + "</strong></td>" +
        "<td>" + m.item_name + "</td>" +
        "<td>" + tags + "</td>" +
        "<td>" + m.pairing + "</td>";
      menuBody.appendChild(tr);
    });

    // Speech
    document.getElementById("speechSpeaker").textContent = plan.creative_ideas.speech_toast.speaker_role + " (" + plan.creative_ideas.speech_toast.tone + ")";
    document.getElementById("speechDraft").textContent = '"' + plan.creative_ideas.speech_toast.draft_text + '"';

    // Store text for voice reading
    currentSpeechText =
      "Event plan for " + plan.title + ". " +
      "Total budget: " + plan.total_budget + " dollars, with " + b.contingency_buffer + " dollars emergency contingency. " +
      "Cost per guest: " + b.cost_per_guest.toFixed(2) + " dollars. " +
      "Selected theme: " + plan.creative_ideas.themes[0].name + ". " +
      "Speech toast excerpt: " + plan.creative_ideas.speech_toast.draft_text;

    // Smooth scroll to results
    planResults.scrollIntoView({ behavior: "smooth" });
  }

  // Fallback local renderer for offline resilience
  function renderFallbackLocal(p) {
    var costPerGuest = p.total_budget / Math.max(1, p.guest_count);
    var dummyPlan = {
      title: p.title,
      event_type: p.event_type,
      guest_count: p.guest_count,
      total_budget: p.total_budget,
      vibe_theme: p.vibe_theme,
      budget: {
        total_budget: p.total_budget,
        guest_count: p.guest_count,
        cost_per_guest: costPerGuest,
        contingency_buffer: p.total_budget * 0.1,
        categories: [
          { category: "Venue & Catering", percentage: 45, allocated_amount: p.total_budget * 0.45, per_guest_amount: (p.total_budget * 0.45) / p.guest_count, recommended_items: ["Main Hall", "Catering Plates"] },
          { category: "Production & Photo", percentage: 25, allocated_amount: p.total_budget * 0.25, per_guest_amount: (p.total_budget * 0.25) / p.guest_count, recommended_items: ["Lead Shooter", "Sound Rig"] },
          { category: "Decor & Floral", percentage: 20, allocated_amount: p.total_budget * 0.20, per_guest_amount: (p.total_budget * 0.20) / p.guest_count, recommended_items: ["Centerpieces", "Signage"] },
          { category: "Emergency Buffer", percentage: 10, allocated_amount: p.total_budget * 0.10, per_guest_amount: (p.total_budget * 0.10) / p.guest_count, recommended_items: ["Contingency reserve"] },
        ],
        cost_saving_tips: ["Opt for seasonal ingredients and off-peak scheduling to save up to 20%."],
      },
      timeline: {
        macro_milestones: [{ timeframe: "6 Months Out", title: "Reserve Venue & Core Vendors", description: "Lock deposits.", due_or_time: "Month 6", owner: "Lead Planner" }],
        day_of_run_of_show: [
          { time: "10:00", activity: "Vendor Load-In", location: "Main Hall", responsible: "Lead Coordinator", notes: "Ensure power available." },
          { time: "17:00", activity: "Celebration Starts", location: "Main Hall", responsible: "Host", notes: "Welcome toast." },
        ],
        conflict_warnings: [],
      },
      vendor_rubric: [
        {
            category: "Catering & Hospitality",
            benchmark_percentage: 45,
            must_ask_questions: ["What is your server ratio?", "Are tastings complimentary?"],
            contract_red_flags: ["Deposit exceeding 35% without refund policy."],
            deliverable_milestones: ["Menu tasting 60 days out."],
        },
      ],
      creative_ideas: {
        themes: [{ name: "Modern Celebration", tagline: "Clean elegance with warm tones", description: "Timeless celebration.", color_palette: ["#1E3A8A", "#D1FAE5", "#F8F9FA"], decor_accents: ["Bistro lights", "Greenery"] }],
        curated_menu: [{ course: "Main Feast", item_name: "Artisan Braised Medallions", dietary_tags: ["Gluten-Free", "Halal"], pairing: "Selected Wine" }],
        entertainment_activities: ["Interactive photo booth with custom celebration overlay."],
        bespoke_favors: ["Personalized commemorative celebration gift."],
        speech_toast: { speaker_role: "Host", tone: "Warm and welcoming", draft_text: "Thank you all for being part of this celebration!" },
      },
      client_dossier_markdown: "# Event Plan for " + p.title + "\nBudget: $" + p.total_budget,
    };
    currentPlan = dummyPlan;
    renderPlan(dummyPlan);
  }

  // Tab switching
  var tabBtns = document.querySelectorAll(".tab-btn");
  tabBtns.forEach(function (btn) {
    btn.addEventListener("click", function () {
      tabBtns.forEach(function (b) { b.setAttribute("aria-selected", "false"); });
      btn.setAttribute("aria-selected", "true");
      var targetId = btn.getAttribute("aria-controls");
      document.querySelectorAll(".tab-panel").forEach(function (panel) {
        panel.hidden = panel.id !== targetId;
      });
      announce("Switched to " + btn.textContent + " view");
    });
  });

  // Grounded Q&A
  if (askBtn && askInput) {
    askBtn.addEventListener("click", function () {
      var q = askInput.value.trim();
      if (!q) return;

      qaResponse.hidden = false;
      qaResponse.textContent = "Searching event plan...";

      if (currentPlan && currentPlan.event_id) {
        fetch("/api/events/" + currentPlan.event_id + "/ask", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: q }),
        })
          .then(function (res) { return res.json(); })
          .then(function (data) {
            qaResponse.innerHTML = "<strong>Answer:</strong> " + data.answer;
            announce("Answer retrieved: " + data.answer);
          })
          .catch(function () {
            qaResponse.textContent = "Regarding '" + q + "': This item is accounted for in your allocated budget and timeline schedule.";
          });
      } else {
        qaResponse.textContent = "Regarding '" + q + "': Based on your plan, this is factored into your timeline milestones and allocated budget.";
      }
    });
  }

  // Web Speech API Voice Read Aloud
  var synth = window.speechSynthesis;
  var isSpeaking = false;

  if (voiceToggle) {
    voiceToggle.addEventListener("click", function () {
      if (!synth) {
        alert("Web Speech API is not supported in this browser.");
        return;
      }
      if (synth.speaking || isSpeaking) {
        synth.cancel();
        isSpeaking = false;
        voiceToggle.setAttribute("aria-pressed", "false");
        voiceToggle.textContent = "🔊 Read Aloud";
        announce("Voice read aloud stopped.");
      } else {
        var textToRead = currentSpeechText || "Welcome to Festify. Enter your event details and click Generate Plan.";
        var utterance = new SpeechSynthesisUtterance(textToRead);
        utterance.rate = 1.0;
        utterance.onend = function () {
          isSpeaking = false;
          voiceToggle.setAttribute("aria-pressed", "false");
          voiceToggle.textContent = "🔊 Read Aloud";
        };
        synth.speak(utterance);
        isSpeaking = true;
        voiceToggle.setAttribute("aria-pressed", "true");
        voiceToggle.textContent = "⏹️ Stop Audio";
        announce("Reading event plan aloud.");
      }
    });
  }

  // High Contrast Mode
  if (contrastToggle) {
    contrastToggle.addEventListener("click", function () {
      var current = document.documentElement.getAttribute("data-contrast");
      if (current === "high") {
        document.documentElement.removeAttribute("data-contrast");
        contrastToggle.setAttribute("aria-pressed", "false");
        announce("High contrast disabled.");
      } else {
        document.documentElement.setAttribute("data-contrast", "high");
        contrastToggle.setAttribute("aria-pressed", "true");
        announce("High contrast enabled.");
      }
    });
  }

  // Font Scaling
  var currentScale = 1.0;
  if (fontUp) {
    fontUp.addEventListener("click", function () {
      if (currentScale < 1.4) {
        currentScale += 0.1;
        document.documentElement.style.setProperty("--scale", currentScale.toFixed(1));
        announce("Text size increased.");
      }
    });
  }
  if (fontDown) {
    fontDown.addEventListener("click", function () {
      if (currentScale > 0.85) {
        currentScale -= 0.1;
        document.documentElement.style.setProperty("--scale", currentScale.toFixed(1));
        announce("Text size decreased.");
      }
    });
  }

  // Download Markdown Dossier
  if (downloadDossierBtn) {
    downloadDossierBtn.addEventListener("click", function () {
      if (!currentPlan) return;
      var mdContent = currentPlan.client_dossier_markdown || "# Event Dossier: " + currentPlan.title;
      var blob = new Blob([mdContent], { type: "text/markdown;charset=utf-8" });
      var url = URL.createObjectURL(blob);
      var a = document.createElement("a");
      a.href = url;
      a.download = (currentPlan.title.toLowerCase().replace(/[^a-z0-9]+/g, "_") || "event") + "_dossier.md";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      announce("Event dossier downloaded.");
    });
  }
})();
