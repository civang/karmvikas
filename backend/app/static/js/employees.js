let currentPage = 1;
let searchDebounce = null;

document.addEventListener("DOMContentLoaded", () => {
  loadDepartmentOptions();
  loadEmployees();

  document.getElementById("search-input").addEventListener("input", () => {
    clearTimeout(searchDebounce);
    searchDebounce = setTimeout(() => {
      currentPage = 1;
      loadEmployees();
    }, 350);
  });

  document.getElementById("department-filter").addEventListener("change", () => {
    currentPage = 1;
    loadEmployees();
  });
});

async function loadDepartmentOptions() {
  try {
    const departments = await apiJson("/departments");
    const select = document.getElementById("department-filter");
    departments.forEach((d) => {
      const opt = document.createElement("option");
      opt.value = d.id;
      opt.textContent = d.name;
      select.appendChild(opt);
    });
  } catch (err) {
    /* directory still works without the filter populated */
  }
}

async function loadEmployees() {
  const search = document.getElementById("search-input").value.trim();
  const departmentId = document.getElementById("department-filter").value;

  const params = new URLSearchParams({ page: currentPage, per_page: 10 });
  if (search) params.set("search", search);
  if (departmentId) params.set("filter[department_id]", departmentId);

  const tbody = document.getElementById("employees-body");
  tbody.innerHTML = `<tr><td colspan="5"><div class="skeleton"></div></td></tr>`;

  try {
    const data = await apiJson(`/employees?${params.toString()}`);
    renderEmployees(data);
  } catch (err) {
    showError(err);
    tbody.innerHTML = "";
  }
}

function renderEmployees(data) {
  const tbody = document.getElementById("employees-body");
  const empty = document.getElementById("employees-empty");

  if (data.items.length === 0) {
    tbody.innerHTML = "";
    empty.classList.remove("d-none");
  } else {
    empty.classList.add("d-none");
    tbody.innerHTML = data.items
      .map(
        (e) => `
      <tr style="cursor:pointer" onclick="openEmployeeModal(${e.id})">
        <td>${e.first_name} ${e.last_name}</td>
        <td>${e.email}</td>
        <td>${e.department_name || "-"}</td>
        <td>${e.designation_title || "-"}</td>
        <td>${e.date_joined}</td>
      </tr>`
      )
      .join("");
  }

  renderPagination(data.meta);
}

function renderPagination(meta) {
  const el = document.getElementById("pagination");
  el.innerHTML = "";
  for (let p = 1; p <= meta.pages; p++) {
    const li = document.createElement("li");
    li.className = `page-item ${p === meta.page ? "active" : ""}`;
    li.innerHTML = `<button class="page-link">${p}</button>`;
    li.addEventListener("click", () => {
      currentPage = p;
      loadEmployees();
    });
    el.appendChild(li);
  }
}

async function openEmployeeModal(employeeId) {
  const modalEl = document.getElementById("employee-modal");
  const modal = new bootstrap.Modal(modalEl);
  document.getElementById("employee-modal-body").innerHTML = `<div class="skeleton"></div>`;
  modal.show();

  try {
    const [e, documents] = await Promise.all([
      apiJson(`/employees/${employeeId}`),
      apiJson(`/employees/${employeeId}/documents`),
    ]);
    const docList = documents.length
      ? documents
          .map(
            (d) => `
        <li class="list-group-item d-flex justify-content-between align-items-center">
          <span><span class="badge text-bg-secondary text-capitalize me-2">${d.document_type.replace("_", " ")}</span>${d.original_filename}</span>
        </li>`
          )
          .join("")
      : `<li class="list-group-item text-secondary">No documents on file.</li>`;

    document.getElementById("employee-modal-body").innerHTML = `
      <p><strong>Name:</strong> ${e.first_name} ${e.last_name}</p>
      <p><strong>Email:</strong> ${e.email}</p>
      <p><strong>Phone:</strong> ${e.phone || "-"}</p>
      <p><strong>Department:</strong> ${e.department_name || "-"}</p>
      <p><strong>Designation:</strong> ${e.designation_title || "-"}</p>
      <p><strong>Joined:</strong> ${e.date_joined}</p>
      <hr>
      <h6 class="text-secondary">Documents</h6>
      <ul class="list-group list-group-flush">${docList}</ul>
    `;
  } catch (err) {
    document.getElementById("employee-modal-body").innerHTML = `<p class="text-danger">${err.message}</p>`;
  }
}
