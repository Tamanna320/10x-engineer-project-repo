# Frontend Specification: PromptLab UI

| Field           | Value                                                                                          |
| --------------- | ---------------------------------------------------------------------------------------------- |
| Feature         | React + Vite frontend for the PromptLab API                                                    |
| Status          | Draft — ready for implementation                                                               |
| Target release  | 0.2.0 (current API version: 0.1.0)                                                             |
| Source of truth | `backend/app/api.py`, `backend/app/models.py`, `docs/API_REFERENCE.md`, `README.md`, `specs/`   |
| Module          | Module 4 — Task 4.1                                                                            |

---

## 1. Screens and Purpose

| Screen             | Route               | Purpose                                                                                                   |
| ------------------ | ------------------- | --------------------------------------------------------------------------------------------------------- |
| Prompt List        | `/`                 | Browse, search, and filter prompts by tag or collection; delete prompts; navigate to detail, create, or edit. |
| Prompt Detail      | `/prompts/:id`       | View a single prompt's full content, tags, and collection; test template rendering; view version history and restore a version; delete the prompt. |
| Prompt Form (Create) | `/prompts/new`     | Fill in title, content, description, collection, and tags to create a new prompt via `POST /prompts`.     |
| Prompt Form (Edit)  | `/prompts/:id/edit` | Pre-filled form to fully replace (PUT) or partially update (PATCH) an existing prompt.                      |
| Collection List    | `/collections`       | Browse, create, and delete collections; view which collections exist for prompt grouping.                |

### Journeys Covered

| Journey                        | Screen(s)                                         |
| ------------------------------ | -------------------------------------------------- |
| View / search / filter prompts | Prompt List                                        |
| View prompt details            | Prompt Detail                                      |
| Create prompt                  | Prompt Form (Create)                               |
| Edit prompt                    | Prompt Form (Edit)                                 |
| Delete prompt                  | Prompt List (row action), Prompt Detail (button)    |
| Manage collections             | Collection List                                    |
| Test / render prompt templates | Prompt Detail (Template Tester section)            |
| View and restore versions      | Prompt Detail (Version History section)            |

---

## 2. Component Inventory

### 2.1 Layout

| Component   | Responsibility                                                        | Props                     |
| ----------- | --------------------------------------------------------------------- | ------------------------- |
| `App`       | Top-level React Router; wraps all pages inside `Layout`.              | _none_                    |
| `Layout`    | Page shell: renders `Header`, `Sidebar`, and the active page content. | `children: ReactNode`     |
| `Header`    | Top bar with the PromptLab title and API health status indicator.     | _none_                    |
| `Sidebar`   | Navigation links to Prompt List and Collection List.                 | _none_                    |

### 2.2 Prompt List

| Component         | Responsibility                                                  | Props                                                                 |
| ----------------- | --------------------------------------------------------------- | --------------------------------------------------------------------- |
| `PromptListPage`  | Fetches prompts and collections; manages filter state; renders children. | _none_                                                |
| `SearchFilterBar` | Search input, collection dropdown, and single-tag input; calls back on change. | `search: string`, `collectionId: string \| null`, `tag: string`, `collections: Collection[]`, `onChange: (filters) => void` |
| `PromptList`      | Renders the list of `PromptCard` components for the current page. | `prompts: Prompt[]`, `loading: boolean`, `onDelete: (id: string) => void` |
| `PromptCard`      | A single prompt summary card with title, tags, description, and action buttons (View, Edit, Delete). | `prompt: Prompt`, `onDelete: (id: string) => void` |

### 2.3 Prompt Detail

| Component          | Responsibility                                                  | Props                                                                 |
| ------------------ | --------------------------------------------------------------- | --------------------------------------------------------------------- |
| `PromptDetailPage` | Fetches the prompt and its versions; renders detail, tester, and history sections. | `promptId: string`                                      |
| `PromptDetail`     | Displays the prompt's title, description, content, tags, collection, and timestamps. | `prompt: Prompt`                                               |
| `TemplateTester`   | Extracts `{{variables}}` from content, provides inputs, calls `/test`, shows rendered output. | `prompt: Prompt`                                       |
| `VersionHistory`   | Lists saved versions with their fields and a "Restore" button per row. | `promptId: string`, `versions: PromptVersion[]`, `onRestore: (versionNumber: number) => void` |

### 2.4 Prompt Form (Create / Edit)

| Component         | Responsibility                                                  | Props                                                                 |
| ----------------- | --------------------------------------------------------------- | --------------------------------------------------------------------- |
| `PromptFormPage`  | Determines create vs edit mode from route; fetches prompt if editing; manages submit. | `mode: "create" \| "edit"`, `promptId?: string`                  |
| `PromptForm`      | Controlled form for title, content, description, collection, and tags. | `initialValues?: Partial<Prompt>`, `collections: Collection[]`, `onSubmit: (data) => void`, `submitting: boolean` |
| `TagInput`        | Comma-separated tag entry that produces a `string[]`.           | `tags: string[]`, `onChange: (tags: string[]) => void`               |

### 2.5 Collection List

| Component           | Responsibility                                                  | Props                                                                 |
| ------------------- | --------------------------------------------------------------- | --------------------------------------------------------------------- |
| `CollectionListPage`| Fetches collections; manages create and delete actions.        | _none_                                                                |
| `CollectionList`     | Renders the list of collections with name, description, and delete action. | `collections: Collection[]`, `loading: boolean`, `onDelete: (id: string) => void` |
| `CollectionForm`    | Inline form to create a new collection (name + description).    | `onSubmit: (data) => void`, `submitting: boolean`                    |

### 2.6 Shared Components

| Component        | Responsibility                                              | Props                                          |
| ---------------- | ----------------------------------------------------------- | ---------------------------------------------- |
| `Modal` | Reusable modal container for dialogs and overlays. | `open: boolean`, `title?: string`, `onClose: () => void`, `children: ReactNode` |
| `ConfirmDialog`  | Reusable confirmation modal for destructive actions.       | `open: boolean`, `title: string`, `message: string`, `onConfirm: () => void`, `onCancel: () => void` |
| `LoadingSpinner` | Centered spinner shown while data is being fetched.        | `message?: string`                             |
| `ErrorBanner`    | Error message with optional retry button.                   | `message: string`, `onRetry?: () => void`      |
| `EmptyState`     | Friendly message and icon when a list is empty.            | `message: string`, `actionLabel?: string`, `onAction?: () => void` |
| `Button`         | Shared styled button with variants (primary, secondary, danger). | `variant?: "primary" \| "secondary" \| "danger"`, `onClick: () => void`, `children: ReactNode`, `disabled?: boolean` |

---

## 3. API Endpoint Mapping

Every endpoint below is implemented in `backend/app/api.py` and documented in `docs/API_REFERENCE.md`. The backend binds to `0.0.0.0:8000` (verified in `backend/main.py`: `uvicorn.run(app, host="0.0.0.0", port=8000)`, `backend/Dockerfile`: `--host 0.0.0.0 --port 8000`, and `docker-compose.yml`: `ports: "8000:8000"`). The frontend reads the API base URL from the `VITE_API_BASE_URL` environment variable, defaulting to `http://localhost:8000`.

**Filtering note:** `GET /prompts` supports three optional query parameters — `collection_id`, `search`, and `tag` (single tag, exact, case-sensitive). These are the only filter parameters the backend currently implements. The `GET /tags` endpoint and `?tags=` multi-tag parameter described in `specs/tagging-system.md` are **not** implemented in the current backend and are therefore **not** included in this specification.

| Screen / Component      | Method | Endpoint                                            | When it is called                             | Purpose                                          |
| ----------------------- | ------ | --------------------------------------------------- | --------------------------------------------- | ------------------------------------------------ |
| Header                  | GET    | `/health`                                           | On app mount.                                 | Show API health status (green/red indicator).    |
| PromptListPage          | GET    | `/prompts`                                          | On mount and when filters change.             | Fetch the prompt list with optional filters.     |
| PromptListPage          | GET    | `/collections`                                      | On mount.                                     | Populate the collection filter dropdown.          |
| PromptCard              | DELETE | `/prompts/{id}`                                     | User clicks delete and confirms.              | Delete a prompt.                                  |
| PromptDetailPage        | GET    | `/prompts/{id}`                                     | On mount.                                     | Fetch the full prompt.                            |
| PromptDetailPage        | GET    | `/prompts/{id}/versions`                            | On mount.                                     | Fetch version history for the prompt.             |
| TemplateTester          | POST   | `/prompts/{id}/test`                                | User enters variable values and clicks "Render". | Render the template with provided variable values. |
| VersionHistory          | POST   | `/prompts/{id}/versions/{n}/restore`                | User clicks "Restore" on a version and confirms. | Restore the prompt to a previous version.        |
| PromptDetailPage        | DELETE | `/prompts/{id}`                                     | User clicks "Delete Prompt" and confirms.     | Delete the prompt.                                |
| PromptFormPage (Create) | GET    | `/collections`                                      | On mount.                                     | Populate the collection dropdown.                  |
| PromptFormPage (Create) | POST   | `/prompts`                                          | User submits the form.                        | Create a new prompt.                              |
| PromptFormPage (Edit)   | GET    | `/prompts/{id}`                                     | On mount.                                     | Pre-fill the form with existing values.            |
| PromptFormPage (Edit)   | GET    | `/collections`                                      | On mount.                                     | Populate the collection dropdown.                  |
| PromptFormPage (Edit)   | PUT    | `/prompts/{id}`                                     | User submits the full-replacement form.       | Fully replace the prompt.                         |
| PromptFormPage (Edit)   | PATCH  | `/prompts/{id}`                                     | User submits only changed fields.             | Partially update the prompt.                       |
| CollectionListPage      | GET    | `/collections`                                      | On mount.                                     | Fetch all collections.                            |
| CollectionListPage      | POST   | `/collections`                                      | User submits the new-collection form.          | Create a new collection.                           |
| CollectionListPage      | DELETE | `/collections/{id}`                                 | User clicks delete and confirms.              | Delete a collection (prompts are unassigned).     |

---

## 4. State Management

The frontend uses **React built-in state only** — no Redux, Zustand, or other external state-management library.

| Layer         | Mechanism                                      | Scope      | What it holds                                                              |
| ------------- | ---------------------------------------------- | ---------- | -------------------------------------------------------------------------- |
| Server data   | `useState` + `useEffect` inside page components | Per-screen | Fetched prompts, collections, versions, rendered content, health status. |
| Form state    | `useState` inside form components               | Per-form   | Field values for create/edit prompt and create collection.                |
| UI state      | `useState` inside page components               | Per-screen | Active tab, dialog open/closed, filter values, submitting flag.           |
| Navigation    | React Router (`react-router-dom`)               | App-wide   | Current route and URL parameters (`:id`).                                  |

**Data-flow principle:** Each screen fetches its own data on mount or when filters change. There is no global cache or cross-screen store. Each page is self-contained.

### API Helper Module (separate from state)

The frontend API layer is separated into small modules:

- `src/api/client.js` — shared fetch wrapper, base URL, and consistent error handling.
- `src/api/prompts.js` — prompt-related API functions.
- `src/api/collections.js` — collection-related API functions.

The API base URL is read from `import.meta.env.VITE_API_BASE_URL`.

```javascript
// src/api/client.js — concept (not implementation)
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Example wrappers:
// getPrompts(params)          → GET /prompts?collection_id=...&search=...&tag=...
// getPrompt(id)                → GET /prompts/{id}
// createPrompt(data)           → POST /prompts
// updatePrompt(id, data)       → PUT /prompts/{id}
// patchPrompt(id, data)        → PATCH /prompts/{id}
// deletePrompt(id)             → DELETE /prompts/{id}
// testPrompt(id, variables)    → POST /prompts/{id}/test
// getVersions(id)              → GET /prompts/{id}/versions
// restoreVersion(id, n)        → POST /prompts/{id}/versions/{n}/restore
// getCollections()              → GET /collections
// createCollection(data)       → POST /collections
// deleteCollection(id)          → DELETE /collections/{id}
// getHealth()                  → GET /health
```

---

## 5. Loading, Error, and Empty States

### 5.1 Loading States

| Screen / Component      | Trigger                                | Behavior                                                       |
| ----------------------- | -------------------------------------- | -------------------------------------------------------------- |
| Prompt List             | `GET /prompts` in flight               | `LoadingSpinner` replaces the prompt list; filter bar stays visible. |
| Prompt Detail           | `GET /prompts/{id}` in flight          | `LoadingSpinner` centered in the content area.                 |
| Version History         | `GET /prompts/{id}/versions` in flight | Spinner inside the version section.                             |
| Template Tester         | `POST /prompts/{id}/test` in flight    | "Render" button shows a spinner and is disabled; output area shows "Rendering…". |
| Prompt Form (Edit)      | `GET /prompts/{id}` pre-fill in flight | Form area shows `LoadingSpinner` until data arrives.            |
| Collection List         | `GET /collections` in flight          | `LoadingSpinner` replaces the collection list.                  |
| Any form submit         | `POST` / `PUT` / `PATCH` / `DELETE` in flight | Submit or delete button shows spinner text and is disabled. |

### 5.2 Error States

| Screen / Component      | Condition                                   | Behavior                                                                                  |
| ----------------------- | ------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Prompt List             | `GET /prompts` fails (network or 5xx)       | `ErrorBanner`: "Failed to load prompts." with a "Retry" button calling `refetch`.          |
| Prompt Detail           | `GET /prompts/{id}` returns 404             | `ErrorBanner`: "Prompt not found." with a link back to the Prompt List.                   |
| Prompt Detail           | `GET /prompts/{id}` fails (network or 5xx)  | `ErrorBanner`: "Failed to load prompt." with a "Retry" button.                            |
| Template Tester         | `POST /test` returns 400 (missing variables) | Inline error: "Missing values for: {variables}".                                         |
| Template Tester         | `POST /test` returns 404                    | Inline error: "Prompt not found."                                                         |
| Version Restore         | `POST /restore` returns 400 (collection gone) | `ErrorBanner` in version section: "Collection not found — cannot restore this version." |
| Version Restore         | `POST /restore` returns 404                 | `ErrorBanner`: "Version not found."                                                       |
| Prompt Form (Create)    | `POST /prompts` returns 422 (validation)   | Field-level error messages derived from the FastAPI validation `detail` array.            |
| Prompt Form (Create)    | `POST /prompts` returns 400 (bad collection) | Inline error on the collection field: "Collection not found."                            |
| Prompt Form (Edit)      | `PUT` / `PATCH` returns 404                | `ErrorBanner`: "Prompt not found." with link back to list.                                 |
| Prompt Form (Edit)      | `PUT` / `PATCH` returns 422                | Field-level error messages from the validation `detail` array.                            |
| Collection List         | `GET /collections` fails                   | `ErrorBanner`: "Failed to load collections." with "Retry".                                 |
| Collection Form         | `POST /collections` returns 422             | Field-level error on the name field.                                                       |
| Header                  | `GET /health` fails                        | Health indicator turns red with tooltip "API unreachable".                               |
| Any delete              | `DELETE` returns 404                       | `ErrorBanner`: "Item not found — it may have been deleted already."                        |

### 5.3 Empty States

| Screen / Component      | Condition                                   | Behavior                                                       |
| ----------------------- | ------------------------------------------- | -------------------------------------------------------------- |
| Prompt List             | `GET /prompts` returns `total: 0` (no filters) | `EmptyState`: "No prompts yet. Create your first prompt." with a "New Prompt" button linking to `/prompts/new`. |
| Prompt List             | Filters applied, `total: 0`                 | `EmptyState`: "No prompts match your filters." with a "Clear Filters" button. |
| Prompt Detail — Versions | `GET /versions` returns `total: 0`         | `EmptyState` inside version section: "No version history yet. Versions are saved automatically when you edit this prompt." |
| Template Tester         | Content has no `{{variables}}`              | Show content as-is with note: "This prompt has no template variables — no input needed." |
| Collection List         | `GET /collections` returns `total: 0`       | `EmptyState`: "No collections yet. Create one to organize your prompts." |

---

## 6. Folder Organization Principle

Each folder groups files by a single responsibility layer — pages are full screens, components are reusable UI building blocks, api contains HTTP API modules, and types contains frontend representations of backend models.

```
frontend/
├── src/
│   ├── main.jsx
│   ├── App.jsx
│   ├── pages/
│   │   ├── PromptListPage.jsx
│   │   ├── PromptDetailPage.jsx
│   │   ├── PromptFormPage.jsx
│   │   └── CollectionListPage.jsx
│   ├── components/
│   │   ├── Layout.jsx
│   │   ├── Header.jsx
│   │   ├── Sidebar.jsx
│   │   ├── SearchFilterBar.jsx
│   │   ├── PromptList.jsx
│   │   ├── PromptCard.jsx
│   │   ├── PromptDetail.jsx
│   │   ├── TemplateTester.jsx
│   │   ├── VersionHistory.jsx
│   │   ├── PromptForm.jsx
│   │   ├── TagInput.jsx
│   │   ├── CollectionList.jsx
│   │   ├── CollectionForm.jsx
│   │   ├── Modal.jsx
│   │   ├── ConfirmDialog.jsx
│   │   ├── LoadingSpinner.jsx
│   │   ├── ErrorBanner.jsx
│   │   ├── EmptyState.jsx
│   │   └── Button.jsx
│   ├── api/
│   │   ├── client.js
│   │   ├── prompts.js
│   │   └── collections.js
│   └── types/
│       └── api.js
├── index.html
├── package.json
└── vite.config.js                     
```

---

## 7. Frontend Constraints

- **React + Vite.** The frontend is a standard Vite React project. No Next.js, no SSR.
- **HTTP-only communication.** The frontend communicates with the backend exclusively through the HTTP API. No direct imports from `backend/`.
- **Configurable API base URL.** The API base URL is read from the `VITE_API_BASE_URL` environment variable, defaulting to `http://localhost:8000`. The `.env` file holding this variable is **not** committed to the repository.
- **No mock or hard-coded data.** All prompt, collection, and version data comes from live API calls. No hardcoded arrays or mock fixtures in the frontend source.
- **No secrets or API keys.** No API keys, tokens, or credentials are committed. The backend currently has no authentication, so none are needed.
- **No external state-management library.** State is managed with `useState`, `useEffect`, and React Router only. No Redux, Zustand, MobX, or similar.
- **No backend modifications.** This spec is frontend-only; the backend API is treated as a fixed contract.
- **No invented endpoints.** Every endpoint in this spec exists in `backend/app/api.py`. The unimplemented `GET /tags` and `?tags=` multi-tag features from `specs/tagging-system.md` are excluded.
