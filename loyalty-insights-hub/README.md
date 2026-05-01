# loyalty-insights-hub

React + TypeScript frontend for the Loyalty Analytics Agent.

Built with Lovable. Connects to the FastAPI backend at `http://localhost:8000`.

## Stack
- React 18 + TypeScript
- Tailwind CSS
- Recharts (bar, line, pie charts)
- Axios (API calls)

## Setup

```bash
cd loyalty-insights-hub
npm install
npm run dev
```

Opens at: http://localhost:5173

## Backend must be running first

```bash
# From project root
.venv\Scripts\uvicorn.exe backend.main:app --reload --port 8000
```

See the root [SETUP.md](../SETUP.md) for full instructions.
