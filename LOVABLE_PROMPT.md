# Lovable Frontend Prompt — Loyalty Analytics Agent

Paste everything below this line into Lovable as your prompt.

---

## BACKEND API CONTRACT (read this first — all data shapes are defined here)

The React app connects to a FastAPI backend running at `http://localhost:8000`.

### Endpoint 1 — Health Check
```
GET http://localhost:8000/health
```
Response:
```json
{
  "status": "ok",
  "db_connected": true,
  "llm_ready": true
}
```

### Endpoint 2 — Schema
```
GET http://localhost:8000/analytics/schema
```
Response:
```json
{
  "schema_text": "Table: transactions_us\nColumns: date_of_transaction (timestamp), loyalty_id (bigint), points (double precision), ...\n\nTable: loyalty_accounts_us\nColumns: loyalty_id (bigint), tier (text), current_tier_points (double precision), ...",
  "tables": [
    "transactions_us",
    "loyalty_accounts_us",
    "loyalty_affiliations_us",
    "credit_sales_us",
    "sales_us",
    "transactions_ca",
    "loyalty_accounts_ca",
    "loyalty_affiliations_ca",
    "sales_ca",
    "credit_sales_ca"
  ]
}
```

### Endpoint 3 — Table Detail
```
GET http://localhost:8000/tables/{table_name}?limit=10
```
Example: `GET http://localhost:8000/tables/transactions_us?limit=5`

Response:
```json
{
  "table": "transactions_us",
  "rows": 35000,
  "columns": 70,
  "preview": [
    {
      "date_of_transaction": "2022-07-14T00:00:00",
      "loyalty_id": 201642,
      "points": 4.0,
      "transaction_status": "Processed",
      "type": "Earn",
      "rule_description": "Rewards Base Pts",
      "extended_sales_amount": 2.86,
      "loyalty_organization_name": "Henry Schein Dental",
      "tier_ratio": 1.5
    }
  ]
}
```

### Endpoint 4 — List Tables
```
GET http://localhost:8000/tables/
```
Response:
```json
[
  "transactions_us",
  "loyalty_accounts_us",
  "loyalty_affiliations_us",
  "credit_sales_us",
  "sales_us",
  "transactions_ca",
  "loyalty_accounts_ca",
  "loyalty_affiliations_ca",
  "sales_ca",
  "credit_sales_ca"
]
```

### Endpoint 5 — Natural Language Query (MAIN ENDPOINT)
```
POST http://localhost:8000/analytics/query
Content-Type: application/json

Body:
{
  "question": "Who are the top 10 customers by total points earned?"
}
```

Response (success with data):
```json
{
  "question": "Who are the top 10 customers by total points earned?",
  "sql": "SELECT loyalty_id, SUM(points) AS total_points FROM transactions_us GROUP BY loyalty_id ORDER BY total_points DESC LIMIT 10",
  "row_count": 10,
  "data": [
    { "loyalty_id": 201642, "total_points": 98432.0 },
    { "loyalty_id": 207080, "total_points": 87211.0 }
  ],
  "summary": "The top customer by total points earned is loyalty ID 201642 with 98,432 points...",
  "chart_spec": {
    "chart": "bar",
    "x": "loyalty_id",
    "y": "total_points",
    "title": "Top 10 Customers by Total Points"
  },
  "error": null
}
```

Response (out of scope question):
```json
{
  "question": "Who is Batman?",
  "sql": "NO_DATA",
  "row_count": 0,
  "data": [],
  "summary": "That question doesn't relate to the Loyalty database. Try asking about transactions, members, points, tiers, or sales.",
  "chart_spec": null,
  "error": null
}
```

Response (SQL error):
```json
{
  "question": "...",
  "sql": "SELECT ...",
  "row_count": 0,
  "data": [],
  "summary": "",
  "chart_spec": null,
  "error": "SQL execution failed: column does not exist"
}
```

chart_spec can be one of:
```json
{ "chart": "bar",  "x": "column_name", "y": "column_name", "title": "Chart Title" }
{ "chart": "line", "x": "column_name", "y": "column_name", "title": "Chart Title" }
{ "chart": "pie",  "names": "column_name", "values": "column_name", "title": "Chart Title" }
{ "chart": "none" }
```

### Endpoint 6 — Refresh Schema
```
POST http://localhost:8000/analytics/refresh-schema
```
Response:
```json
{ "message": "Schema refreshed. 10 tables found." }
```

---

## THE APP TO BUILD

Build a full React + TypeScript single-page application called **"Loyalty Analytics Agent"** that is a conversational AI analytics dashboard. Use Tailwind CSS for styling. Use Recharts for all charts. Use axios for API calls.

### Overall Layout

Two-column layout:
- **Left sidebar** — fixed width 280px, dark background `#0f1117`
- **Main content area** — takes remaining width, dark background `#13151f`

The entire app uses a dark theme. Background `#13151f`, card backgrounds `#1a1d27`, borders `#2a2d3a`, text white/gray.

---

### LEFT SIDEBAR

#### Header
- Diamond emoji 💎 followed by bold text "Loyalty Analytics"
- Below it a thin horizontal divider

#### API Status Card
On mount, call `GET /health`. Show:
- A green pill badge "✅ API Online" if `status === "ok"`
- A red pill badge "❌ API Offline" if the call fails
- Below that, two small metric chips side by side:
  - "Database" with green ✅ or red ❌ based on `db_connected`
  - "LLM" with green ✅ or red ❌ based on `llm_ready`
- If offline, show a code block: `uvicorn backend.main:app --reload --port 8000`

#### Schema Section
- Section heading "🗄️ Schema"
- A collapsible accordion panel labelled "View full schema"
- Inside: a scrollable `<pre>` block showing `schema_text` from `GET /analytics/schema`
- Monospace font, small text, max height 300px with overflow scroll

#### Tables Section
- Section heading "📋 Tables"
- A `<select>` dropdown populated with the `tables` array from `GET /analytics/schema`
- Default option "— select a table —"
- When a table is selected, call `GET /tables/{table_name}?limit=5`
- Show an expandable card below the dropdown with:
  - Table name as heading in backtick code style
  - A scrollable data grid showing the preview rows (columns as headers, rows as cells)
  - Below the grid: "Rows: **{rows}** · Columns: **{columns}**" in small gray text

#### Settings Section
- Section heading "⚙️ Settings"
- Three toggle switches (boolean state, default all ON):
  - "Show generated SQL"
  - "Show raw data table"
  - "Auto-generate chart"
- A "🗑️ Clear chat history" button — full width, outlined style, clears the chat messages array in state

#### Footer
- Small gray text showing:
  - `SQL model: llama-3.3-70b-versatile`
  - `Polish model: llama-3.1-8b-instant`
  - `Row limit: 50`

---

### MAIN CONTENT AREA

#### Page Header
- Large heading: "💎 Loyalty Data Analytics Agent"
- Subtitle paragraph: "Ask anything about your loyalty data in plain English. The agent converts your question into SQL, runs it, and explains the results."
- Thin horizontal divider

#### Example Prompts Row
- Small label "💡 Try an example:"
- A 3-column grid of clickable pill buttons. When clicked, the text is placed into the chat input and submitted automatically. The 6 examples are:
  1. "Who are the top 10 customers by total points earned?"
  2. "How many Gold, Silver, and Bronze tier members are there?"
  3. "What are the total points earned per month in 2024?"
  4. "Show me the top 5 products by extended sales amount"
  5. "Which loyalty organizations have the most active members?"
  6. "What is the average points per transaction by tier?"

#### Chat History Area
- Scrollable area that grows as messages are added
- Auto-scrolls to bottom on new message
- Each message is a chat bubble:

**User bubble** (right-aligned):
- Light blue/indigo background `#3b5bdb`
- Rounded corners, max width 70%
- White text

**Assistant bubble** (left-aligned):
- Dark card background `#1a1d27`
- Border `#2a2d3a`
- Rounded corners, max width 90%
- Contains in order (each section only shown if the relevant toggle is ON and data exists):

  1. **SQL Block** (if "Show generated SQL" toggle is ON and sql is not "NO_DATA"):
     - Collapsible accordion, default OPEN for the latest message, CLOSED for history
     - Header: "🛠️ Generated SQL"
     - Inside: syntax-highlighted code block with dark background, the SQL string

  2. **Data Table** (if "Show raw data table" toggle is ON and data.length > 0):
     - Collapsible accordion, default OPEN for latest, CLOSED for history
     - Header: "📊 Raw Data ({row_count} rows)"
     - Inside: a scrollable table with sticky headers, max height 300px
     - Column headers from Object.keys(data[0])
     - Rows from data array
     - Alternating row background colors

  3. **Chart** (if "Auto-generate chart" toggle is ON and chart_spec.chart !== "none" and chart_spec is not null):
     - Rendered inline, no accordion wrapper
     - If chart_spec.chart === "bar": render a Recharts `<BarChart>` with `XAxis dataKey={chart_spec.x}`, `YAxis`, `Bar dataKey={chart_spec.y}`, `Tooltip`, `CartesianGrid`
     - If chart_spec.chart === "line": render a Recharts `<LineChart>` with `XAxis dataKey={chart_spec.x}`, `YAxis`, `Line dataKey={chart_spec.y}`, `Tooltip`, `CartesianGrid`
     - If chart_spec.chart === "pie": render a Recharts `<PieChart>` with `Pie dataKey={chart_spec.values}` and `nameKey={chart_spec.names}`, with `Tooltip` and `Legend`
     - All charts: dark background, white axis labels, colour palette `["#4F8EF7", "#F7874F", "#4FF7A0", "#F74F6E", "#A04FF7", "#F7D44F"]`
     - Chart title from `chart_spec.title` shown above the chart in small bold text
     - Height 280px, width 100%

  4. **Summary text** — always shown
     - The `summary` string rendered as plain paragraph text
     - If `error` is not null, show the error in a red alert box instead

**Loading state** — while waiting for the API response, show a pulsing assistant bubble with:
- Three animated dots "🧠 Analysing…"
- A step-by-step status list that animates through:
  - "📝 Generating SQL query…"
  - "⚡ Running query on PostgreSQL…"
  - "✍️ Writing summary…"
  - "📈 Generating chart…"
- Each step appears with a 600ms delay after the previous one

#### Chat Input Bar
- Sticky to the bottom of the main content area
- Full-width text input with placeholder "Ask a question about the Loyalty Data…"
- A send button (arrow icon) to the right
- Submit on Enter key or button click
- Disabled while a request is in flight
- On submit:
  1. Add user message to chat history
  2. Add loading bubble to chat history
  3. Call `POST /analytics/query` with `{ "question": userInput }`
  4. Replace loading bubble with the assistant response bubble
  5. Clear the input field

---

### STATE MANAGEMENT

Use React `useState` and `useEffect`. No external state library needed.

```typescript
interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string        // user text OR summary text
  sql?: string
  rowCount?: number
  data?: Record<string, any>[]
  chartSpec?: {
    chart: 'bar' | 'line' | 'pie' | 'none'
    x?: string
    y?: string
    names?: string
    values?: string
    title?: string
  } | null
  error?: string | null
  isLoading?: boolean
}

interface AppState {
  messages: Message[]
  health: { status: string; db_connected: boolean; llm_ready: boolean } | null
  schema: { schema_text: string; tables: string[] } | null
  selectedTable: string
  tableDetail: { table: string; rows: number; columns: number; preview: Record<string, any>[] } | null
  settings: {
    showSQL: boolean
    showRawData: boolean
    showChart: boolean
  }
  isQuerying: boolean
}
```

---

### API CONFIGURATION

Create a file `src/api/client.ts`:

```typescript
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

export const api = {
  health: () => axios.get(`${API_BASE}/health`),
  schema: () => axios.get(`${API_BASE}/analytics/schema`),
  tables: () => axios.get(`${API_BASE}/tables/`),
  tableDetail: (name: string, limit = 5) =>
    axios.get(`${API_BASE}/tables/${name}`, { params: { limit } }),
  query: (question: string) =>
    axios.post(`${API_BASE}/analytics/query`, { question }),
  refreshSchema: () =>
    axios.post(`${API_BASE}/analytics/refresh-schema`),
}
```

---

### STYLING TOKENS

```
Background:        #13151f
Sidebar bg:        #0f1117
Card bg:           #1a1d27
Border:            #2a2d3a
Text primary:      #ffffff
Text secondary:    #8b8fa8
Text muted:        #4a4d5e
Accent blue:       #4F8EF7
Accent orange:     #F7874F
Accent green:      #4FF7A0
User bubble:       #3b5bdb
Success green:     #2d9e5f
Error red:         #e03131
Font:              Inter, system-ui, sans-serif
Code font:         JetBrains Mono, Fira Code, monospace
Border radius:     10px (cards), 20px (bubbles), 6px (buttons)
```

---

### ADDITIONAL REQUIREMENTS

1. On app mount, call both `/health` and `/analytics/schema` in parallel using `Promise.all`
2. The schema dropdown and table explorer should show a skeleton loader while fetching
3. All API errors should show a toast notification in the top-right corner (red background, auto-dismiss after 4 seconds)
4. The chat area should have a subtle gradient at the top fading to transparent to indicate scrollability
5. Empty state: when there are no messages yet, show a centered hero section with the 💎 emoji large, the app name, and the subtitle text
6. All accordions use smooth CSS transitions (max-height animation)
7. The data table columns should be truncated with ellipsis if too long, with full value shown on hover via title attribute
8. Numbers in the data table should be right-aligned
9. Add a "Refresh Schema" button next to the Schema section heading that calls `POST /analytics/refresh-schema` and then re-fetches the schema
10. The selected table in the dropdown should persist in state so it doesn't reset when a new chat message arrives

---

### PACKAGE DEPENDENCIES NEEDED

```json
{
  "dependencies": {
    "axios": "^1.6.0",
    "recharts": "^2.12.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0"
  }
}
```

---

### IMPORTANT NOTES FOR LOVABLE

- The backend runs locally at `http://localhost:8000` — hardcode this as the API base URL
- CORS is already enabled on the backend (`allow_origins=["*"]`) so no proxy is needed
- All chart data comes directly from the `data` array in the query response — pass it directly to Recharts
- The `chart_spec` tells you exactly which column to use for each axis — use `chart_spec.x` as the `dataKey` for XAxis, `chart_spec.y` as the `dataKey` for Bar/Line
- For pie charts use `chart_spec.names` as `nameKey` and `chart_spec.values` as `dataKey`
- Dates in the data array come as ISO strings like `"2022-07-14T00:00:00"` — display them as-is or format with `.split('T')[0]`
- Null values in data rows come as JSON `null` — display as empty string in the table
- The `sql` field will be the string `"NO_DATA"` when the question is out of scope — in that case hide the SQL block entirely
