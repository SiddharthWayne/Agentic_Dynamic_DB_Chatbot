import axios from "axios";

const API_BASE = "http://localhost:8000";

export interface HealthResponse {
  status: string;
  db_connected: boolean;
  llm_ready: boolean;
}

export interface SchemaResponse {
  schema_text: string;
  tables: string[];
}

export interface TableDetailResponse {
  table: string;
  rows: number;
  columns: number;
  preview: Record<string, unknown>[];
}

export type ChartSpec =
  | { chart: "bar"; x: string; y: string; title?: string }
  | { chart: "line"; x: string; y: string; title?: string }
  | { chart: "pie"; names: string; values: string; title?: string }
  | { chart: "none" };

export interface QueryResponse {
  question: string;
  sql: string;
  row_count: number;
  data: Record<string, unknown>[];
  summary: string;
  chart_spec: ChartSpec | null;
  error: string | null;
}

export const api = {
  health: () => axios.get<HealthResponse>(`${API_BASE}/health`),
  schema: () => axios.get<SchemaResponse>(`${API_BASE}/analytics/schema`),
  tables: () => axios.get<string[]>(`${API_BASE}/tables/`),
  tableDetail: (name: string, limit = 5) =>
    axios.get<TableDetailResponse>(`${API_BASE}/tables/${name}`, { params: { limit } }),
  query: (question: string) =>
    axios.post<QueryResponse>(`${API_BASE}/analytics/query`, { question }),
  refreshSchema: () => axios.post<{ message: string }>(`${API_BASE}/analytics/refresh-schema`),
};
