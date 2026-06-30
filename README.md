# Expense Tracker

A personal finance management web application that provides expense categorization, income and expense balance tracking, installment purchase management with bill forecasting, and budget limit goals with consumption alerts.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python · FastAPI · SQLAlchemy 2 · SQLite · Uvicorn |
| Frontend | Vite · React 19 · TypeScript · Tailwind CSS v4 |
| Backend tests | pytest · pytest-cov · httpx |
| Frontend tests | Vitest · React Testing Library · MSW |

---

## Running the application

You need **two terminals** — one for the backend and one for the frontend.

### 1 · Backend

```bash
cd app

# First time only — create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

pip install -r requirements.txt

# Start the development server (auto-reloads on file changes)
uvicorn main:app --reload
```

The API will be available at **http://localhost:8000**.  
Interactive docs (Swagger UI) at **http://localhost:8000/docs**.  
The SQLite database file (`financial.db`) is created automatically on first run.

> **Schema changes:** `create_all` only creates tables that don't exist yet — it won't alter existing ones.  
> Delete `financial.db` and restart the server whenever you change a model.

---

### 2 · Frontend

```bash
cd frontend

npm install          # first time only
npm run dev
```

Open **http://localhost:5173** in your browser.  
All `/api/*` requests are proxied to the backend at `http://localhost:8000` by Vite automatically — no CORS setup needed in development.

---

## Running the tests

### Backend tests

```bash
cd app
pytest                                           # all tests
pytest -v                                        # verbose output
pytest --cov=services --cov-report=term-missing  # service layer coverage
```

### Frontend tests

```bash
cd frontend
npm test                   # run all tests once
npm run test:watch         # watch mode (re-runs on file changes)
npm run test:coverage      # coverage report
```

---

## Project structure

```
app/                    Backend (FastAPI)
├── main.py             Entry point — creates app, tables, registers routers
├── requirements.txt
├── database/
├── models/             SQLAlchemy ORM models
├── schemas/            Pydantic v2 schemas
├── routers/            One file per resource group
├── services/
│   └── financial_service.py   Pure business logic (IO-free, fully unit-tested)
└── tests/
    ├── unit/           Tests for pure service functions
    └── integration/    HTTP endpoint tests (in-memory SQLite)

frontend/               Frontend (Vite + React + TypeScript)
├── src/
│   ├── api/            Typed API client functions (one file per resource)
│   ├── components/     Shared UI components
│   ├── context/        UserContext — selected user persisted in localStorage
│   ├── hooks/          useAsync — data-fetching hook
│   ├── lib/            Pure utilities (formatCurrency, formatMonthYear, …)
│   ├── pages/          One component per route, each with a *.test.tsx file
│   ├── test/           Vitest + MSW test setup
│   └── types/          TypeScript types mirroring backend schemas
└── vite.config.ts      Vitest config lives here alongside Vite config
```
