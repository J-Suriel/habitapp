document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".progress-bar-fill").forEach(el => {
    const percent = el.dataset.percent || 0;
    el.style.width = percent + "%";
  });
});