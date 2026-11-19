const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(detail.detail || `Request failed (${response.status})`);
  }
  return response.json();
}

export const api = {
  products: (params = {}) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== "" && value !== null && value !== undefined) query.set(key, value);
    });
    return request(`/products/?${query.toString()}`);
  },
  chat: (payload) => request("/assistant/chat", {
    method: "POST", body: JSON.stringify(payload),
  }),
  compare: (product_ids) => request("/assistant/compare", {
    method: "POST", body: JSON.stringify({ product_ids }),
  }),
};
