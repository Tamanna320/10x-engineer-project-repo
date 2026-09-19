# PromptLab API Reference

**API version:** 0.1.0
**Base URL:** `http://localhost:8000` (server started via `python backend/main.py`, uvicorn on port 8000)
**Framework:** FastAPI

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Error Response Format](#error-response-format)
- [Endpoints](#endpoints)
  - [Health](#health)
    - [GET /health](#get-health)
  - [Prompts](#prompts)
    - [GET /prompts](#get-prompts)
    - [GET /prompts/{prompt_id}](#get-promptsprompt_id)
    - [POST /prompts](#post-prompts)
    - [PUT /prompts/{prompt_id}](#put-promptsprompt_id)
    - [PATCH /prompts/{prompt_id}](#patch-promptsprompt_id)
    - [DELETE /prompts/{prompt_id}](#delete-promptsprompt_id)
    - [POST /prompts/{prompt_id}/test](#post-promptsprompt_idtest)
    - [GET /prompts/{prompt_id}/versions](#get-promptsprompt_idversions)
    - [GET /prompts/{prompt_id}/versions/{version_number}](#get-promptsprompt_idversionsversion_number)
  - [Collections](#collections)
    - [GET /collections](#get-collections)
    - [GET /collections/{collection_id}](#get-collectionscollection_id)
    - [POST /collections](#post-collections)
    - [DELETE /collections/{collection_id}](#delete-collectionscollection_id)

## Overview

PromptLab is an AI prompt engineering platform. It stores **prompts** (text
templates that may contain `{{variable}}` placeholders), organizes them into
**collections**, supports tagging and full-text search, renders templates with
test values, and keeps a **version history** of prompt edits.

**Storage note:** All data is held in an in-memory store. Restarting the
server discards all prompts, collections, and versions.

**IDs and timestamps:** `id` fields are server-generated UUID4 strings.
`created_at`, `updated_at`, and `saved_at` are server-generated UTC timestamps
serialized as ISO 8601 strings.

**CORS:** All origins, methods, and headers are allowed
(`allow_origins=["*"]`, `allow_credentials=True`).

## Authentication

**None.** The API currently implements no authentication or authorization.
Every endpoint is publicly accessible and requires no API key, token, or
credentials.

## Error Response Format

Errors raised by the application return FastAPI's default error body:

```json
{
  "detail": "Human-readable error message"
}
```

Request validation failures (invalid types, missing required fields, or
constraint violations such as `title` exceeding 200 characters) return FastAPI's
default **422** body:

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character",
      "type": "string_too_short"
    }
  ]
}
```

## Endpoints

### Health

#### GET /health

Check the health status of the API. Useful for load balancer health probes and
monitoring.

**Parameters:** None.

**Authentication:** None required.

**curl example:**

```bash
curl http://localhost:8000/health
```

**Response shape (`HealthResponse`):**

| Field     | Type   | Description                          |
| --------- | ------ | ------------------------------------ |
| `status`  | string | Health status, always `"healthy"`.   |
| `version` | string | Running API version (app `__version__`). |

**Sample response — `200 OK`:**

```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

**Error status codes:** None (always returns 200 when the server is running).

---

### Prompts

#### GET /prompts

List all prompts, with optional filtering and searching. Filters are applied
cumulatively when several are provided, in the order: collection → search →
tag. Results are sorted by `created_at`, newest first.

**Query parameters:**

| Parameter       | Type   | Required | Description                                                                                                    |
| --------------- | ------ | -------- | -------------------------------------------------------------------------------------------------------------- |
| `collection_id` | string | No       | Only return prompts belonging to this collection ID.                                                            |
| `search`        | string | No       | Case-insensitive substring match against the prompt `title` and `description` (prompts with no description match on title only). |
| `tag`           | string | No       | Only return prompts whose `tags` list contains this exact (case-sensitive) tag.                                 |

**Authentication:** None required.

**curl example:**

```bash
# All prompts
curl http://localhost:8000/prompts

# Filtered and searched
curl "http://localhost:8000/prompts?collection_id=col-123&search=email&tag=marketing"
```

**Response shape (`PromptList`):**

| Field     | Type            | Description                                                |
| --------- | --------------- | ---------------------------------------------------------- |
| `prompts` | array of Prompt | Matching prompts, sorted by `created_at` newest first.      |
| `total`   | integer         | Number of matching prompts.                                |

Each `Prompt` object has the shape described under
[GET /prompts/{prompt_id}](#get-promptsprompt_id).

**Sample response — `200 OK`:**

```json
{
  "prompts": [
    {
      "id": "b3f1c2a4-8d6e-4f5a-9b0c-1d2e3f4a5b6c",
      "title": "Marketing Email",
      "content": "Write a {{tone}} marketing email for {{product}}.",
      "description": "Generates marketing emails.",
      "collection_id": "col-123",
      "tags": ["marketing", "email"],
      "created_at": "2025-01-15T10:30:00",
      "updated_at": "2025-01-15T10:30:00"
    }
  ],
  "total": 1
}
```

**Error status codes:**

| Code | Reason                                                        |
| ---- | ------------------------------------------------------------- |
| 422  | Query parameters of the wrong type (FastAPI validation error). |

---

#### GET /prompts/{prompt_id}

Retrieve a single prompt by its ID.

**Path parameters:**

| Parameter   | Type   | Required | Description                |
| ----------- | ------ | -------- | -------------------------- |
| `prompt_id` | string | Yes      | The prompt's unique ID.    |

**Authentication:** None required.

**curl example:**

```bash
curl http://localhost:8000/prompts/b3f1c2a4-8d6e-4f5a-9b0c-1d2e3f4a5b6c
```

**Response shape (`Prompt`):**

| Field           | Type            | Description                                                          |
| --------------- | --------------- | -------------------------------------------------------------------- |
| `id`            | string          | Server-generated UUID4.                                              |
| `title`         | string          | Prompt title (1–200 chars).                                          |
| `content`       | string          | Prompt text; may contain `{{variable}}` placeholders (min 1 char).   |
| `description`   | string or null  | Optional summary (max 500 chars).                                    |
| `collection_id` | string or null  | ID of the owning collection, or null.                                |
| `tags`          | array of string | Tags for categorization and filtering.                               |
| `created_at`    | string (datetime) | Creation timestamp (UTC).                                          |
| `updated_at`    | string (datetime) | Last update timestamp (UTC).                                       |

**Sample response — `200 OK`:**

```json
{
  "id": "b3f1c2a4-8d6e-4f5a-9b0c-1d2e3f4a5b6c",
  "title": "Marketing Email",
  "content": "Write a {{tone}} marketing email for {{product}}.",
  "description": "Generates marketing emails.",
  "collection_id": "col-123",
  "tags": ["marketing", "email"],
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-16T08:15:00"
}
```

**Error status codes:**

| Code | Reason                    | Detail message      |
| ---- | ------------------------- | ------------------- |
| 404  | No prompt with that ID.   | `"Prompt not found"` |

---

#### POST /prompts

Create a new prompt. The server assigns `id`, `created_at`, and `updated_at`.

**Request body (`PromptCreate`):**

| Field           | Type            | Required | Constraint              | Default |
| --------------- | --------------- | -------- | ----------------------- | ------- |
| `title`         | string          | Yes      | 1–200 characters        | —       |
| `content`       | string          | Yes      | Minimum 1 character     | —       |
| `description`   | string or null  | No       | Maximum 500 characters  | `null`  |
| `collection_id` | string or null  | No       | Must reference an existing collection | `null` |
| `tags`          | array of string | No       | —                       | `[]`    |

**Authentication:** None required.

**curl example:**

```bash
curl -X POST http://localhost:8000/prompts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Marketing Email",
    "content": "Write a {{tone}} marketing email for {{product}}.",
    "description": "Generates marketing emails.",
    "collection_id": "col-123",
    "tags": ["marketing", "email"]
  }'
```

**Response shape:** `Prompt` (see [GET /prompts/{prompt_id}](#get-promptsprompt_id)).

**Sample response — `201 Created`:**

```json
{
  "id": "b3f1c2a4-8d6e-4f5a-9b0c-1d2e3f4a5b6c",
  "title": "Marketing Email",
  "content": "Write a {{tone}} marketing email for {{product}}.",
  "description": "Generates marketing emails.",
  "collection_id": "col-123",
  "tags": ["marketing", "email"],
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T10:30:00"
}
```

**Error status codes:**

| Code | Reason                                                       | Detail message          |
| ---- | ------------------------------------------------------------ | ----------------------- |
| 400  | `collection_id` was provided but no such collection exists.  | `"Collection not found"` |
| 422  | Body fails validation (missing `title`/`content`, constraints violated, wrong types). | (FastAPI validation error) |

---

#### PUT /prompts/{prompt_id}

Fully replace an existing prompt (PUT semantics). **All fields are replaced
with the values in the request body** — omitted optional fields fall back to
their defaults (`description` → `null`, `collection_id` → `null`,
`tags` → `[]`), so clients must send every field they want to keep. For
partial updates, use [PATCH](#patch-promptsprompt_id) instead.

Before overwriting, the prompt's **current state is saved as a new
`PromptVersion`** in its version history. `id` and `created_at` are preserved;
`updated_at` is refreshed.

**Path parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `prompt_id` | string | Yes      | The prompt's unique ID. |

**Request body (`PromptUpdate`):** same fields and constraints as
`PromptCreate` (see [POST /prompts](#post-prompts)).

**Authentication:** None required.

**curl example:**

```bash
curl -X PUT http://localhost:8000/prompts/b3f1c2a4-8d6e-4f5a-9b0c-1d2e3f4a5b6c \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Marketing Email v2",
    "content": "Write a {{tone}} marketing email for {{product}} in {{language}}.",
    "description": "Generates marketing emails, now multilingual.",
    "collection_id": "col-123",
    "tags": ["marketing", "email", "v2"]
  }'
```

**Response shape:** `Prompt`.

**Sample response — `200 OK`:**

```json
{
  "id": "b3f1c2a4-8d6e-4f5a-9b0c-1d2e3f4a5b6c",
  "title": "Marketing Email v2",
  "content": "Write a {{tone}} marketing email for {{product}} in {{language}}.",
  "description": "Generates marketing emails, now multilingual.",
  "collection_id": "col-123",
  "tags": ["marketing", "email", "v2"],
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-16T08:15:00"
}
```

**Error status codes:**

| Code | Reason                                                       | Detail message          |
| ---- | ------------------------------------------------------------ | ----------------------- |
| 404  | No prompt with that ID.                                      | `"Prompt not found"`    |
| 400  | `collection_id` was provided but no such collection exists.  | `"Collection not found"` |
| 422  | Body fails validation.                                       | (FastAPI validation error) |

---

#### PATCH /prompts/{prompt_id}

Partially update an existing prompt (PATCH semantics). **Only the fields
explicitly provided in the request body are changed**; omitted fields keep
their current values. Explicitly sending a field as `null` (e.g.
`"collection_id": null`) sets that field to `null`, which can be used to
unassign a prompt from its collection.

Before overwriting, the prompt's **current state is saved as a new
`PromptVersion`** in its version history (same as PUT). `id` and `created_at`
are preserved; `updated_at` is refreshed.

**Path parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `prompt_id` | string | Yes      | The prompt's unique ID. |

**Request body (`PromptPatch`):** all fields optional; any subset may be sent.

| Field           | Type            | Constraint (if provided)        |
| --------------- | --------------- | ------------------------------- |
| `title`         | string or null  | 1–200 characters                |
| `content`       | string or null  | Minimum 1 character             |
| `description`   | string or null  | Maximum 500 characters          |
| `collection_id` | string or null  | Non-null values must reference an existing collection |
| `tags`          | array of string or null | Replaces the existing tags entirely |

**Authentication:** None required.

**curl example:**

```bash
# Update only the title and tags
curl -X PATCH http://localhost:8000/prompts/b3f1c2a4-8d6e-4f5a-9b0c-1d2e3f4a5b6c \
  -H "Content-Type: application/json" \
  -d '{"title": "Marketing Email v3", "tags": ["marketing", "email", "v3"]}'

# Unassign the prompt from its collection
curl -X PATCH http://localhost:8000/prompts/b3f1c2a4-8d6e-4f5a-9b0c-1d2e3f4a5b6c \
  -H "Content-Type: application/json" \
  -d '{"collection_id": null}'
```

**Response shape:** `Prompt`.

**Sample response — `200 OK`:**

```json
{
  "id": "b3f1c2a4-8d6e-4f5a-9b0c-1d2e3f4a5b6c",
  "title": "Marketing Email v3",
  "content": "Write a {{tone}} marketing email for {{product}} in {{language}}.",
  "description": "Generates marketing emails, now multilingual.",
  "collection_id": "col-123",
  "tags": ["marketing", "email", "v3"],
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-17T09:00:00"
}
```

**Error status codes:**

| Code | Reason                                                                  | Detail message          |
| ---- | ----------------------------------------------------------------------- | ----------------------- |
| 404  | No prompt with that ID.                                                 | `"Prompt not found"`    |
| 400  | A non-null `collection_id` was provided but no such collection exists.  | `"Collection not found"` |
| 422  | Body fails validation (e.g. `title` longer than 200 characters).        | (FastAPI validation error) |

---

#### DELETE /prompts/{prompt_id}

Delete a prompt by its ID. The prompt's version history is deleted along with
it. Returns `204 No Content` with an empty body on success.

**Path parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `prompt_id` | string | Yes      | The prompt's unique ID. |

**Authentication:** None required.

**curl example:**

```bash
curl -X DELETE http://localhost:8000/prompts/b3f1c2a4-8d6e-4f5a-9b0c-1d2e3f4a5b6c
```

**Response shape:** No body.

**Sample response:** `204 No Content` (empty body).

**Error status codes:**

| Code | Reason                  | Detail message      |
| ---- | ----------------------- | ------------------- |
| 404  | No prompt with that ID. | `"Prompt not found"` |

---

#### POST /prompts/{prompt_id}/test

Render a prompt template with test variable values. Every `{{variable}}`
placeholder in the prompt's `content` is extracted, and the request must
supply a value for each one. The rendered result lets users preview the exact
text that would be sent to an LLM. The prompt itself is not modified.

**Path parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `prompt_id` | string | Yes      | The prompt's unique ID. |

**Request body (`PromptTestRequest`):**

| Field       | Type                    | Required | Default | Description                                                                                  |
| ----------- | ----------------------- | -------- | ------- | -------------------------------------------------------------------------------------------- |
| `variables` | object (string → string) | No       | `{}`    | Maps each template variable name (without `{{ }}`) to the value to substitute. Keys not matching any placeholder have no effect. |

**Authentication:** None required.

**curl example:**

```bash
curl -X POST http://localhost:8000/prompts/b3f1c2a4-8d6e-4f5a-9b0c-1d2e3f4a5b6c/test \
  -H "Content-Type: application/json" \
  -d '{"variables": {"tone": "friendly", "product": "PromptLab"}}'
```

**Response shape (`PromptTestResponse`):**

| Field              | Type   | Description                                        |
| ------------------ | ------ | -------------------------------------------------- |
| `prompt_id`        | string | ID of the prompt that was rendered.                |
| `rendered_content` | string | Content with all provided variables substituted.   |

**Sample response — `200 OK`:**

```json
{
  "prompt_id": "b3f1c2a4-8d6e-4f5a-9b0c-1d2e3f4a5b6c",
  "rendered_content": "Write a friendly marketing email for PromptLab."
}
```

**Error status codes:**

| Code | Reason                                                                       | Detail message                                            |
| ---- | ---------------------------------------------------------------------------- | --------------------------------------------------------- |
| 404  | No prompt with that ID.                                                      | `"Prompt not found"`                                       |
| 400  | One or more template variables have no value in `variables`.                 | `"Missing values for variables: language"` (comma-separated list) |
| 422  | Body fails validation (e.g. `variables` is not an object of strings).        | (FastAPI validation error)                                 |

---

#### GET /prompts/{prompt_id}/versions

List the saved version history of a prompt. A snapshot is saved each time the
prompt is updated via PUT or PATCH, capturing the state **before** the update.
Versions are returned in the order they were saved (oldest first). A prompt
that has never been updated returns an empty list.

**Path parameters:**

| Parameter   | Type   | Required | Description             |
| ----------- | ------ | -------- | ----------------------- |
| `prompt_id` | string | Yes      | The prompt's unique ID. |

**Authentication:** None required.

**curl example:**

```bash
curl http://localhost:8000/prompts/b3f1c2a4-8d6e-4f5a-9b0c-1d2e3f4a5b6c/versions
```

**Response shape (`VersionList`):**

| Field      | Type                   | Description                              |
| ---------- | ---------------------- | ---------------------------------------- |
| `versions` | array of PromptVersion | Saved snapshots, in the order saved.     |
| `total`    | integer                | Number of saved versions.                |

Each `PromptVersion` object has the shape described under
[GET /prompts/{prompt_id}/versions/{version_number}](#get-promptsprompt_idversionsversion_number).

**Sample response — `200 OK`:**

```json
{
  "versions": [
    {
      "version": 1,
      "title": "Marketing Email",
      "content": "Write a {{tone}} marketing email for {{product}}.",
      "description": "Generates marketing emails.",
      "collection_id": "col-123",
      "tags": ["marketing", "email"],
      "saved_at": "2025-01-16T08:15:00"
    }
  ],
  "total": 1
}
```

**Error status codes:**

| Code | Reason                  | Detail message      |
| ---- | ----------------------- | ------------------- |
| 404  | No prompt with that ID. | `"Prompt not found"` |

---

#### GET /prompts/{prompt_id}/versions/{version_number}

Retrieve a specific version from a prompt's history. Version numbers are
sequential, starting at 1 for the first saved snapshot.

**Path parameters:**

| Parameter        | Type    | Required | Description                          |
| ---------------- | ------- | -------- | ------------------------------------ |
| `prompt_id`      | string  | Yes      | The prompt's unique ID.              |
| `version_number` | integer | Yes      | The sequential version number (≥ 1). |

**Authentication:** None required.

**curl example:**

```bash
curl http://localhost:8000/prompts/b3f1c2a4-8d6e-4f5a-9b0c-1d2e3f4a5b6c/versions/1
```

**Response shape (`PromptVersion`):**

| Field           | Type            | Description                                          |
| --------------- | --------------- | ---------------------------------------------------- |
| `version`       | integer         | Sequential version number.                           |
| `title`         | string          | Title at the time of the snapshot.                   |
| `content`       | string          | Content at the time of the snapshot.                 |
| `description`   | string or null  | Description at the time of the snapshot.             |
| `collection_id` | string or null  | Owning collection ID at the time of the snapshot.    |
| `tags`          | array of string | Tags at the time of the snapshot.                    |
| `saved_at`      | string (datetime) | When the snapshot was saved (UTC).                 |

**Sample response — `200 OK`:**

```json
{
  "version": 1,
  "title": "Marketing Email",
  "content": "Write a {{tone}} marketing email for {{product}}.",
  "description": "Generates marketing emails.",
  "collection_id": "col-123",
  "tags": ["marketing", "email"],
  "saved_at": "2025-01-16T08:15:00"
}
```

**Error status codes:**

| Code | Reason                                                  | Detail message        |
| ---- | ------------------------------------------------------- | --------------------- |
| 404  | No prompt with that ID.                                 | `"Prompt not found"`  |
| 404  | The prompt has no version with that number.             | `"Version not found"` |
| 422  | `version_number` is not an integer.                     | (FastAPI validation error) |

---

### Collections

#### GET /collections

List all collections.

**Parameters:** None.

**Authentication:** None required.

**curl example:**

```bash
curl http://localhost:8000/collections
```

**Response shape (`CollectionList`):**

| Field         | Type                | Description                     |
| ------------- | ------------------- | ------------------------------- |
| `collections` | array of Collection | All stored collections.         |
| `total`       | integer             | Number of collections.          |

Each `Collection` object has the shape described under
[GET /collections/{collection_id}](#get-collectionscollection_id).

**Sample response — `200 OK`:**

```json
{
  "collections": [
    {
      "id": "col-123",
      "name": "Marketing",
      "description": "Prompts for marketing copy.",
      "created_at": "2025-01-10T09:00:00"
    }
  ],
  "total": 1
}
```

**Error status codes:** None (returns an empty list when no collections exist).

---

#### GET /collections/{collection_id}

Retrieve a single collection by its ID.

**Path parameters:**

| Parameter       | Type   | Required | Description                   |
| --------------- | ------ | -------- | ----------------------------- |
| `collection_id` | string | Yes      | The collection's unique ID.   |

**Authentication:** None required.

**curl example:**

```bash
curl http://localhost:8000/collections/col-123
```

**Response shape (`Collection`):**

| Field         | Type              | Description                        |
| ------------- | ----------------- | ---------------------------------- |
| `id`          | string            | Server-generated UUID4.            |
| `name`        | string            | Collection name (1–100 chars).     |
| `description` | string or null    | Optional summary (max 500 chars).  |
| `created_at`  | string (datetime) | Creation timestamp (UTC).          |

**Sample response — `200 OK`:**

```json
{
  "id": "col-123",
  "name": "Marketing",
  "description": "Prompts for marketing copy.",
  "created_at": "2025-01-10T09:00:00"
}
```

**Error status codes:**

| Code | Reason                      | Detail message          |
| ---- | --------------------------- | ----------------------- |
| 404  | No collection with that ID. | `"Collection not found"` |

---

#### POST /collections

Create a new collection. The server assigns `id` and `created_at`.

**Request body (`CollectionCreate`):**

| Field         | Type           | Required | Constraint             | Default |
| ------------- | -------------- | -------- | ---------------------- | ------- |
| `name`        | string         | Yes      | 1–100 characters       | —       |
| `description` | string or null | No       | Maximum 500 characters | `null`  |

**Authentication:** None required.

**curl example:**

```bash
curl -X POST http://localhost:8000/collections \
  -H "Content-Type: application/json" \
  -d '{"name": "Marketing", "description": "Prompts for marketing copy."}'
```

**Response shape:** `Collection` (see [GET /collections/{collection_id}](#get-collectionscollection_id)).

**Sample response — `201 Created`:**

```json
{
  "id": "col-123",
  "name": "Marketing",
  "description": "Prompts for marketing copy.",
  "created_at": "2025-01-10T09:00:00"
}
```

**Error status codes:**

| Code | Reason                                                                       |
| ---- | ---------------------------------------------------------------------------- |
| 422  | Body fails validation (missing `name`, constraints violated, wrong types).   |

---

#### DELETE /collections/{collection_id}

Delete a collection by its ID. Prompts belonging to the collection are **not
deleted** — they are first unassigned (their `collection_id` is set to `null`).
Returns `204 No Content` with an empty body on success.

**Path parameters:**

| Parameter       | Type   | Required | Description                 |
| --------------- | ------ | -------- | --------------------------- |
| `collection_id` | string | Yes      | The collection's unique ID. |

**Authentication:** None required.

**curl example:**

```bash
curl -X DELETE http://localhost:8000/collections/col-123
```

**Response shape:** No body.

**Sample response:** `204 No Content` (empty body).

**Error status codes:**

| Code | Reason                      | Detail message          |
| ---- | --------------------------- | ----------------------- |
| 404  | No collection with that ID. | `"Collection not found"` |

---

## Endpoint Summary

| Method | Path                                          | Description                                  | Success status |
| ------ | --------------------------------------------- | -------------------------------------------- | -------------- |
| GET    | `/health`                                     | Health check.                                | 200            |
| GET    | `/prompts`                                    | List/filter/search prompts (newest first).   | 200            |
| GET    | `/prompts/{prompt_id}`                        | Get one prompt.                              | 200            |
| POST   | `/prompts`                                    | Create a prompt.                             | 201            |
| PUT    | `/prompts/{prompt_id}`                        | Fully replace a prompt (saves a version).    | 200            |
| PATCH  | `/prompts/{prompt_id}`                        | Partially update a prompt (saves a version). | 200            |
| DELETE | `/prompts/{prompt_id}`                        | Delete a prompt and its version history.     | 204            |
| POST   | `/prompts/{prompt_id}/test`                   | Render the template with test variables.     | 200            |
| GET    | `/prompts/{prompt_id}/versions`               | List a prompt's version history.             | 200            |
| GET    | `/prompts/{prompt_id}/versions/{version_number}` | Get one saved version.                    | 200            |
| GET    | `/collections`                                | List all collections.                        | 200            |
| GET    | `/collections/{collection_id}`                | Get one collection.                          | 200            |
| POST   | `/collections`                                | Create a collection.                         | 201            |
| DELETE | `/collections/{collection_id}`                | Delete a collection (prompts are unassigned).| 204            |
