document.addEventListener("DOMContentLoaded", () => {
  loadAttendance();

  document.getElementById("check-in-btn").addEventListener("click", async () => {
    try {
      await apiJson("/attendance/check-in", { method: "POST" });
      showToast("Checked in successfully", "success");
      loadAttendance();
    } catch (err) {
      showError(err);
    }
  });

  document.getElementById("check-out-btn").addEventListener("click", async () => {
    try {
      await apiJson("/attendance/check-out", { method: "POST" });
      showToast("Checked out successfully", "success");
      loadAttendance();
    } catch (err) {
      showError(err);
    }
  });
});

async function loadAttendance() {
  try {
    const records = await apiJson("/attendance");
    const tbody = document.getElementById("attendance-body");
    const empty = document.getElementById("attendance-empty");

    if (records.length === 0) {
      tbody.innerHTML = "";
      empty.classList.remove("d-none");
      return;
    }
    empty.classList.add("d-none");
    tbody.innerHTML = records
      .map(
        (r) => `
      <tr>
        <td>${r.date}</td>
        <td>${r.check_in ? new Date(r.check_in).toLocaleTimeString() : "-"}</td>
        <td>${r.check_out ? new Date(r.check_out).toLocaleTimeString() : "-"}</td>
        <td><span class="badge text-bg-secondary text-capitalize">${r.status}</span></td>
      </tr>`
      )
      .join("");
  } catch (err) {
    showError(err);
  }
}
