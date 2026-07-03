const API_BASE = "/api/v1";

const Auth = {
  getAccessToken: () => localStorage.getItem("access_token"),
  getRefreshToken: () => localStorage.getItem("refresh_token"),
  setTokens: (access, refresh) => {
    localStorage.setItem("access_token", access);
    if (refresh) localStorage.setItem("refresh_token", refresh);
  },
  clear: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },
  decodedRole: () => {
    const claims = Auth._decode(Auth.getAccessToken());
    return claims ? claims.role : null;
  },
  decodedUserId: () => {
    const claims = Auth._decode(Auth.getAccessToken());
    return claims ? claims.sub : null;
  },
  _decode: (token) => {
    if (!token) return null;
    try {
      const payload = token.split(".")[1];
      return JSON.parse(atob(payload.replace(/-/g, "+").replace(/_/g, "/")));
    } catch (e) {
      return null;
    }
  },
  isLoggedIn: () => !!Auth.getAccessToken(),
};

async function apiFetch(path, options = {}, retry = true) {
  // FormData sets its own Content-Type with a multipart boundary - forcing
  // application/json here would silently break file uploads.
  const isFormData = options.body instanceof FormData;
  const headers = Object.assign(
    isFormData ? {} : { "Content-Type": "application/json" },
    options.headers || {}
  );
  const token = Auth.getAccessToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (response.status === 401 && retry && Auth.getRefreshToken()) {
    const refreshed = await tryRefresh();
    if (refreshed) return apiFetch(path, options, false);
  }

  if (response.status === 401 || response.status === 403) {
    if (response.status === 401 && !Auth.isLoggedIn()) {
      window.location.href = "/login";
    }
  }

  return response;
}

async function tryRefresh() {
  try {
    const res = await fetch(`${API_BASE}/auth/refresh`, {
      method: "POST",
      headers: { Authorization: `Bearer ${Auth.getRefreshToken()}` },
    });
    if (!res.ok) {
      Auth.clear();
      return false;
    }
    const data = await res.json();
    Auth.setTokens(data.access_token, data.refresh_token);
    return true;
  } catch (e) {
    Auth.clear();
    return false;
  }
}

async function apiJson(path, options = {}) {
  const res = await apiFetch(path, options);
  let body = null;
  try {
    body = await res.json();
  } catch (e) {
    body = null;
  }
  if (!res.ok) {
    const message = body && body.error ? body.error.message : "Something went wrong";
    const err = new Error(message);
    err.status = res.status;
    err.details = body && body.error ? body.error.details : null;
    throw err;
  }
  return body;
}

function requireAuth() {
  if (!Auth.isLoggedIn()) {
    window.location.href = "/login";
  }
}
