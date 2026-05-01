export function DataTable({ data }: { data: Record<string, unknown>[] }) {
  if (!data?.length) return null;
  const columns = Object.keys(data[0]);

  const fmt = (v: unknown) => {
    if (v === null || v === undefined) return "";
    if (typeof v === "number") return v.toLocaleString();
    return String(v);
  };
  const isNum = (v: unknown) => typeof v === "number";

  return (
    <div className="la-scroll overflow-auto rounded-md border border-[var(--la-border)]" style={{ maxHeight: 300 }}>
      <table className="w-full text-xs">
        <thead className="sticky top-0 bg-[#0f1117] z-10">
          <tr>
            {columns.map((c) => (
              <th key={c} className="text-left px-3 py-2 font-semibold text-[var(--la-text-secondary)] border-b border-[var(--la-border)] whitespace-nowrap">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i} className={i % 2 ? "bg-[#1a1d27]" : "bg-[#16182199]"}>
              {columns.map((c) => {
                const val = row[c];
                const text = fmt(val);
                return (
                  <td
                    key={c}
                    title={text}
                    className={`px-3 py-1.5 text-white border-b border-[var(--la-border)] max-w-[220px] truncate ${isNum(val) ? "text-right font-mono" : ""}`}
                  >
                    {text}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
