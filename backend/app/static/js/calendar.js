let isManager = false;
let allEvents = [];

document.addEventListener("DOMContentLoaded", () => {
  const role = Auth.decodedRole();
  isManager = role === "admin" || role === "hr";

  if (isManager) {
    document.getElementById("add-event-card").classList.remove("d-none");
  }

  document.getElementById("event-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      await apiJson("/calendar-events", {
        method: "POST",
        body: JSON.stringify({
          title: document.getElementById("event-title").value,
          date: document.getElementById("event-date").value,
          event_type: document.getElementById("event-type").value,
          description: document.getElementById("event-description").value,
        }),
      });
      showToast("Event added", "success");
      e.target.reset();
      loadEvents();
    } catch (err) {
      showError(err);
    }
  });

  document.getElementById("type-filter").addEventListener("change", renderEvents);

  loadEvents();
});

async function loadEvents() {
  try {
    allEvents = await apiJson("/calendar-events");
    renderEvents();
  } catch (err) {
    showError(err);
  }
}

function renderEvents() {
  const typeFilter = document.getElementById("type-filter").value;
  const tbody = document.getElementById("events-body");
  const empty = document.getElementById("events-empty");

  const events = typeFilter ? allEvents.filter((e) => e.event_type === typeFilter) : allEvents;

  if (events.length === 0) {
    tbody.innerHTML = "";
    empty.classList.remove("d-none");
    return;
  }
  empty.classList.add("d-none");

  const today = new Date().toISOString().slice(0, 10);
  tbody.innerHTML = events
    .map(
      (e) => `
    <tr>
      <td>${e.date}${e.date >= today ? ' <span class="badge text-bg-info">Upcoming</span>' : ""}</td>
      <td>${e.title}</td>
      <td>${typeBadge(e.event_type)}</td>
      <td>${e.description || "-"}</td>
      <td class="${isManager ? "" : "d-none"}">
        <button class="btn btn-sm btn-outline-danger" onclick="deleteEvent(${e.id})"><i class="bi bi-trash"></i></button>
      </td>
    </tr>`
    )
    .join("");
}

function typeBadge(type) {
  const variants = {
    holiday: "success",
    meeting: "primary",
    deadline: "danger",
    event: "info",
    other: "secondary",
  };
  return `<span class="badge text-bg-${variants[type] || "secondary"} text-capitalize">${type}</span>`;
}

async function deleteEvent(id) {
  if (!confirm("Delete this event?")) return;
  try {
    const res = await apiFetch(`/calendar-events/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Delete failed");
    showToast("Event deleted", "success");
    loadEvents();
  } catch (err) {
    showError(err);
  }
}
