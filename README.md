# PromptLab

**An AI Prompt Engineering Platform — store, organize, version, and test your prompt templates.**

PromptLab is a REST API built with FastAPI that acts as a central workspace for AI prompts. Think of it as a "Postman for Prompts": you can save prompt templates with `{{variables}}`, organize them into collections, tag and search them, track their version history, and render them with sample inputs — all through a clean HTTP API.

> **Note:** PromptLab currently uses **in-memory storage**. All data is lost when the server restarts. The storage layer is isolated in `backend/app/storage.py` so it can be swapped for a real database later.
---

## Features

- 📝 **Prompt management** — Create, read, update (full and partial), and delete prompts
- 🧩 **Prompt templates** — Use `{{variable}}` placeholders inside prompt content
- 🧪 **Prompt testing** — Render a template with sample variable values via `/prompts/{id}/test`
- 📜 **Version history** — Every update automatically saves a snapshot of the previous state, retrievable via `/prompts/{id}/versions`
- 📁 **Collections** — Group prompts into named collections; deleting a collection safely unassigns its prompts instead of deleting them
- 🏷️ **Tags** — Label prompts and filter them by tag
- 🔍 **Search** — Case-insensitive search across prompt titles and descriptions
- ↕️ **Sorting & filtering** — List prompts filtered by collection, search query, or tag, sorted newest-first
- ✅ **Automatic validation** — Request data is validated with Pydantic (e.g., title length, required fields); assigning a prompt to a non-existent collection is rejected
- 🌐 **CORS enabled** — Ready for a browser-based frontend to connect
- 🏥 **Health check** — `/health` endpoint for uptime monitoring
---

## Tech Stack

- **Python 3.10+**
- **FastAPI 0.109** — web framework
- **Pydantic 2.5** — data validation
- **Uvicorn 0.27** — ASGI server
- **pytest 7.4 + httpx** — testing
---

## Project Structure

```
promptlab/
├── README.md                 # You are here
├── config.yaml
│
├── backend/
│   ├── app/
│   │   ├── __init__.py       # Package version
│   │   ├── api.py            # FastAPI routes (all endpoints)
│   │   ├── models.py         # Pydantic models (data shapes + validation)
│   │   ├── storage.py        # In-memory storage layer
│   │   └── utils.py          # Helpers: sorting, filtering, search, templating
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py       # Test fixtures (test client, sample data)
│   │   └── test_api.py       # API tests
│   ├── main.py               # Server entry point
│   └── requirements.txt      # Pinned dependencies
│
├── docs/                     # Documentation (grows over time)
├── specs/                    # Feature specifications (grows over time)
└── frontend/                 # Frontend (planned)
```

---

## Prerequisites

- **Python 3.10 or higher**
- **pip**
- **Git**

---

## Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd promptlab

# 2. Create and activate a virtual environment (recommended)
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
cd backend
pip install -r requirements.txt
```

---

## Quick Start

```bash
# From the backend/ directory
python main.py
```

The API is now running:

- **API base URL:** http://localhost:8000
- **Interactive API docs (Swagger UI):** http://localhost:8000/docs
- **Alternative docs (ReDoc):** http://localhost:8000/redoc

Verify it's working:

```bash
curl http://localhost:8000/health
```

```json
{"status": "healthy", "version": "0.1.0"}
```

### Your first prompt

```bash
# Create a prompt template with a {{variable}}
curl -X POST http://localhost:8000/prompts \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Code Review\", \"content\": \"Review the following code and provide feedback:\\n\\n{{code}}\", \"tags\": [\"coding\", \"review\"]}"
```

Response (`201 Created`):

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "Code Review",
  "content": "Review the following code and provide feedback:\n\n{{code}}",
  "description": null,
  "collection_id": null,
  "tags": ["coding", "review"],
  "created_at": "2024-01-15T10:30:00.000000",
  "updated_at": "2024-01-15T10:30:00.000000"
}
```

Render the template with a real value:

```bash
curl -X POST http://localhost:8000/prompts/<prompt-id>/test \
  -H "Content-Type: application/json" \
  -d "{\"variables\": {\"code\": \"print('hello world')\"}}"
```

```json
{
  "prompt_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "rendered_content": "Review the following code and provide feedback:\n\nprint('hello world')"
}
```

---

## API Reference

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check — returns status and API version |

### Prompts

| Method | Endpoint | Description | Success | Errors |
|--------|----------|-------------|---------|--------|
| GET | `/prompts` | List prompts (newest first) | 200 | — |
| GET | `/prompts/{id}` | Get a single prompt | 200 | 404 |
| POST | `/prompts` | Create a prompt | 201 | 400, 422 |
| PUT | `/prompts/{id}` | Full update (all fields required) | 200 | 400, 404, 422 |
| PATCH | `/prompts/{id}` | Partial update (only sent fields change) | 200 | 400, 404, 422 |
| DELETE | `/prompts/{id}` | Delete a prompt (and its version history) | 204 | 404 |
| POST | `/prompts/{id}/test` | Render the template with variable values | 200 | 400, 404 |
| GET | `/prompts/{id}/versions` | List saved versions of a prompt | 200 | 404 |
| GET | `/prompts/{id}/versions/{n}` | Get one specific version | 200 | 404 |

**Query parameters for `GET /prompts`** (can be combined):

```
GET /prompts?collection_id=<id>&search=review&tag=coding
```

| Parameter | Effect |
|-----------|--------|
| `collection_id` | Only prompts in that collection |
| `search` | Case-insensitive match on title and description |
| `tag` | Only prompts having that tag |

**PUT vs PATCH:** `PUT` replaces the whole prompt — you must send all required fields. `PATCH` changes only the fields you send:

```bash
# Change only the title; everything else stays the same
curl -X PATCH http://localhost:8000/prompts/<prompt-id> \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Better Code Review\"}"
```

Both `PUT` and `PATCH` save the previous state as a new version before overwriting, so history is never lost:

```bash
curl http://localhost:8000/prompts/<prompt-id>/versions
```

```json
{
  "versions": [
    {
      "version": 1,
      "title": "Code Review",
      "content": "Review the following code and provide feedback:\n\n{{code}}",
      "description": null,
      "collection_id": null,
      "tags": ["coding", "review"],
      "saved_at": "2024-01-15T10:35:00.000000"
    }
  ],
  "total": 1
}
```

### Collections

| Method | Endpoint | Description | Success | Errors |
|--------|----------|-------------|---------|--------|
| GET | `/collections` | List all collections | 200 | — |
| GET | `/collections/{id}` | Get a single collection | 200 | 404 |
| POST | `/collections` | Create a collection | 201 | 422 |
| DELETE | `/collections/{id}` | Delete a collection | 204 | 404 |

```bash
curl -X POST http://localhost:8000/collections \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Development\", \"description\": \"Prompts for dev tasks\"}"
```

**Deleting a collection does not delete its prompts** — their `collection_id` is set to `null` so they become unassigned.

### Common error responses

| Status | Meaning |
|--------|---------|
| 400 | Bad request (e.g., unknown `collection_id`, missing template variables) |
| 404 | Prompt, collection, or version not found |
| 422 | Validation failed (e.g., empty title, title over 200 characters) |

---

## Development Setup

The steps under **Installation** give you everything needed for development. A few extra notes:

- **Auto-reload:** `main.py` starts Uvicorn with `reload=True`, so the server restarts automatically when you edit code. Just run `python main.py` and start editing.
- **Manual testing:** use the interactive Swagger UI at http://localhost:8000/docs — you can call every endpoint from your browser without writing any client code.
- **Code layout:** keep the current layering —
  - `models.py` — data shapes and validation rules only
  - `api.py` — HTTP routes only; delegate work to `storage.py` and `utils.py`
  - `storage.py` — all data access; the API never touches the internal dictionaries directly
  - `utils.py` — pure helper functions (no state)

---

## Running Tests

```bash
# From the backend/ directory
pytest tests/ -v
```

The test suite uses FastAPI's `TestClient` (no live server needed) and fixtures from `tests/conftest.py`. Storage is automatically cleared before and after every test, so tests are fully independent.

To also see test coverage (`pytest-cov` is included in `requirements.txt`):

```bash
pytest tests/ -v --cov=app
```

---

## Contributing

1. **Create a branch** for your change:
   ```bash
   git checkout -b feature/my-change
   ```
2. **Follow the existing code conventions:**
   - Keep the layered structure (`api.py` → `storage.py` / `utils.py`)
   - Add or update Pydantic models in `models.py` for any new request/response data
   - Use type hints and docstrings consistent with the existing code
3. **Write tests** for new behavior in `tests/test_api.py` (reuse the fixtures in `conftest.py`).
4. **Run the full test suite** before submitting:
   ```bash
   pytest tests/ -v
   ```
   All tests must pass.
5. **Open a pull request** with a clear description of what changed and why.

### Reporting issues

When filing a bug report, include: the endpoint and HTTP method, the request body you sent, the response you got (status code + body), and the response you expected.

---

## Run with Docker

Docker must be installed and running.

Start the application:

```bash
docker compose up --build
```

The API is available at http://localhost:8000

Health check:

```bash
curl http://localhost:8000/health
```

Stop the application:

```bash
docker compose down
```

---

## License

Internal project — all rights reserved.



