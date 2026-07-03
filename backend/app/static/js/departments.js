document.addEventListener("DOMContentLoaded", () => {
  loadDepartments();
  loadDesignations();

  document.getElementById("department-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      await apiJson("/departments", {
        method: "POST",
        body: JSON.stringify({
          name: document.getElementById("dept-name").value,
          description: document.getElementById("dept-description").value,
        }),
      });
      showToast("Department created", "success");
      bootstrap.Modal.getInstance(document.getElementById("department-modal")).hide();
      e.target.reset();
      loadDepartments();
    } catch (err) {
      showError(err);
    }
  });

  document.getElementById("designation-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      await apiJson("/designations", {
        method: "POST",
        body: JSON.stringify({
          title: document.getElementById("desig-title").value,
          department_id: parseInt(document.getElementById("desig-department").value, 10),
        }),
      });
      showToast("Designation created", "success");
      bootstrap.Modal.getInstance(document.getElementById("designation-modal")).hide();
      e.target.reset();
      loadDesignations();
    } catch (err) {
      showError(err);
    }
  });
});

async function loadDepartments() {
  try {
    const departments = await apiJson("/departments");
    const list = document.getElementById("departments-list");
    list.innerHTML = departments.length
      ? departments
          .map(
            (d) => `
      <li class="list-group-item d-flex justify-content-between align-items-center">
        <div><strong>${d.name}</strong><br><small class="text-secondary">${d.description || ""}</small></div>
        <button class="btn btn-sm btn-outline-danger" onclick="deleteDepartment(${d.id})"><i class="bi bi-trash"></i></button>
      </li>`
          )
          .join("")
      : `<li class="list-group-item empty-state">No departments yet.</li>`;

    const select = document.getElementById("desig-department");
    select.innerHTML = departments.map((d) => `<option value="${d.id}">${d.name}</option>`).join("");
  } catch (err) {
    showError(err);
  }
}

async function loadDesignations() {
  try {
    const designations = await apiJson("/designations");
    const list = document.getElementById("designations-list");
    list.innerHTML = designations.length
      ? designations
          .map(
            (d) => `
      <li class="list-group-item d-flex justify-content-between align-items-center">
        ${d.title}
        <button class="btn btn-sm btn-outline-danger" onclick="deleteDesignation(${d.id})"><i class="bi bi-trash"></i></button>
      </li>`
          )
          .join("")
      : `<li class="list-group-item empty-state">No designations yet.</li>`;
  } catch (err) {
    showError(err);
  }
}

async function deleteDepartment(id) {
  if (!confirm("Delete this department?")) return;
  try {
    await deleteResource(`/departments/${id}`);
    showToast("Department deleted", "success");
    loadDepartments();
  } catch (err) {
    showError(err);
  }
}

async function deleteDesignation(id) {
  if (!confirm("Delete this designation?")) return;
  try {
    await deleteResource(`/designations/${id}`);
    showToast("Designation deleted", "success");
    loadDesignations();
  } catch (err) {
    showError(err);
  }
}

async function deleteResource(path) {
  const res = await apiFetch(path, { method: "DELETE" });
  if (!res.ok) {
    let message = "Delete failed";
    try {
      const body = await res.json();
      message = body.error ? body.error.message : message;
    } catch (e) {
      /* no JSON body to parse */
    }
    throw new Error(message);
  }
}
