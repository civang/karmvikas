(function () {
  // Theme is already applied synchronously by an inline script in <head>
  // (before first paint) to avoid a flash of the wrong theme on navigation.
  const saved = document.documentElement.getAttribute("data-bs-theme") || "light";

  document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("theme-toggle");
    if (!btn) return;
    updateThemeButton(saved);
    btn.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-bs-theme");
      const next = current === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-bs-theme", next);
      localStorage.setItem("theme", next);
      updateThemeButton(next);
    });
  });

  function updateThemeButton(theme) {
    const btn = document.getElementById("theme-toggle");
    if (!btn) return;
    btn.innerHTML =
      theme === "dark"
        ? '<i class="bi bi-sun me-1"></i>Light Mode'
        : '<i class="bi bi-moon-stars me-1"></i>Dark Mode';
  }
})();
