export default function ItemList({ items }) {
  return (
    <section className="rounded-lg border border-gray-200 p-4">
      <h2 className="mb-3 font-semibold">Saved items ({items.length})</h2>
      {items.length === 0 ? (
        <p className="text-sm text-gray-500">Nothing saved yet.</p>
      ) : (
        <ul className="space-y-2">
          {items.map((it) => (
            <li key={it.id} className="rounded bg-gray-50 p-2 text-sm">
              <div className="mb-1 flex justify-between text-xs text-gray-500">
                <span className="rounded bg-gray-200 px-1.5 py-0.5">
                  {it.source_type}
                </span>
                <span>{it.created_at}</span>
              </div>
              {it.source && (
                <a
                  href={it.source}
                  target="_blank"
                  rel="noreferrer"
                  className="block truncate text-blue-600"
                >
                  {it.source}
                </a>
              )}
              <p className="line-clamp-2 text-gray-700">{it.content}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
