/**
 * calibr/ui.js
 *
 * Minimal vanilla JS that enhances the Streamlit UI.
 * Injected via st.components.v1.html() or st.markdown().
 *
 * Modules:
 *   1. Progress bar staggered entrance (runs once on DOM ready)
 *   2. Score number count-up animation
 *   3. Drag-and-drop upload zone highlight
 *   4. Smooth scroll to results after analysis
 *   5. Intersection Observer — fade-up cards on scroll
 */

(function () {
  "use strict";

  /* ─── 1. Progress bar entrance ──────────────────────────────── */
  function animateBars() {
    const bars = document.querySelectorAll(".progress-bar[data-width]");
    bars.forEach((bar, i) => {
      bar.style.width = "0%";
      bar.style.transition = "none";
      const target = bar.getAttribute("data-width") || "0";
      setTimeout(() => {
        bar.style.transition = `width 620ms cubic-bezier(.22,.68,0,1.2) ${i * 80}ms`;
        bar.style.width = target + "%";
      }, 60);
    });
  }

  /* ─── 2. Score count-up ─────────────────────────────────────── */
  function countUp(el, target, duration) {
    if (!el || isNaN(target)) return;
    const start = performance.now();
    const from  = 0;

    function frame(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      // ease-out-quart
      const ease = 1 - Math.pow(1 - progress, 4);
      const value = Math.round(from + (target - from) * ease);
      el.textContent = value;
      if (progress < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  function initCountUp() {
    const scoreEl = document.querySelector(".score-hero-number[data-score]");
    if (!scoreEl) return;
    const target = parseInt(scoreEl.getAttribute("data-score"), 10);
    countUp(scoreEl, target, 900);
  }

  /* ─── 3. Drag-and-drop highlight ────────────────────────────── */
  function initUploadZones() {
    document.querySelectorAll(".upload-zone").forEach((zone) => {
      ["dragenter", "dragover"].forEach((evt) => {
        zone.addEventListener(evt, (e) => {
          e.preventDefault();
          zone.classList.add("drag-over");
        });
      });

      ["dragleave", "drop"].forEach((evt) => {
        zone.addEventListener(evt, () => {
          zone.classList.remove("drag-over");
        });
      });
    });
  }

  /* ─── 4. Smooth scroll to results ───────────────────────────── */
  function scrollToResults() {
    const target = document.querySelector("[data-results-anchor]");
    if (!target) return;
    setTimeout(() => {
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 300);
  }

  /* ─── 5. Intersection Observer — fade-up on scroll ─────────── */
  function initScrollReveal() {
    const cards = document.querySelectorAll(".card, .issue-card, .stat-box, .match-card");
    if (!("IntersectionObserver" in window)) {
      // Fallback: just show everything
      cards.forEach((c) => c.classList.add("animate-fade-up"));
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("animate-fade-up");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.08, rootMargin: "0px 0px -40px 0px" }
    );

    cards.forEach((c) => {
      c.style.opacity = "0";
      observer.observe(c);
    });
  }

  /* ─── 6. Tab active state sync ──────────────────────────────── */
  function syncTabs() {
    document.querySelectorAll(".topbar-nav-item, .sidebar-item").forEach((btn) => {
      btn.addEventListener("click", function () {
        const group = this.closest(".topbar-nav, .sidebar");
        if (!group) return;
        group.querySelectorAll(".topbar-nav-item, .sidebar-item")
             .forEach((b) => b.classList.remove("active"));
        this.classList.add("active");
      });
    });
  }

  /* ─── 7. Auto-collapse long issue lists ─────────────────────── */
  function collapseIssueLists() {
    document.querySelectorAll(".action-list").forEach((list) => {
      const items = list.querySelectorAll("li");
      if (items.length <= 4) return;
      items.forEach((item, i) => {
        if (i >= 4) item.style.display = "none";
      });
      const toggle = document.createElement("li");
      toggle.style.cssText = "cursor:pointer; color: var(--brand); font-weight:600; list-style:none; padding:6px 0;";
      toggle.textContent = `Show ${items.length - 4} more steps`;
      toggle.addEventListener("click", () => {
        items.forEach((item) => (item.style.display = ""));
        toggle.remove();
      });
      list.appendChild(toggle);
    });
  }

  /* ─── Init ──────────────────────────────────────────────────── */
  function init() {
    animateBars();
    initCountUp();
    initUploadZones();
    initScrollReveal();
    syncTabs();
    collapseIssueLists();

    // Listen for Streamlit re-renders (it replaces DOM nodes)
    const observer = new MutationObserver(() => {
      animateBars();
      initCountUp();
      initUploadZones();
      collapseIssueLists();
    });

    observer.observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Expose scrollToResults for Python to call via st.components
  window.calibrScrollToResults = scrollToResults;
})();