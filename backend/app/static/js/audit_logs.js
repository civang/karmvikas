document.addEventListener("DOMContentLoaded", async () => {
  try {
    const logs = await apiJson("/audit-logs");
    const tbody = document.getElementById("audit-body");
    const empty = document.getElementById("audit-empty");

    if (logs.length === 0) {
      tbody.innerHTML = "";
      empty.classList.remove("d-none");
      return;
    }
    tbody.innerHTML = logs
      .map(
        (l) => `
      <tr>
        <td>${new Date(l.timestamp).toLocaleString()}</td>
        <td>#${l.user_id ?? "-"}</td>
        <td><span class="badge text-bg-secondary">${l.action}</span></td>
        <td>${l.entity}${l.entity_id ? " #" + l.entity_id : ""}</td>
        <td>${l.ip_address || "-"}</td>
      </tr>`
      )
      .join("");
  } catch (err) {
    showError(err);
  }
});
