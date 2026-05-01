import { useEffect, useRef, useState, type FormEvent } from "react";
import { toast } from "sonner";
import { api, type HealthResponse, type SchemaResponse } from "@/api/client";
import { Sidebar } from "./Sidebar";
import { MessageBubble, type ChatMessage } from "./MessageBubble";

const EXAMPLES = [
  "Who are the top 10 customers by total points earned?",
  "How many Gold, Silver, and Bronze tier members are there?",
  "What are the total points earned per month in 2024?",
  "Show me the top 5 products by extended sales amount",
  "Which loyalty organizations have the most active members?",
  "What is the average points per transaction by tier?",
];

const uid = () => Math.random().toString(36).slice(2) + Date.now().toString(36);

export function LoyaltyApp() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthError, setHealthError] = useState(false);
  const [schema, setSchema] = useState<SchemaResponse | null>(null);
  const [schemaLoading, setSchemaLoading] = useState(true);
  const [selectedTable, setSelectedTable] = useState("");
  const [settings, setSettings] = useState({ showSQL: true, showRawData: true, showChart: true });
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isQuerying, setIsQuerying] = useState(false);

  const chatEndRef = useRef<HTMLDivElement>(null);

  const loadInitial = async () => {
    setSchemaLoading(true);
    const [healthR, schemaR] = await Promise.allSettled([api.health(), api.schema()]);
    if (healthR.status === "fulfilled") {
      setHealth(healthR.value.data); setHealthError(false);
    } else {
      setHealthError(true); setHealth(null);
      toast.error("Backend offline — start uvicorn on port 8000");
    }
    if (schemaR.status === "fulfilled") setSchema(schemaR.value.data);
    else toast.error("Failed to load schema");
    setSchemaLoading(false);
  };

  useEffect(() => { loadInitial(); }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const refreshSchema = async () => {
    try {
      const r = await api.refreshSchema();
      toast.success(r.data.message);
      const s = await api.schema();
      setSchema(s.data);
    } catch {
      toast.error("Refresh failed");
    }
  };

  const submitQuestion = async (question: string) => {
    if (!question.trim() || isQuerying) return;
    setInput("");
    const userMsg: ChatMessage = { id: uid(), role: "user", content: question };
    const loadingMsg: ChatMessage = { id: uid(), role: "assistant", content: "", isLoading: true };
    setMessages((m) => [...m, userMsg, loadingMsg]);
    setIsQuerying(true);

    try {
      const { data } = await api.query(question);
      const assistantMsg: ChatMessage = {
        id: loadingMsg.id,
        role: "assistant",
        content: data.summary,
        sql: data.sql,
        rowCount: data.row_count,
        data: data.data,
        chartSpec: data.chart_spec,
        error: data.error,
      };
      setMessages((m) => m.map((msg) => (msg.id === loadingMsg.id ? assistantMsg : msg)));
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : "Request failed";
      toast.error(errorMsg);
      setMessages((m) => m.map((msg) =>
        msg.id === loadingMsg.id
          ? { ...msg, isLoading: false, content: "", error: errorMsg }
          : msg
      ));
    } finally {
      setIsQuerying(false);
    }
  };

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    submitQuestion(input);
  };

  // Find latest assistant index for "isLatest" detection
  let latestAssistantId: string | null = null;
  for (let i = messages.length - 1; i >= 0; i--) {
    if (messages[i].role === "assistant" && !messages[i].isLoading) {
      latestAssistantId = messages[i].id;
      break;
    }
  }

  return (
    <div className="flex w-full" style={{ background: "var(--la-bg)", color: "var(--la-text)", minHeight: "100vh" }}>
      <Sidebar
        health={health}
        healthError={healthError}
        schema={schema}
        schemaLoading={schemaLoading}
        selectedTable={selectedTable}
        setSelectedTable={setSelectedTable}
        settings={settings}
        setSettings={setSettings}
        onClearChat={() => setMessages([])}
        onRefreshSchema={refreshSchema}
      />

      <main className="flex-1 flex flex-col h-screen relative">
        {/* Header */}
        <header className="px-8 pt-6 pb-4 border-b border-[var(--la-border)]">
          <h1 className="text-2xl font-bold text-white">💎 Loyalty Data Analytics Agent</h1>
          <p className="text-sm text-[var(--la-text-secondary)] mt-1">
            Ask anything about your loyalty data in plain English. The agent converts your question into SQL, runs it, and explains the results.
          </p>
        </header>

        {/* Examples */}
        <div className="px-8 pt-4">
          <div className="text-xs text-[var(--la-text-secondary)] mb-2">💡 Try an example:</div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
            {EXAMPLES.map((ex) => (
              <button
                key={ex}
                disabled={isQuerying}
                onClick={() => submitQuestion(ex)}
                className="text-left text-xs px-3 py-2 rounded-full border border-[var(--la-border)] bg-[#1a1d27] hover:bg-[#22263080] hover:border-[var(--la-accent-blue)] text-white transition-colors disabled:opacity-50"
              >
                {ex}
              </button>
            ))}
          </div>
        </div>

        {/* Chat */}
        <div className="relative flex-1 overflow-hidden mt-4">
          <div className="absolute inset-x-0 top-0 h-6 z-10 pointer-events-none" style={{ background: "linear-gradient(to bottom, var(--la-bg), transparent)" }} />
          <div className="la-scroll h-full overflow-y-auto px-8 pb-6">
            {messages.length === 0 ? (
              <div className="h-full flex items-center justify-center text-center">
                <div>
                  <div className="text-6xl mb-3">💎</div>
                  <h2 className="text-2xl font-bold text-white">Loyalty Analytics Agent</h2>
                  <p className="text-sm text-[var(--la-text-secondary)] mt-2 max-w-md mx-auto">
                    Ask anything about your loyalty data in plain English.
                  </p>
                </div>
              </div>
            ) : (
              <div className="flex flex-col gap-4 max-w-5xl mx-auto pt-4">
                {messages.map((m) => (
                  <MessageBubble
                    key={m.id}
                    message={m}
                    isLatest={m.id === latestAssistantId}
                    showSQL={settings.showSQL}
                    showRawData={settings.showRawData}
                    showChart={settings.showChart}
                  />
                ))}
                <div ref={chatEndRef} />
              </div>
            )}
          </div>
        </div>

        {/* Input */}
        <form onSubmit={onSubmit} className="px-8 py-4 border-t border-[var(--la-border)] bg-[var(--la-bg)]">
          <div className="max-w-5xl mx-auto flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isQuerying}
              placeholder="Ask a question about the Loyalty Data…"
              className="flex-1 px-4 py-3 rounded-md bg-[var(--la-card)] border border-[var(--la-border)] text-white placeholder:text-[var(--la-text-muted)] focus:outline-none focus:border-[var(--la-accent-blue)] disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={isQuerying || !input.trim()}
              className="px-4 py-3 rounded-md bg-[var(--la-accent-blue)] text-white font-medium hover:opacity-90 disabled:opacity-40 transition"
              aria-label="Send"
            >
              ➤
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}
