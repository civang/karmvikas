document.addEventListener("DOMContentLoaded", () => {
  if (window.location.pathname === "/login") return;
  requireAuth();

  const role = Auth.decodedRole();
  document.getElementById("user-role").textContent = role || "";

  if (role !== "admin" && role !== "hr") {
    document.querySelectorAll(".admin-only").forEach((el) => el.remove());
  }

  const current = window.location.pathname.replace("/", "") || "dashboard";
  document.querySelectorAll("#nav-links .nav-link").forEach((link) => {
    if (link.dataset.page === current) link.classList.add("active");
  });

  document.getElementById("logout-btn").addEventListener("click", async () => {
    try {
      await fetch(`${API_BASE}/auth/logout`, {
        method: "POST",
        headers: { Authorization: `Bearer ${Auth.getRefreshToken()}` },
      });
    } catch (e) {
      /* logout best-effort even if the network call fails */
    }
    Auth.clear();
    window.location.href = "/login";
  });

  const sidebarToggle = document.getElementById("sidebar-toggle");
  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", () => {
      document.getElementById("sidebar").classList.toggle("show");
    });
  }

  loadCurrentUserEmail();
});

async function loadCurrentUserEmail() {
  try {
    const me = await apiJson("/employees/me");
    document.getElementById("user-email").textContent = me.email;
    document.getElementById("user-avatar").textContent = initialsFromName(me.first_name, me.last_name, me.email);
  } catch (e) {
    /* non-fatal: topbar email is a nice-to-have, not required for the page to function */
  }
}

function initialsFromName(firstName, lastName, email) {
  if (firstName && lastName) return (firstName[0] + lastName[0]).toUpperCase();
  return (email || "?").slice(0, 2).toUpperCase();
}
