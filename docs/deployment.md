# PromptLab Deployment Guide

This guide explains how a new developer can deploy PromptLab from a
fresh clone. PromptLab consists of two independently deployable parts:

- **Backend** - a FastAPI application (Python 3.10+) serving the REST
  API on port 8000.
- **Frontend** - a React SPA (Vite) that builds to static files in
  `frontend/dist/`.

Both can run on the same host or on separate hosts. The only coupling
is a single build-time environment variable (`VITE_API_BASE_URL`) that
tells the frontend where the backend lives.

---

## 1. Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Git | any recent | Clone the repository |
| Python | 3.10 or higher | Run the backend |
| pip | bundled with Python | Install backend dependencies |
| Node.js | 18 or higher | Build the frontend |
| npm | 10 or higher | Install/build frontend dependencies |
| Docker (optional) | any recent | Containerized deployment alternative |

---

## 2. Repository setup

```bash
git clone <your-repo-url>
cd 10x-engineer-project-repo
```

The repository root contains:

```
10x-engineer-project-repo/
+-- backend/          # FastAPI application
+-- frontend/         # React + Vite SPA
+-- docs/             # Documentation (you are here)
+-- specs/            # Feature specifications
+-- docker-compose.yml # Docker Compose (backend only - optional)
+-- config.yaml
+-- pyproject.toml
+-- README.md
```

---

## 3. Backend setup

All backend commands run from the `backend/` directory.

### 4. Backend install command

Create a virtual environment and install dependencies:

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment:

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

The pinned dependencies are:

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.109.0 | Web framework |
| uvicorn | 0.27.0 | ASGI server |
| pydantic | 2.5.3 | Data validation |
| pytest | 7.4.4 | Testing (optional for deployment) |
| pytest-cov | 4.1.0 | Test coverage (optional for deployment) |
| httpx | 0.26.0 | HTTP client for tests (optional for deployment) |

### 5. Backend start command (local development)

```bash
python main.py
```

This runs `uvicorn` on `0.0.0.0:8000` with auto-reload enabled
(`reload=True`), which is ideal for local development.

The API is now available at `http://localhost:8000`.

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health check:** http://localhost:8000/health

### 6. Backend deployment configuration

The backend has no external configuration files, no database, and no
application-level environment variables. All application settings are
code-level defaults:

| Setting | Value | Location |
|---------|-------|----------|
| Host | `0.0.0.0` | `backend/main.py`, `backend/Dockerfile` |
| Port | `8000` | `backend/main.py`, `backend/Dockerfile` |
| CORS | `allow_origins=["*"]` | `backend/app/api.py` |
| Storage | In-memory (see section 16) | `backend/app/storage.py` |

#### Production start command

The FastAPI application object is exposed from `app.api:app`. For a
production deployment, start the server without auto-reload and bind
to the port provided by the hosting platform:

```bash
uvicorn app.api:app --host 0.0.0.0 --port $PORT
```

On platforms like Render, `$PORT` is injected automatically. On a VPS
or local machine, replace `$PORT` with the desired port number (e.g.
`8000`).

> **Do not use `uvicorn main:app` for production.** `main.py` is a
> local development entry point that hardcodes `reload=True`. The
> production ASGI app is `app.api:app`.

---

## 7. Frontend setup

All frontend commands run from the `frontend/` directory.

```bash
cd frontend
npm install
```

### 8. Frontend build command

```bash
npm run build
```

This produces static files in `frontend/dist/`:

```
dist/
+-- index.html
+-- assets/
    +-- index-<hash>.css
    +-- index-<hash>.js
```

To preview the production build locally:

```bash
npm run preview
```

To run the Vite dev server (hot reload, defaults to
`http://localhost:5173`):

```bash
npm run dev
```

### 9. Frontend deployment configuration

The frontend is a standard Vite SPA. After `npm run build`, the
`dist/` directory can be served by any static host.

> **Important - SPA fallback:** The frontend uses client-side routing
> (React Router). The host must serve `index.html` for all routes
> that do not match a static file, otherwise deep links like
> `/prompts/123` will return a 404. With nginx, add:
>
> ```nginx
> location / {
>   try_files $uri $uri/ /index.html;
> }
> ```
>
> On Render Static Sites, configure a redirect rule in the dashboard:
>
> | Field | Value |
> |------|-------|
> | **Source** | `/*` |
> | **Destination** | `/index.html` |
> | **Action** | **Rewrite** |
>
> This rewrite is required so that direct or deep links such as
> `/prompts/123` continue to work when the page is refreshed or
> opened directly in the browser.

---

## 10. Required environment variables

PromptLab requires exactly **one** environment variable:

| Variable | Scope | Required | Default | Description |
|----------|-------|----------|---------|-------------|
| `VITE_API_BASE_URL` | Frontend (build-time) | Yes for deployment | `http://localhost:8000` | The public URL of the backend API |

The backend application requires **no** environment variables. It has
no database URL, no API keys, and no authentication secrets. The only
Render-specific variable is `PYTHON_VERSION`, which is a Render runtime
configuration (see [section 13](#13-primary-deployment---render)), not
an application variable.

### 11. Where VITE_API_BASE_URL is configured

`VITE_API_BASE_URL` is a Vite build-time environment variable. It is
read in two places in the frontend source:

1. **`frontend/src/api/client.js`** - the shared API client that all
   feature modules (`prompts.js`, `collections.js`) use for every
   request:
   ```js
   const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
   ```

2. **`frontend/src/components/Header.jsx`** - the global health-check
   indicator that polls `GET /health`:
   ```js
   const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
   ```

Because Vite inlines environment variables at build time, the value
must be set **before** running `npm run build`. It cannot be changed at
runtime after the build.

#### How to set it

**Local development (`.env` file in `frontend/`):**

A template is provided in `frontend/.env.example`:

```
VITE_API_BASE_URL=http://localhost:8000
```

Copy it to create your local `.env`:

```bash
cp frontend/.env.example frontend/.env
```

**Production build (shell environment variable):**

```bash
# Linux / macOS
export VITE_API_BASE_URL=https://your-backend.onrender.com
npm run build
```

```powershell
# Windows (PowerShell)
$env:VITE_API_BASE_URL="https://your-backend.onrender.com"
npm run build
```

**Render Static Site (dashboard environment variable):**

Set `VITE_API_BASE_URL` in the Render dashboard under
**Environment** > **Environment Variables** for the frontend static
site. Render injects it automatically at build time.

---

## 12. Secret / credential handling

PromptLab currently has **no secrets or credentials**:

- The backend has **no authentication** - all endpoints are publicly
  accessible. No API keys, tokens, or passwords are required.
- No database connection strings exist (storage is in-memory).
- The root-level `config.yaml` is not referenced by any application
  code.

#### `.env` files and `.gitignore`

The repository's `frontend/.gitignore` already contains the following
rules:

```gitignore
.env
.env.*
!.env.example
```

These rules ignore `.env` and all environment-specific variants
(`.env.local`, `.env.production`, etc.) so they are never committed
accidentally. The `!.env.example` negation keeps `.env.example`
tracked so other developers can discover the required variable.

**`.env` files must never be committed to the repository.** Only
`.env.example` (which contains no secrets) is committed.

If authentication or a database is added in the future, secrets
should be supplied through environment variables or the hosting
platform's secret management - **never** committed to the repository.

---

## 13. Primary deployment - Render

The recommended deployment path is [Render](https://render.com), which
supports both the FastAPI backend and the static frontend as separate
services. The two services are fully independent and can be deployed
in either order.

### Backend - Render Web Service

| Setting | Value |
|---------|-------|
| **Service type** | Web Service |
| **Root directory** | `backend` |
| **Runtime** | Python |
| **Python version** | 3.12.11 |
| **Build command** | `pip install -r requirements.txt` |
| **Start command** | `uvicorn app.api:app --host 0.0.0.0 --port $PORT` |

#### Backend environment variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `PYTHON_VERSION` | `3.12.11` | Render backend runtime configuration - tells Render which Python version to use for the build and runtime |

Render injects `$PORT` automatically. The start command uses
`app.api:app` (the ASGI application object), not `main:app` (which is
a local dev entry point with `reload=True`).

> **Note:** `PYTHON_VERSION` is a Render runtime configuration
> variable for the backend service. It is unrelated to
> `VITE_API_BASE_URL`, which is the frontend application environment
> variable that tells the SPA where the backend API is hosted. These
> two variables are set on different Render services.

### Frontend - Render Static Site

| Setting | Value |
|---------|-------|
| **Service type** | Static Site |
| **Root directory** | `frontend` |
| **Build command** | `npm install && npm run build` |
| **Publish directory** | `dist` |
| **Environment variables** | `VITE_API_BASE_URL` = backend URL (e.g. `https://your-backend.onrender.com`) |

Set `VITE_API_BASE_URL` in the Render dashboard under the static
site's **Environment** > **Environment Variables**. Render injects it
at build time so Vite can inline it into the bundle.

For React Router deep links to work on Render Static Sites, configure
a rewrite rule as described in [section 9](#9-frontend-deployment-configuration)
(Source: `/*`, Destination: `/index.html`, Action: Rewrite).

---

## 14. Optional deployment - Docker

Docker is provided as an alternative for local development or
self-hosted deployments. The included `Dockerfile` (in `backend/`)
containerizes the backend only; no frontend Dockerfile is included.

#### Backend container

A `Dockerfile` is included in `backend/`:

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

To build and run the backend container:

```bash
docker build -t promptlab-backend ./backend
docker run -p 8000:8000 promptlab-backend
```

Or use Docker Compose from the repository root (includes the
`PYTHONUNBUFFERED=1` environment variable):

```bash
docker compose up --build
```

> **Note:** The included `docker-compose.yml` defines only the
> backend service and the Dockerfile CMD uses `--reload` for
> development. For a production container, remove `--reload` from the
> CMD and use `app.api:app` instead of `main:app`.

#### Frontend

No frontend Dockerfile is included. After `npm run build`, serve the
`dist/` directory with any static host or an external web server
(e.g. nginx) with SPA fallback.

---

## 15. How to verify the deployed backend

### Health check

```bash
curl https://your-backend.onrender.com/health
```

Expected response:

```json
{"status": "healthy", "version": "0.1.0"}
```

### List prompts

```bash
curl https://your-backend.onrender.com/prompts
```

Expected response (empty list on a fresh server):

```json
{"prompts": [], "total": 0}
```

### Interactive API docs

Open `https://your-backend.onrender.com/docs` in a browser to access
the Swagger UI.

---

## 16. How to verify the deployed frontend

1. Open the deployed frontend URL in a browser.
2. The **Prompt List** page should load, showing the dark SaaS
   dashboard shell with a sidebar and header.
3. The **header** displays a green health indicator dot (top-right)
   when the backend health check succeeds. A red dot means the
   frontend cannot reach the backend - verify `VITE_API_BASE_URL`
   was set correctly at build time and that the backend is running.
4. If no prompts exist, the **empty state** message "No prompts yet.
   Create your first prompt." should be displayed.

---

## 17. End-to-end verification checklist

Run through the following checklist to confirm the full CRUD flow and
UX states work across the deployed frontend and backend.

### CRUD operations

- [ ] **List prompts** - The prompt list page loads and displays all
      prompts as cards (or the empty state if none exist).
- [ ] **View detail** - Clicking **View** on a prompt card opens the
      detail page showing title, content, tags, timestamps, and
      collection.
- [ ] **Create** - Clicking **New Prompt** opens the form; filling in
      title + content and clicking **Save** creates the prompt and
      redirects to the list with the new card visible.
- [ ] **Edit** - On the detail page, clicking **Edit** opens the
      pre-filled form; changing fields and saving redirects to the
      detail page with updated values and a refreshed "Updated"
      timestamp.
- [ ] **Delete with confirmation** - Clicking **Delete** on a prompt
      card opens a confirmation dialog. Clicking **Cancel** keeps the
      prompt; clicking **Confirm** removes it from the list.

### Collections

- [ ] **Collections** - Navigating to Collections shows the collection
      list and a create form.
- [ ] **Collection filtering** - On the prompt list, selecting a
      collection from the filter dropdown narrows the prompt list to
      that collection. Changing back to "All Collections" shows all.
- [ ] **Collection assignment** - Creating or editing a prompt and
      selecting a collection from the dropdown assigns it; the
      detail page shows the collection name.
- [ ] **Collection delete** - Deleting a collection unassigns its
      prompts (sets `collection_id` to null) rather than deleting
      them; the prompts remain visible in the list.

### Search and filtering

- [ ] **Search** - Typing in the search box filters prompts by
      case-insensitive match on title and description. Clearing the
      search restores the full list.
- [ ] **Tag filter** - Typing a tag in the tag filter box narrows the
      list to prompts carrying that exact tag.
- [ ] **Combined filters** - Search + collection + tag filters can be
      combined; the "Clear Filters" button (shown in the empty state
      when filters are active) resets all filters.

### UX states

- [ ] **Loading states** - A spinner appears while data is being
      fetched (initial load, filter change, retry, delete).
- [ ] **Empty states** - When no prompts exist: "No prompts yet.
      Create your first prompt." When filters match nothing: "No
      prompts match your filters." with a "Clear Filters" button.
      When no collections exist: "No collections yet. Create one to
      organize your prompts."
- [ ] **Visible API errors** - If the backend is unreachable, an
      error banner with a **Retry** button appears. If a create/edit
      fails validation, field-level error messages appear below the
      relevant input. If a delete fails (e.g. 404), an error banner
      appears at the top of the page.

---

## 18. Known limitations

### In-memory storage (data is lost on restart)

The backend uses an in-memory storage layer
(`backend/app/storage.py`). All prompts, collections, and version
history are stored in Python dictionaries inside the server process.
**All data is lost when the server restarts.**

The storage layer is isolated behind a `Storage` class so it can be
swapped for a database-backed implementation in the future, but the
current deployment has no persistent storage.

### No authentication

The backend has no authentication or authorization. All endpoints are
publicly accessible. Do not expose the API to the public internet
without adding an authentication layer first.

### CORS allows all origins

The backend's CORS configuration allows requests from any origin
(`allow_origins=["*"]`). This is suitable for development and for a
frontend deployed to any static host, but it means any website can
make requests to the API. If authentication is added, this should be
tightened to specific origins.

### `VITE_API_BASE_URL` is build-time only

Because Vite inlines environment variables at build time, the API base
URL is baked into the frontend bundle. Changing the backend URL after
building the frontend requires a rebuild. Plan the backend URL before
building the frontend for deployment.

### No frontend Dockerfile

The repository includes a `Dockerfile` for the backend but not for
the frontend. The frontend is deployed as static files (`npm run
build` -> `dist/`) to a static host. No containerization is provided
for the frontend.

### Docker Compose is backend-only

The included `docker-compose.yml` defines only the backend service
and uses the `--reload` flag for development. It does not include a
frontend service.
