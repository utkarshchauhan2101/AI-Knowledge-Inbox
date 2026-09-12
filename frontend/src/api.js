const BASE = "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      /* non-json error body */
    }
    throw new Error(detail);
  }
  return res.json();
}

export const api = {
  ingest: (payload) =>
    request("/ingest", { method: "POST", body: JSON.stringify(payload) }),
  listItems: () => request("/items"),
  query: (question) =>
    request("/query", { method: "POST", body: JSON.stringify({ question }) }),
};
