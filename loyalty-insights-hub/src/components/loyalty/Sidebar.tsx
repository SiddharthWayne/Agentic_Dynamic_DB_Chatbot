import { useEffect, useState } from "react";
import { toast } from "sonner";
import { api, type HealthResponse, type SchemaResponse, type TableDetailResponse } from "@/api/client";
import { Accordion } from "./Accordion";
import { DataTable } from "./DataTable";

interface Settings {
  showSQL: boolean;
  showRawData: boolean;
  showChart: boolean;
}

interface Props {
  health: HealthResponse | null;
  healthError: boolean;
  schema: SchemaResponse | null;
  schemaLoading: boolean;
  selectedTable: string;
  setSelectedTable: (t: string) => void;
  settings: Settings;
  setSettings: (s: Settings) => void;
  onClearChat: () => void;
  onRefreshSchema: () => void;
}

export function Sidebar({
  health, healthError, schema, schemaLoading,
  selectedTable, setSelectedTable, settings, setSettings,
  onClearChat, onRefreshSchema,
}: Props) {
  const [tableDetail, setTableDetail] = useState<TableDetailResponse | null>(null);
  const [tableLoading, setTableLoading] = useState(false);

  useEffect(() => {
    if (!selectedTable) { setTableDetail(null); return; }
    setTableLoading(true);
    api.tableDetail(selectedTable, 5)
      .then((r) => setTableDetail(r.data))
      .catch(() => toast.error(`Failed to load table ${selectedTable}`))
      .finally(() => setTableLoading(false));
  }, [selectedTable]);

  const Pill = ({ ok, label }: { ok: boolean; label: string }) => (
    <span
      className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium"
      style={{ background: ok ? "rgba(45,158,95,0.15)" : "rgba(224,49,49,0.15)", color: ok ? "#4FF7A0" : "#ff6b6b" }}
    >
      {ok ? "✅" : "❌"} {label}
    </span>
  );

  return (
    <aside
      className="la-scroll flex flex-col gap-5 p-5 overflow-y-auto h-screen border-r border-[var(--la-border)]"
      style={{ width: 280, minWidth: 280, background: "var(--la-sidebar)" }}
    >
      <div>
        <div className="flex items-center gap-2 text-lg font-bold text-white">
          <span>💎</span><span>Loyalty Analytics</span>
        </div>
        <div className="mt-3 h-px bg-[var(--la-border)]" />
      </div>

      {/* Health */}
      <section className="flex flex-col gap-2">
        {health && !healthError ? (
          <Pill ok={health.status === "ok"} label={health.status === "ok" ? "API Online" : "API Error"} />
        ) : healthError ? (
          <Pill ok={false} label="API Offline" />
        ) : (
          <div className="h-6 rounded bg-[#1a1d27] animate-pulse" />
        )}
        {health && (
          <div className="flex gap-2">
            <span className="text-xs px-2 py-1 rounded bg-[#1a1d27] border border-[var(--la-border)]">
              Database {health.db_connected ? "✅" : "❌"}
            </span>
            <span className="text-xs px-2 py-1 rounded bg-[#1a1d27] border border-[var(--la-border)]">
              LLM {health.llm_ready ? "✅" : "❌"}
            </span>
          </div>
        )}
        {healthError && (
          <pre className="text-[10px] bg-black/40 p-2 rounded border border-[var(--la-border)] overflow-auto" style={{ fontFamily: "JetBrains Mono, Fira Code, monospace" }}>
uvicorn backend.main:app --reload --port 8000
          </pre>
        )}
      </section>

      {/* Schema */}
      <section className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-[var(--la-text-secondary)]">🗄️ Schema</h3>
          <button
            onClick={onRefreshSchema}
            className="text-xs px-2 py-0.5 rounded border border-[var(--la-border)] hover:bg-[#1a1d27] text-[var(--la-text-secondary)]"
            title="Refresh schema"
          >
            ↻
          </button>
        </div>
        {schemaLoading ? (
          <div className="h-10 rounded bg-[#1a1d27] animate-pulse" />
        ) : (
          <Accordion title="View full schema">
            <pre
              className="la-scroll text-[10px] text-[var(--la-text-secondary)] overflow-auto whitespace-pre"
              style={{ maxHeight: 300, fontFamily: "JetBrains Mono, Fira Code, monospace" }}
            >
              {schema?.schema_text || "No schema available"}
            </pre>
          </Accordion>
        )}
      </section>

      {/* Tables */}
      <section className="flex flex-col gap-2">
        <h3 className="text-sm font-semibold text-[var(--la-text-secondary)]">📋 Tables</h3>
        {schemaLoading ? (
          <div className="h-9 rounded bg-[#1a1d27] animate-pulse" />
        ) : (
          <select
            value={selectedTable}
            onChange={(e) => setSelectedTable(e.target.value)}
            className="w-full bg-[#1a1d27] border border-[var(--la-border)] rounded-md px-2 py-2 text-sm text-white"
          >
            <option value="">— select a table —</option>
            {schema?.tables.map((t) => (<option key={t} value={t}>{t}</option>))}
          </select>
        )}
        {selectedTable && (
          <div className="rounded-md border border-[var(--la-border)] bg-[#0f1117] p-2 mt-1">
            <code className="text-xs text-[var(--la-accent-blue)]">`{selectedTable}`</code>
            {tableLoading ? (
              <div className="h-20 mt-2 rounded bg-[#1a1d27] animate-pulse" />
            ) : tableDetail ? (
              <>
                <div className="mt-2"><DataTable data={tableDetail.preview} /></div>
                <div className="mt-2 text-xs text-[var(--la-text-secondary)]">
                  Rows: <strong className="text-white">{tableDetail.rows.toLocaleString()}</strong> ·
                  Columns: <strong className="text-white"> {tableDetail.columns}</strong>
                </div>
              </>
            ) : null}
          </div>
        )}
      </section>

      {/* Settings */}
      <section className="flex flex-col gap-2">
        <h3 className="text-sm font-semibold text-[var(--la-text-secondary)]">⚙️ Settings</h3>
        {([
          ["showSQL", "Show generated SQL"],
          ["showRawData", "Show raw data table"],
          ["showChart", "Auto-generate chart"],
        ] as const).map(([key, label]) => (
          <label key={key} className="flex items-center justify-between text-sm text-white cursor-pointer">
            <span>{label}</span>
            <button
              onClick={() => setSettings({ ...settings, [key]: !settings[key] })}
              className="relative inline-flex h-5 w-9 rounded-full transition-colors"
              style={{ background: settings[key] ? "var(--la-accent-blue)" : "#2a2d3a" }}
            >
              <span
                className="inline-block h-4 w-4 rounded-full bg-white transition-transform"
                style={{ transform: settings[key] ? "translateX(18px)" : "translateX(2px)", marginTop: 2 }}
              />
            </button>
          </label>
        ))}
        <button
          onClick={onClearChat}
          className="mt-2 w-full px-3 py-1.5 rounded-md border border-[var(--la-border)] text-sm text-white hover:bg-[#1a1d27] transition"
        >
          🗑️ Clear chat history
        </button>
      </section>

      <div className="mt-auto pt-4 border-t border-[var(--la-border)] text-[10px] text-[var(--la-text-muted)] flex flex-col gap-1" style={{ fontFamily: "JetBrains Mono, Fira Code, monospace" }}>
        <div>SQL model: llama-3.3-70b-versatile</div>
        <div>Polish model: llama-3.1-8b-instant</div>
        <div>Row limit: 50</div>
      </div>
    </aside>
  );
}
