import { useState } from "react";
import { api } from "../api";

export default function AddItem({ onAdded }) {
  const [mode, setMode] = useState("note");
  const [value, setValue] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit() {
    if (!value.trim()) return;
    setBusy(true);
    setError("");
    try {
      const payload =
        mode === "note"
          ? { source_type: "note", content: value }
          : { source_type: "url", url: value };
      await api.ingest(payload);
      setValue("");
      onAdded();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="rounded-lg border border-gray-200 p-4">
      <h2 className="mb-3 font-semibold">Add content</h2>

      <div className="mb-3 flex gap-2">
        {["note", "url"].map((m) => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className={`rounded px-3 py-1 text-sm ${
              mode === m ? "bg-gray-900 text-white" : "bg-gray-100"
            }`}
          >
            {m}
          </button>
        ))}
      </div>

      {mode === "note" ? (
        <textarea
          className="w-full rounded border border-gray-300 p-2"
          rows={3}
          placeholder="Paste a note…"
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />
      ) : (
        <input
          className="w-full rounded border border-gray-300 p-2"
          placeholder="https://…"
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />
      )}

      <div className="mt-3 flex items-center gap-3">
        <button
          onClick={submit}
          disabled={busy}
          className="rounded bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
        >
          {busy ? "Saving…" : "Save"}
        </button>
        {error && <span className="text-sm text-red-600">{error}</span>}
      </div>
    </section>
  );
}
