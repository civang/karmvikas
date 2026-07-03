document.addEventListener("DOMContentLoaded", () => {
  loadBalances();
  loadMyLeaves();

  const role = Auth.decodedRole();
  if (role === "admin" || role === "hr") {
    document.getElementById("approvals-card").classList.remove("d-none");
    loadPendingApprovals();
  }

  document.getElementById("leave-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      await apiJson("/leaves", {
        method: "POST",
        body: JSON.stringify({
          leave_type: document.getElementById("leave-type").value,
          start_date: document.getElementById("leave-start").value,
          end_date: document.getElementById("leave-end").value,
        }),
      });
      showToast("Leave request submitted", "success");
      e.target.reset();
      loadMyLeaves();
    } catch (err) {
      showError(err);
    }
  });
});

async function loadBalances() {
  try {
    const balances = await apiJson("/leaves/balances");
    document.getElementById("balance-cards").innerHTML = balances
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
  } catch (err) {
    showError(err);
  }
}

async function loadMyLeaves() {
  try {
    const leaves = await apiJson("/leaves");
    const tbody = document.getElementById("my-leaves-body");
    tbody.innerHTML = leaves.length
      ? leaves
          .map(
            (l) => `
      <tr>
        <td class="text-capitalize">${l.leave_type}</td>
        <td>${l.start_date}</td>
        <td>${l.end_date}</td>
        <td>${statusBadge(l.status)}</td>
        <td>${l.comment || "-"}</td>
      </tr>`
          )
          .join("")
      : `<tr><td colspan="5" class="empty-state">No leave requests yet.</td></tr>`;
  } catch (err) {
    showError(err);
  }
}

async function loadPendingApprovals() {
  try {
    const leaves = await apiJson("/leaves?status=pending");
    const tbody = document.getElementById("pending-approvals-body");
    const empty = document.getElementById("approvals-empty");

    if (leaves.length === 0) {
      tbody.innerHTML = "";
      empty.classList.remove("d-none");
      return;
    }
    empty.classList.add("d-none");
    tbody.innerHTML = leaves
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
  } catch (err) {
    showError(err);
  }
}

async function reviewLeave(leaveId, action) {
  try {
    await apiJson(`/leaves/${leaveId}/${action}`, { method: "PATCH", body: JSON.stringify({}) });
    showToast(`Leave ${action}d`, "success");
    loadPendingApprovals();
    loadBalances();
  } catch (err) {
    showError(err);
  }
}

function statusBadge(status) {
  const variant = status === "approved" ? "success" : status === "rejected" ? "danger" : "warning";
  return `<span class="badge text-bg-${variant} text-capitalize">${status}</span>`;
}
