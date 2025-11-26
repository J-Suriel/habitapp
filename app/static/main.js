document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".progress-bar-fill").forEach(el => {
    const percent = el.getAttribute("data-percent") || "0";
    el.style.width = percent + "%";
  });
});
