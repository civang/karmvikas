document.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search);
  const token = params.get("token");

  if (!token) {
    showToast("This reset link is missing its token. Please request a new one.", "danger");
  }

  document.getElementById("reset-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const newPassword = document.getElementById("new-password").value;
    const confirmPassword = document.getElementById("confirm-password").value;

    if (newPassword !== confirmPassword) {
      showToast("Passwords do not match", "danger");
      return;
    }

    const btn = document.getElementById("submit-btn");
    const spinner = document.getElementById("spinner");
    btn.disabled = true;
    spinner.classList.remove("d-none");

    try {
      const res = await fetch(`${API_BASE}/auth/reset-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, new_password: newPassword }),
      });
      const body = await res.json().catch(() => null);
      if (!res.ok) throw new Error(body && body.error ? body.error.message : "Reset failed");

      document.getElementById("reset-form").classList.add("d-none");
      document.getElementById("success-message").classList.remove("d-none");
    } catch (err) {
      showError(err);
    } finally {
      btn.disabled = false;
      spinner.classList.add("d-none");
    }
  });
});
