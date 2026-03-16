# Copilot Instructions (Milk SaaS)

This repository contains two main apps:

- **`backend/`**: FastAPI + SQLAlchemy app with PostgreSQL. Auth is JWT-based (OAuth2 password flow).
- **`frontend/`**: Next.js (App Router) React app with client-side auth and Axios for API calls.

---

## 📦 Architecture & Data Flow (Big Picture)

- **Tenant model**: Every request is scoped to a `Farm` (the authenticated user) via `get_current_farm` (see `backend/app/api/deps.py`).
- **Backend boundaries**:
  - API routers live under `backend/app/api/routers/`.
  - Models in `backend/app/models/__init__.py` map to PostgreSQL tables.
  - Schemas are in `backend/app/schemas/` and mostly follow Pydantic v2 (uses `ConfigDict(from_attributes=True)`).
  - No migrations: schema is created on startup via `Base.metadata.create_all(bind=engine)` in `backend/app/main.py`.
- **Frontend boundaries**:
  - Routes are in `frontend/src/app/` (Next.js app router).
  - Auth is global via `frontend/src/contexts/AuthContext.tsx`.
  - API client is `frontend/src/lib/api.ts` and points to `http://localhost:8000`.

---

## 🔧 Development / Run Workflow (must know)

### Backend
1. Ensure Postgres is running and reachable at `DATABASE_URL`.
2. Activate the venv and install dependencies:
   ```powershell
   cd backend
   .\venv313\Scripts\Activate
   pip install -r requirements.txt
   ```
3. Run the API server:
   ```powershell
   uvicorn app.main:app --reload
   ```
4. If the backend fails at startup, it is usually a DB connection issue (see `backend/database.py` and `.env`).

### Frontend
1. From `frontend`:
   ```bash
   npm install
   npm run dev
   ```
2. The frontend expects the backend at `http://localhost:8000` (see `frontend/src/lib/api.ts`).

---

## 🔗 Integration Patterns & Conventions

- **Auth flow**:
  - Frontend stores JWT in `localStorage` under `token`.
  - `AuthProvider` sets `api.defaults.headers.common.Authorization` and redirects to `/login` if the token is invalid.
  - Backend uses `OAuth2PasswordBearer(tokenUrl="/auth/token")` and expects `sub` claim to be the `Farm.id`.

- **CRUD endpoints**:
  - Use `model_dump(exclude_unset=True)` to apply partial updates (see `backend/app/api/routers/animals.py` and others).
  - Access is always filtered by `current_farm.id`.

- **Router order matters**:
  - For example, `backend/app/api/routers/milk.py` defines `/dashboard` before `/{milk_id}` to avoid routing conflicts.

- **UUIDs**:
  - All primary keys are UUIDs (see `backend/app/models/__init__.py`). Frontend transports IDs as strings.

---

## 🧠 What an AI agent should know first

- This is a **tenant-scoped app**: every request is tied to a `Farm`; tables are always filtered by `farm_id` (see `backend/app/api/deps.py`).
- The backend is a **standalone FastAPI service**; the frontend is a **Next.js app** calling it via `http://localhost:8000`.
- The backend **does not use migrations**; schemas are created on startup via `Base.metadata.create_all(...)` in `backend/app/main.py`.
- New frontend pages must match backend endpoint shapes (e.g., `/milk`, `/finance`) and use the shared auth flow.

---

## 🧪 Important gaps to keep in mind

- No automated tests are present.
- No CI config / linting rules.
- Backend requires a running Postgres instance reachable via `DATABASE_URL` (see `backend/.env`).

---

> When in doubt, point to the exact file that owns the behavior (e.g., `frontend/src/contexts/AuthContext.tsx` for auth, or `backend/app/api/endpoints/auth.py` for token flow).
