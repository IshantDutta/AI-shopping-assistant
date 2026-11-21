const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...(options.headers || {}),
      },
    });
  } catch {
    throw new Error(
      `Cannot reach the backend at ${API_BASE}. Start FastAPI and check the API URL.`
    );
  }

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const detail = payload.detail || payload.message || `Request failed (${response.status})`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return response.json();
}

export const api = {
  health: () => request("/health"),
  status: () => request("/assistant/status"),
  products: (params = {}) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== "" && value !== null && value !== undefined) {
        query.set(key, value);
      }
    });
    const suffix = query.toString();
    return request(`/products/${suffix ? `?${suffix}` : ""}`);
  },
  chat: (payload) => request("/assistant/chat", {
    method: "POST",
    body: JSON.stringify(payload),
  }),
  compare: (product_ids) => request("/assistant/compare", {
    method: "POST",
    body: JSON.stringify({ product_ids }),
  }),
};
