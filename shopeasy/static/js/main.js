/* ShopEasy JS */
"use strict";

// ── Sidebar mobile toggle ──────────────────────────────────────────────────
const toggle = document.getElementById("menuToggle");
const sidebar = document.getElementById("sidebar");

if (toggle && sidebar) {
  toggle.addEventListener("click", () => {
    sidebar.classList.toggle("open");
  });

  // Close on outside click
  document.addEventListener("click", (e) => {
    if (sidebar.classList.contains("open") && !sidebar.contains(e.target) && e.target !== toggle) {
      sidebar.classList.remove("open");
    }
  });
}

// ── Auto-dismiss flash messages after 5 s ─────────────────────────────────
document.querySelectorAll(".flash").forEach((el) => {
  setTimeout(() => {
    el.style.transition = "opacity 0.5s";
    el.style.opacity = "0";
    setTimeout(() => el.remove(), 500);
  }, 5000);
});

// ── Animate KPI values on load ─────────────────────────────────────────────
function animateCount(el, target, prefix = "", suffix = "", duration = 800) {
  const start = 0;
  const step = (timestamp) => {
    if (!start) start = timestamp;
    const progress = Math.min((timestamp - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = prefix + Math.floor(eased * target).toLocaleString() + suffix;
    if (progress < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

document.querySelectorAll(".kpi-value").forEach((el) => {
  const raw = el.textContent.trim().replace(/[$,]/g, "");
  const val = parseFloat(raw);
  if (!isNaN(val) && val > 0) animateCount(el, val);
});
