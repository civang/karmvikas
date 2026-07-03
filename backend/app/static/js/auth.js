document.addEventListener("DOMContentLoaded", () => {
  if (Auth.isLoggedIn()) {
    window.location.href = "/dashboard";
    return;
  }

  document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const btn = document.getElementById("login-btn");
    const spinner = document.getElementById("login-spinner");

    btn.disabled = true;
    spinner.classList.remove("d-none");

    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ? data.error.message : "Login failed");
      Auth.setTokens(data.access_token, data.refresh_token);
      window.location.href = "/dashboard";
    } catch (err) {
      showError(err);
    } finally {
      btn.disabled = false;
      spinner.classList.add("d-none");
    }
  });

  document.getElementById("forgot-link").addEventListener("click", async (e) => {
    e.preventDefault();
    const email = prompt("Enter your account email:");
    if (!email) return;
    try {
      await fetch(`${API_BASE}/auth/forgot-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      showToast("If an account with that email exists, a reset link has been sent.", "info");
    } catch (err) {
      showError(err);
    }
  });
});
