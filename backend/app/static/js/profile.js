let myEmployeeId = null;

document.addEventListener("DOMContentLoaded", async () => {
  try {
    const me = await apiJson("/employees/me");
    myEmployeeId = me.id;
    document.getElementById("p-email").value = me.email;
    document.getElementById("p-first-name").value = me.first_name;
    document.getElementById("p-last-name").value = me.last_name;
    document.getElementById("p-phone").value = me.phone || "";
    document.getElementById("p-department").value = me.department_name || "-";
    document.getElementById("p-designation").value = me.designation_title || "-";
    loadDocuments();
  } catch (err) {
    showError(err);
  }

  document.getElementById("document-upload-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById("document-file");
    if (!fileInput.files.length) return;

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("document_type", document.getElementById("document-type").value);

    try {
      const res = await apiFetch(`/employees/${myEmployeeId}/documents`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const body = await res.json().catch(() => null);
        throw new Error(body && body.error ? body.error.message : "Upload failed");
      }
      showToast("Document uploaded", "success");
      e.target.reset();
      loadDocuments();
    } catch (err) {
      showError(err);
    }
  });

  document.getElementById("profile-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      await apiJson(`/employees/${myEmployeeId}`, {
        method: "PATCH",
        body: JSON.stringify({
          first_name: document.getElementById("p-first-name").value,
          last_name: document.getElementById("p-last-name").value,
          phone: document.getElementById("p-phone").value,
        }),
      });
      showToast("Profile updated successfully", "success");
    } catch (err) {
      showError(err);
    }
  });
});

async function loadDocuments() {
  try {
    const documents = await apiJson(`/employees/${myEmployeeId}/documents`);
    const list = document.getElementById("documents-list");
    const empty = document.getElementById("documents-empty");

    if (documents.length === 0) {
      list.innerHTML = "";
      empty.classList.remove("d-none");
      return;
    }
    empty.classList.add("d-none");
    list.innerHTML = documents
      .map(
        (d) => `
      <li class="list-group-item d-flex justify-content-between align-items-center">
        <div>
          <span class="badge text-bg-secondary text-capitalize me-2">${d.document_type.replace("_", " ")}</span>
          ${d.original_filename}
        </div>
        <div>
          <a class="btn btn-sm btn-outline-primary me-1" href="#" onclick="downloadDocument(${d.id}); return false;"><i class="bi bi-download"></i></a>
          <button class="btn btn-sm btn-outline-danger" onclick="deleteDocument(${d.id})"><i class="bi bi-trash"></i></button>
        </div>
      </li>`
      )
      .join("");
  } catch (err) {
    showError(err);
  }
}

async function downloadDocument(documentId) {
  try {
    const res = await apiFetch(`/documents/${documentId}/download`);
    if (!res.ok) throw new Error("Download failed");
    const blob = await res.blob();
    const disposition = res.headers.get("Content-Disposition") || "";
    const match = disposition.match(/filename="?([^"]+)"?/);
    const filename = match ? match[1] : "document";

    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    showError(err);
  }
}

async function deleteDocument(documentId) {
  if (!confirm("Delete this document?")) return;
  try {
    const res = await apiFetch(`/documents/${documentId}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Delete failed");
    showToast("Document deleted", "success");
    loadDocuments();
  } catch (err) {
    showError(err);
  }
}
