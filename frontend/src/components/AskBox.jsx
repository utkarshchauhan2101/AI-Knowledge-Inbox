import { useState } from "react";
import { api } from "../api";

export default function AskBox() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null); // { answer, sources }
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function ask() {
    if (!question.trim()) return;
    setBusy(true);
    setError("");
    setResult(null);
    try {
      setResult(await api.query(question));
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="rounded-lg border border-gray-200 p-4">
      <h2 className="mb-3 font-semibold">Ask</h2>

      <div className="flex gap-2">
        <input
          className="flex-1 rounded border border-gray-300 p-2"
          placeholder="Ask a question about your saved content…"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && ask()}
        />
        <button
          onClick={ask}
          disabled={busy}
          className="rounded bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
        >
          {busy ? "…" : "Ask"}
        </button>
      </div>

      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}

      {result && (
        <div className="mt-4 space-y-4">
          <div>
            <h3 className="mb-1 text-sm font-semibold text-gray-500">Answer</h3>
            <p className="whitespace-pre-wrap">{result.answer}</p>
          </div>

          {result.sources.length > 0 && (
            <div>
              <h3 className="mb-1 text-sm font-semibold text-gray-500">
                Sources
              </h3>
              <ul className="space-y-2">
                {result.sources.map((s, i) => (
                  <li key={i} className="rounded bg-gray-50 p-2 text-sm">
                    <div className="mb-1 flex justify-between text-xs text-gray-500">
                      <span>
                        item #{s.item_id} · {s.source_type}
                      </span>
                      <span>score {s.score.toFixed(3)}</span>
                    </div>
                    <p className="line-clamp-3 text-gray-700">{s.snippet}</p>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
