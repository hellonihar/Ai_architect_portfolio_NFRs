# Enterprise Process Fairness & Bias Dashboard

A full-stack application for monitoring fairness metrics, bias alerts, compliance status, and remediation actions in automated loan approval processes.

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend    │────▶│  PostgreSQL  │
│  React/Vite  │     │  FastAPI     │     │              │
│  Port 5173   │     │  Port 8000   │     │  Port 5432   │
└──────────────┘     └──────────────┘     └──────────────┘
       │                     │
       └───── /api/* ────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, TypeScript, Vite 6, Mantine UI 7, @mantine/charts (Recharts), React Router 7 |
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), AsyncPG, Pydantic 2 |
| **Database** | PostgreSQL 16 |
| **Tools** | uv (Python venv), npm |

## Database

6 tables under database `enterprise_fairness`:

| Table | Purpose |
|-------|---------|
| `loan_applications` | Raw applicant records with approval decisions (250 seed rows) |
| `fairness_metrics` | Computed metric values (fairness_index, disparate_impact, equalized_odds) |
| `bias_alerts` | Alerts triggered when metrics cross thresholds (4 severity levels) |
| `demographic_parity` | Per-group approval rates broken down by dimension (Gender, Region, Income) |
| `compliance_status` | Audit badge statuses with retraining requirements |
| `actions` | Remediation actions linked to alerts and compliance findings |

## Backend API

All endpoints are prefixed with `/api`.

### Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check, returns `{"status": "healthy"}` |

### Fairness
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/fairness/metrics` | Latest fairness metrics (up to 50, newest first) |
| GET | `/api/fairness/demographics?dimension=` | Demographic parity by group, optional `dimension` filter |
| GET | `/api/fairness/summary` | Aggregated dashboard summary (fairness_index, disparate_impact, equalized_odds, alert counts, compliance counts, group counts) |

### Alerts
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/alerts?severity=&status=` | Bias alerts with optional `severity` and `status` filters |
| GET | `/api/alerts/stats` | Alert counts grouped by severity (review, investigate, escalate) |
| PATCH | `/api/alerts/{id}/resolve` | Mark alert as Resolved |

### Compliance
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/compliance/status` | All compliance badges with audit dates and retraining flags |

### Actions
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/actions?status=` | Actions with optional `status` filter |
| POST | `/api/actions` | Create a new action (body: action_type, title, description, alert_id, assigned_to) |
| PATCH | `/api/actions/{id}/complete` | Mark action as Completed |

### Backend Project Structure
```
backend/
  app/
    main.py          — FastAPI app, CORS, router registration, health endpoint
    config.py        — Settings (database URL, app name, CORS origins)
    database.py      — Async SQLAlchemy engine, session factory, init_db
    models.py        — 6 ORM models (SQLAlchemy)
    schemas.py       — Pydantic request/response models
    routes/
      fairness.py    — /api/fairness/*
      alerts.py      — /api/alerts/*
      compliance.py  — /api/compliance/*
      actions.py     — /api/actions/*
  scripts/
    seed_data.py     — Populates all tables with sample data
```

## Frontend

4 pages, navigated via sidebar:

### Dashboard (`/`)
- Metric cards: Fairness Index, Disparate Impact, Equalized Odds, Open Alerts
- Bar chart: Approval rate by group with parity threshold line
- Ring progress: Fairness Index score visualization
- Group breakdown charts by dimension (Gender, Region, Income)
- Compliance badges and group count summary

### Bias Alerts (`/alerts`)
- Severity summary cards (Escalate, Investigate, Review counts)
- Tab filter: All / Escalate / Investigate / Review
- Alert table: severity badge, title, description, dimension, affected group, metric value, status
- Resolve button to close open alerts
- Toast notifications on resolve

### Compliance (`/compliance`)
- Status summary cards (Passed, Failed, In Progress counts)
- Badge table: badge name, status, description, last/next audit dates, retraining requirement
- Retraining timeline section for badges requiring retraining

### Actions (`/actions`)
- Type summary cards (Investigate, Escalate, Update Data/Reports counts)
- Action table: type badge, title, assigned_to, status, created date
- Complete button for in-progress/pending actions
- Create Action modal: type select, title, description, assigned_to
- Toast notifications on create/complete

### Frontend Project Structure
```
frontend/
  src/
    main.tsx                 — Entry point, MantineProvider, BrowserRouter
    App.tsx                  — AppShell layout, sidebar nav, routes, ErrorBoundary
    theme.ts                 — Mantine theme customization
    global.css               — Base CSS reset (scrollbar, body margin)
    api/
      client.ts              — Typed fetch API client with all endpoint methods
    components/
      ErrorBoundary.tsx      — React error boundary wrapping all routes
      ChartContainer.tsx     — ResizeObserver-based chart wrapper (fixes Recharts blank-on-scroll)
    pages/
      Dashboard.tsx          — Main overview with metrics, bar chart, ring progress
      Alerts.tsx             — Bias alerts with tabs, table, and resolve action
      Compliance.tsx         — Compliance badges with retraining timeline
      Actions.tsx            — Action tracker with create modal and complete action
```

### Vite Proxy
Vite proxies `/api/*` to `http://localhost:8000` so the frontend never calls the backend directly.

## Setup & Operations

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 16 running on localhost:5432

### 1. Database

Create the database and user:

```sql
CREATE USER fairness_user WITH PASSWORD 'fairness_pass';
CREATE DATABASE enterprise_fairness OWNER fairness_user;
```

Apply the schema:

```bash
psql -U fairness_user -d enterprise_fairness -f db/init.sql
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
python scripts/seed_data.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend starts at **http://localhost:8000**. API docs at **http://localhost:8000/docs**.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend starts at **http://localhost:5173**.

### Verify Health

```bash
curl http://localhost:8000/api/health
# → {"status": "healthy", "app": "Enterprise Fairness & Bias Dashboard"}
```

## Known Issues & Fixes

### Pydantic v2 Decimal Serialization
PostgreSQL `DECIMAL` columns arrive as Python `Decimal` objects. Pydantic v2 serializes `Decimal` as a string in JSON, which causes `toFixed()` calls in JavaScript to fail. **Fixed by** using `float` type hints in Pydantic schemas instead of `Decimal`.

### Recharts Blank on Scroll
`ResponsiveContainer` from Recharts becomes confused during scroll in Mantine's AppShell, rendering at zero dimensions. **Fixed by** replacing with a custom `ChartContainer` component using native `ResizeObserver`, and switching to `@mantine/charts` BarChart.

### Navigation Crash
Calling `api.compliance()` and `api.actions()` as functions (TypeError) crashed the React tree because `.compliance` and `.actions` are namespace objects with `.list()`, `.create()`, etc. **Fixed by** calling the correct methods (`.list()`, `.create()`, `.complete()`) and wrapping routes in an `ErrorBoundary`.
