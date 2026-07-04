document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("forgot-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value.trim();
    const btn = document.getElementById("submit-btn");
    const spinner = document.getElementById("spinner");

    btn.disabled = true;
    spinner.classList.remove("d-none");

    try {
      const res = await fetch(`${API_BASE}/auth/forgot-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => null);
        throw new Error(body && body.error ? body.error.message : "Something went wrong");
      }
      document.getElementById("forgot-form").classList.add("d-none");
      document.getElementById("success-message").classList.remove("d-none");
    } catch (err) {
      showError(err);
    } finally {
      btn.disabled = false;
      spinner.classList.add("d-none");
    }
  });
});
