import { useEffect, useState } from "react";
import { Accordion } from "./Accordion";
import { DataTable } from "./DataTable";
import { ChartView } from "./ChartView";
import type { ChartSpec } from "@/api/client";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sql?: string;
  rowCount?: number;
  data?: Record<string, unknown>[];
  chartSpec?: ChartSpec | null;
  error?: string | null;
  isLoading?: boolean;
}

interface Props {
  message: ChatMessage;
  isLatest: boolean;
  showSQL: boolean;
  showRawData: boolean;
  showChart: boolean;
}

const LOADING_STEPS = [
  "📝 Generating SQL query…",
  "⚡ Running query on PostgreSQL…",
  "✍️ Writing summary…",
  "📈 Generating chart…",
];

function LoadingBubble() {
  const [step, setStep] = useState(0);
  useEffect(() => {
    if (step >= LOADING_STEPS.length - 1) return;
    const t = setTimeout(() => setStep((s) => s + 1), 600);
    return () => clearTimeout(t);
  }, [step]);
  return (
    <div className="flex gap-2 items-center mb-2">
      <div className="flex gap-1">
        <span className="la-dot inline-block w-2 h-2 rounded-full bg-[var(--la-accent-blue)]" />
        <span className="la-dot inline-block w-2 h-2 rounded-full bg-[var(--la-accent-blue)]" />
        <span className="la-dot inline-block w-2 h-2 rounded-full bg-[var(--la-accent-blue)]" />
      </div>
      <span className="text-sm text-white">🧠 Analysing…</span>
      <ul className="ml-4 text-xs text-[var(--la-text-secondary)] list-none">
        {LOADING_STEPS.slice(0, step + 1).map((s, i) => (
          <li key={i} className="la-fade-in">{s}</li>
        ))}
      </ul>
    </div>
  );
}

export function MessageBubble({ message, isLatest, showSQL, showRawData, showChart }: Props) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end la-fade-in">
        <div
          className="px-4 py-2.5 text-white text-sm leading-relaxed"
          style={{
            background: "var(--la-user-bubble)",
            borderRadius: 20,
            maxWidth: "70%",
            wordBreak: "break-word",
          }}
        >
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start la-fade-in">
      <div
        className="p-4 text-white text-sm w-full"
        style={{
          background: "var(--la-card)",
          border: "1px solid var(--la-border)",
          borderRadius: 20,
          maxWidth: "90%",
        }}
      >
        {message.isLoading ? (
          <LoadingBubble />
        ) : (
          <div className="flex flex-col gap-3">
            {showSQL && message.sql && message.sql !== "NO_DATA" && (
              <Accordion title="🛠️ Generated SQL" defaultOpen={isLatest}>
                <pre
                  className="la-scroll text-xs text-[#a8d8ff] overflow-auto whitespace-pre-wrap p-2 bg-black/40 rounded"
                  style={{ fontFamily: "JetBrains Mono, Fira Code, monospace" }}
                >
                  {message.sql}
                </pre>
              </Accordion>
            )}

            {showRawData && message.data && message.data.length > 0 && (
              <Accordion title={`📊 Raw Data (${message.rowCount ?? message.data.length} rows)`} defaultOpen={isLatest}>
                <DataTable data={message.data} />
              </Accordion>
            )}

            {showChart && message.chartSpec && message.chartSpec.chart !== "none" && message.data && message.data.length > 0 && (
              <ChartView spec={message.chartSpec} data={message.data} />
            )}

            {message.error ? (
              <div className="p-3 rounded-md text-sm" style={{ background: "rgba(224,49,49,0.15)", border: "1px solid #e03131", color: "#ff8a8a" }}>
                ⚠️ {message.error}
              </div>
            ) : (
              <p className="text-sm leading-relaxed text-white whitespace-pre-wrap">{message.content}</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
