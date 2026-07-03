document.addEventListener("DOMContentLoaded", async () => {
  const role = Auth.decodedRole();
  if (role === "admin" || role === "hr") {
    document.getElementById("admin-dashboard").classList.remove("d-none");
    loadAdminDashboard();
  } else {
    document.getElementById("employee-dashboard").classList.remove("d-none");
    loadEmployeeDashboard();
  }
});

async function loadEmployeeDashboard() {
  try {
    const [attendance, balances, announcements] = await Promise.all([
      apiJson("/attendance"),
      apiJson("/leaves/balances"),
      apiJson("/announcements?limit=5"),
    ]);

    const list = document.getElementById("announcements-list");
    list.innerHTML = announcements.length
      ? announcements
          .map(
            (a) => `
      <div class="border-bottom pb-2 mb-2">
        <strong>${a.title}</strong>
        <p class="mb-0 small text-secondary">${a.body}</p>
      </div>`
          )
          .join("")
      : `<div class="empty-state">No announcements yet.</div>`;

    const today = new Date().toISOString().slice(0, 10);
    const todayRecord = attendance.find((a) => a.date === today);
    document.getElementById("today-status").textContent = todayRecord
      ? `Checked in at ${new Date(todayRecord.check_in).toLocaleTimeString()}`
      : "Not checked in yet";

    const cards = balances
      .map(
        (b) => `
      <div class="col-6 col-md-3">
        <div class="border rounded p-2 text-center">
          <div class="text-secondary text-capitalize small">${b.leave_type}</div>
          <div class="fs-5">${b.remaining}<span class="text-secondary small">/${b.total}</span></div>
        </div>
      </div>`
      )
      .join("");
    document.getElementById("balance-cards").innerHTML = cards;
  } catch (err) {
    showError(err);
  }
}

async function loadAdminDashboard() {
  try {
    const [employees, departments, pendingLeaves] = await Promise.all([
      apiJson("/employees?per_page=1"),
      apiJson("/departments"),
      apiJson("/leaves?status=pending"),
    ]);

    document.getElementById("stat-headcount").textContent = employees.meta.total;
    document.getElementById("stat-departments").textContent = departments.length;
    document.getElementById("stat-pending-leaves").textContent = pendingLeaves.length;

    const tbody = document.getElementById("pending-leaves-body");
    if (pendingLeaves.length === 0) {
      document.getElementById("pending-leaves-empty").classList.remove("d-none");
    } else {
      tbody.innerHTML = pendingLeaves
        .map(
          (l) => `
        <tr>
          <td>#${l.employee_id}</td>
          <td class="text-capitalize">${l.leave_type}</td>
          <td>${l.start_date}</td>
          <td>${l.end_date}</td>
          <td>
            <button class="btn btn-sm btn-success me-1" onclick="reviewLeave(${l.id}, 'approve')">Approve</button>
            <button class="btn btn-sm btn-outline-danger" onclick="reviewLeave(${l.id}, 'reject')">Reject</button>
          </td>
        </tr>`
        )
        .join("");
    }
  } catch (err) {
    showError(err);
  }
}

async function reviewLeave(leaveId, action) {
  try {
    await apiJson(`/leaves/${leaveId}/${action}`, { method: "PATCH", body: JSON.stringify({}) });
    showToast(`Leave ${action}d`, "success");
    loadAdminDashboard();
  } catch (err) {
    showError(err);
  }
}
