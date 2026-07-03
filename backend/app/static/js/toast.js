function showToast(message, variant = "primary") {
  const container = document.getElementById("toast-container");
  const el = document.createElement("div");
  el.className = `toast align-items-center text-bg-${variant} border-0`;
  el.role = "alert";
  el.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>`;
  container.appendChild(el);
  const toast = new bootstrap.Toast(el, { delay: 4000 });
  toast.show();
  el.addEventListener("hidden.bs.toast", () => el.remove());
}

function showError(err) {
  showToast(err.message || "Something went wrong", "danger");
}
