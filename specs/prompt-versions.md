# Feature Specification: Prompt Version History & Restore

| Field              | Value                                                                 |
| ------------------ | --------------------------------------------------------------------- |
| Feature            | Prompt Version History & Restore                                      |
| Spec file          | `specs/prompt-versions.md`                                            |
| Status             | Draft — ready for implementation                                      |
| Target release     | 0.2.0 (current version: 0.1.0)                                        |
| Source of truth    | `backend/app/api.py`, `backend/app/models.py`, `backend/app/storage.py`, `backend/app/utils.py`, `backend/tests/`, `docs/API_REFERENCE.md`, `README.md` |

---

## 1. Overview and Goals

### 1.1 What exists today (verified against the current codebase)

The version-history mechanism is **partially implemented**:

- **Snapshots are created automatically.** Both `PUT /prompts/{prompt_id}` and
  `PATCH /prompts/{prompt_id}` build a `PromptVersion` from the prompt's
  **pre-update** state and save it via `storage.save_version()` **before**
  overwriting the prompt.
- **Version numbers are sequential per prompt**, computed as
  `len(storage.get_versions(prompt_id)) + 1`, so the first snapshot is
  version 1.
- **Retrieval endpoints exist:**
  - `GET /prompts/{prompt_id}/versions` → `VersionList`
  - `GET /prompts/{prompt_id}/versions/{version_number}` → `PromptVersion`
- **History is deleted with the prompt.** `storage.delete_prompt()` also
  removes the prompt's version list.
- **The `PromptVersion` docstring already promises restore** ("Versions allow
  users to inspect or restore earlier content"), but **no restore capability
  exists** — that is the gap this specification closes.

### 1.2 Goals

- **G-1.** Guarantee, as a documented contract, that every **successful**
  `PUT` or `PATCH` on a prompt saves exactly one snapshot of the pre-update
  state. (Codifies existing behavior; no code change.)
- **G-2.** Guarantee the retrieval contract for listing and fetching versions,
  including exact response shapes, ordering, and error messages. (Codifies
  existing behavior; no code change.)
- **G-3.** Add one **new** endpoint,
  `POST /prompts/{prompt_id}/versions/{version_number}/restore`, that
  replaces a prompt's editable fields with the values captured in a saved
  version. (**New code — the only new endpoint in this spec.**)
- **G-4.** Make restore itself safe: restoring a prompt first saves a snapshot
  of the state being replaced, so a restore can always be undone by restoring
  the newest version.
- **G-5.** Introduce **no breaking changes**: no new or removed fields on any
  existing model, no changed response shapes, no changed status codes or
  error messages on existing endpoints.

### 1.3 Out of scope (explicitly not part of this feature)

- Diffing two versions.
- Deleting an individual version or pruning history.
- Version retention limits or pagination of version lists.
- Restoring a version **as a new prompt** (copy-on-restore). Restore is
  always in place, on the same `prompt_id`.
- Authentication/authorization (the API currently has none).
- A `current_version` field on `Prompt` (not required by any story below).

---

## 2. User Stories with Testable Acceptance Criteria

### US-1 — Automatic snapshot on update (existing behavior, formalized)

> As a prompt author, I want every successful update of my prompt to save the
> previous state automatically, so that no edit can destroy earlier work.

**Acceptance criteria:**

- **AC-1.1 (PUT creates snapshot):** Given a prompt created with
  `title = "Original Title"`, when `PUT /prompts/{id}` succeeds with
  `title = "Updated Title"`, then `GET /prompts/{id}/versions` returns
  `200` with `total == 1`, and `versions[0]["title"] == "Original Title"`.
- **AC-1.2 (PATCH creates snapshot):** Given the same prompt, when a
  subsequent `PATCH /prompts/{id}` succeeds with `title = "Third Title"`,
  then `GET /prompts/{id}/versions` returns `total == 2`, and
  `versions[1]["title"] == "Updated Title"`.
- **AC-1.3 (snapshot captures all editable fields):** Each saved version
  contains the pre-update values of `title`, `content`, `description`,
  `collection_id`, and `tags`, plus a `version` number and a `saved_at`
  timestamp.
- **AC-1.4 (failed updates create no snapshot):** When a `PUT` or `PATCH`
  fails with `400`, `404`, or `422`, the prompt's version `total` is
  unchanged afterwards.

### US-2 — List version history (existing behavior, formalized)

> As a prompt author, I want to see every saved version of a prompt, so that
> I can find the state I want to return to.

**Acceptance criteria:**

- **AC-2.1:** Given a prompt updated twice, `GET /prompts/{id}/versions`
  returns `200` with body `{"versions": [...], "total": 2}`, where
  `versions[0]["version"] == 1` and `versions[1]["version"] == 2` (oldest
  first, insertion order).
- **AC-2.2:** Given a prompt that has never been updated,
  `GET /prompts/{id}/versions` returns `200` with
  `{"versions": [], "total": 0}`.
- **AC-2.3:** Given an unknown prompt ID, `GET /prompts/{id}/versions`
  returns `404` with body `{"detail": "Prompt not found"}`.

### US-3 — Retrieve one specific version (existing behavior, formalized)

> As a prompt author, I want to fetch a single version by number, so that I
> can inspect exactly what the prompt looked like at that point.

**Acceptance criteria:**

- **AC-3.1:** Given a prompt whose original title was `"Code Review Prompt"`
  and which was then PATCHed twice (to `"V2 Title"`, then `"V3 Title"`),
  `GET /prompts/{id}/versions/1` returns `200` with
  `title == "Code Review Prompt"`, and `GET /prompts/{id}/versions/2`
  returns `200` with `title == "V2 Title"`.
- **AC-3.2:** `GET /prompts/{id}/versions/99` (no such version) returns `404`
  with body `{"detail": "Version not found"}`.
- **AC-3.3:** `GET /prompts/{unknown-id}/versions/1` returns `404` with body
  `{"detail": "Prompt not found"}`.

### US-4 — Restore a prompt to a previous version (**new**)

> As a prompt author, I want to restore my prompt to any saved version, so
> that I can recover from a bad edit without retyping the old content.

**Acceptance criteria:**

- **AC-4.1 (happy path):** Given a prompt created with `title = "Original"`
  and then updated so its current title is `"Changed"`, when
  `POST /prompts/{id}/versions/1/restore` is called, then the response is
  `200` and the response body is the restored `Prompt` with
  `title == "Original"`.
- **AC-4.2 (restore snapshots current state first):** After the restore in
  AC-4.1, `GET /prompts/{id}/versions` returns `total == 2`, and
  `versions[1]["title"] == "Changed"` (the state that was just replaced).
- **AC-4.3 (identity fields preserved):** The restore response body has the
  same `id` and `created_at` as before the restore, and an `updated_at`
  different from (later than) its pre-restore value.
- **AC-4.4 (all editable fields restored):** Restoring version *n* sets the
  prompt's `title`, `content`, `description`, `collection_id`, and `tags`
  to exactly the values stored in version *n*, including `null` and `[]`
  values.
- **AC-4.5 (unknown prompt):** `POST /prompts/{unknown-id}/versions/1/restore`
  returns `404` with body `{"detail": "Prompt not found"}`.
- **AC-4.6 (unknown version):** `POST /prompts/{id}/versions/99/restore`
  returns `404` with body `{"detail": "Version not found"}`, and the prompt
  is unchanged.
- **AC-4.7 (restore is repeatable):** Calling restore for the same version
  twice succeeds both times; each call appends exactly one new snapshot, so
  `total` grows by 1 per call.

### US-5 — History lifetime follows the prompt (existing behavior, formalized)

> As a prompt author, I want a deleted prompt's history removed with it, so
> that storage does not fill with orphaned versions.

**Acceptance criteria:**

- **AC-5.1:** Given a prompt with at least one saved version, when
  `DELETE /prompts/{id}` returns `204`, then a subsequent
  `GET /prompts/{id}/versions` returns `404` with
  `{"detail": "Prompt not found"}`.

---

## 3. Data Model Changes

### 3.1 Existing models — **unchanged** (no new, removed, or retyped fields)

`PromptVersion` (in `backend/app/models.py`) remains exactly as implemented:

| Field           | Type            | Description                                              |
| --------------- | --------------- | -------------------------------------------------------- |
| `version`       | `int`           | Sequential per prompt, starting at 1.                     |
| `title`         | `str`           | Title at snapshot time.                                   |
| `content`       | `str`           | Content at snapshot time (may contain `{{variables}}`).   |
| `description`   | `Optional[str]` | Description at snapshot time; default `None`.             |
| `collection_id` | `Optional[str]` | Owning collection at snapshot time; default `None`.       |
| `tags`          | `List[str]`     | Tags at snapshot time; default `[]`.                      |
| `saved_at`      | `datetime`      | UTC timestamp when the snapshot was saved (auto-set).     |

`VersionList` remains `{"versions": List[PromptVersion], "total": int}`.

`Prompt` is unchanged. Restore responses reuse it as-is
(`id`, `title`, `content`, `description`, `collection_id`, `tags`,
`created_at`, `updated_at`).

### 3.2 New models — **none**

The restore endpoint takes **no request body** and returns the existing
`Prompt` model, so no new Pydantic model is introduced.

### 3.3 Storage changes — **none required**

`Storage` (`backend/app/storage.py`) already provides everything the restore
endpoint needs. The implementation must compose the existing methods only:

- `get_prompt(prompt_id)`
- `get_version(prompt_id, version_number)`
- `get_versions(prompt_id)`
- `save_version(prompt_id, version)`
- `update_prompt(prompt_id, prompt)`
- `get_collection(collection_id)` (for the validation rule in §4.3)

### 3.4 Normative versioning rules

1. Version numbers are per-prompt, start at **1**, and increase by exactly 1
   per snapshot. The next number is always
   `len(storage.get_versions(prompt_id)) + 1`.
2. A snapshot is created **only** by a successful `PUT`, `PATCH`, or restore,
   and always captures the **pre-change** state.
3. Version numbers are never reused within a prompt's lifetime.
4. Versions are returned oldest-first (insertion order).
5. Deleting a prompt deletes its entire version history.

---

## 4. API Endpoints

### 4.1 Snapshot triggers: `PUT` / `PATCH /prompts/{prompt_id}` (existing — no API change)

- **Purpose:** Full / partial update. As part of a successful update, save
  the pre-update state as the next `PromptVersion`.
- **Request/response shapes:** Unchanged (see `docs/API_REFERENCE.md`).
- **Status codes:** Unchanged (`200`, `400`, `404`, `422`).
- **Directly testable acceptance criterion:** Given a prompt updated once via
  `PUT` with a new title, `GET /prompts/{id}/versions` returns
  `total == 1` and `versions[0]["title"]` equals the **original** title
  (mirrors existing test `test_version_history_created_on_update`). A `PUT`
  that fails validation (`422`) leaves `total == 0`.

### 4.2 `GET /prompts/{prompt_id}/versions` (existing — contract formalized)

- **Purpose:** List the prompt's saved versions, oldest first.
- **Request shape:** No body. Path parameter `prompt_id: str`.
- **Response shape (`200`, `VersionList`):**
  `{"versions": [PromptVersion, ...], "total": int}`
- **Status codes:** `200` (including empty history), `404`.
- **Directly testable acceptance criteria:** AC-2.1, AC-2.2, AC-2.3 above.

### 4.3 `GET /prompts/{prompt_id}/versions/{version_number}` (existing — contract formalized)

- **Purpose:** Fetch one saved version by its sequential number.
- **Request shape:** No body. Path parameters `prompt_id: str`,
  `version_number: int`.
- **Response shape (`200`, `PromptVersion`):** the seven fields listed in
  §3.1.
- **Status codes:** `200`, `404` (`"Prompt not found"` /
  `"Version not found"`), `422` (non-integer `version_number`).
- **Directly testable acceptance criteria:** AC-3.1, AC-3.2, AC-3.3 above.

### 4.4 `POST /prompts/{prompt_id}/versions/{version_number}/restore` (**NEW**)

- **Purpose:** Replace the prompt's editable fields (`title`, `content`,
  `description`, `collection_id`, `tags`) with the values stored in version
  `version_number`, after first snapshotting the current state. `id` and
  `created_at` are preserved; `updated_at` is refreshed.
- **Request shape:** No request body (any body sent is ignored). Path
  parameters `prompt_id: str`, `version_number: int`.
- **Response shape (`200`):** the updated `Prompt`:

  ```json
  {
    "id": "b3f1c2a4-8d6e-4f5a-9b0c-1d2e3f4a5b6c",
    "title": "Original",
    "content": "Review the following code and provide feedback:\n\n{{code}}",
    "description": "A prompt for AI code review",
    "collection_id": null,
    "tags": ["coding", "review"],
    "created_at": "2025-01-15T10:30:00",
    "updated_at": "2025-01-17T09:00:00"
  }
  ```

- **Status codes:**

  | Code | Condition                                             | Body                                    |
  | ---- | ----------------------------------------------------- | --------------------------------------- |
  | 200  | Restore succeeded.                                    | `Prompt`                                 |
  | 400  | Version's `collection_id` is non-null but the collection no longer exists. | `{"detail": "Collection not found"}` |
  | 404  | No prompt with `prompt_id`.                           | `{"detail": "Prompt not found"}`         |
  | 404  | Prompt exists, but has no version `version_number`.   | `{"detail": "Version not found"}`        |
  | 422  | `version_number` is not an integer.                   | FastAPI validation error                 |

- **Required processing order (normative):**
  1. `prompt = storage.get_prompt(prompt_id)`; if missing → `404 "Prompt not found"`.
  2. `version = storage.get_version(prompt_id, version_number)`; if missing → `404 "Version not found"`.
  3. If `version.collection_id` is not `None` and
     `storage.get_collection(version.collection_id)` is missing →
     `400 "Collection not found"` with **no state change** (no snapshot, no
     modification).
  4. Snapshot the **current** prompt state as the next version (fields per
     §3.1, number per §3.4 rule 1) via `storage.save_version()`.
  5. Build a `Prompt` with the existing `id` and `created_at`, all editable
     fields taken from `version`, and `updated_at = get_current_time()`.
  6. Return `storage.update_prompt(prompt_id, updated_prompt)`.

- **Implementation placement:** new route in
  `backend/app/api.py`, immediately after `get_prompt_version`, decorated with
  `@app.post("/prompts/{prompt_id}/versions/{version_number}/restore", response_model=Prompt)`.
  No new imports are needed (`PromptVersion`, `get_current_time`, `storage`,
  `HTTPException` are already imported in `api.py`).

- **Directly testable acceptance criteria:** AC-4.1 through AC-4.7 above
  (every criterion maps to this endpoint unless noted otherwise).

---

## 5. Error Conditions and Edge Cases

| #   | Condition                                                                 | Expected result                                                                                              | State change?                |
| --- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ---------------------------- |
| E-1 | List versions for a prompt that was never updated.                        | `200` with `{"versions": [], "total": 0}`.                                                                    | None.                        |
| E-2 | Fetch version 1 of a prompt that was never updated.                       | `404` — `{"detail": "Version not found"}`.                                                                    | None.                        |
| E-3 | `version_number` is `0` or negative (any version endpoint).               | `404` — `{"detail": "Version not found"}` (no such version can ever exist).                                  | None.                        |
| E-4 | `version_number` is not an integer (e.g. `abc`).                          | `422` FastAPI validation error.                                                                               | None.                        |
| E-5 | Unknown `prompt_id` on any of the three version endpoints.                | `404` — `{"detail": "Prompt not found"}`.                                                                     | None.                        |
| E-6 | Failed update (`PUT`/`PATCH` returning `400`, `404`, or `422`).           | Original error returned; version `total` unchanged.                                                           | None (no snapshot).          |
| E-7 | Restore a version whose `collection_id` references a deleted collection.  | `400` — `{"detail": "Collection not found"}`; prompt unchanged; version `total` unchanged.                   | None (no snapshot).          |
| E-8 | Restore the most recently saved version.                                  | Allowed; behaves like any other restore (snapshots current state first).                                     | One snapshot; fields updated. |
| E-9 | Restore the same version twice in a row.                                  | Both calls return `200`; each appends exactly one snapshot, so `total` grows by 2 overall.                    | One snapshot per call.       |
| E-10 | Delete a prompt that has saved versions.                                 | `204`; afterwards all version endpoints for that prompt return `404 "Prompt not found"` (history removed).    | History deleted with prompt. |
| E-11 | Restored content contains `{{variables}}`.                               | Content is restored verbatim; restore performs no template rendering or variable validation.                  | Fields updated.              |
| E-12 | Restore when the version's field values equal the current values.        | Still succeeds (`200`) and still snapshots the current state first; restore is not optimized away.            | One snapshot.                |

### Notes on consistency with existing behavior

- All error bodies use the existing FastAPI format `{"detail": "..."}`; no
  new error format is introduced.
- The `400` validation on restore (E-7) mirrors the collection-existence
  checks already performed by `POST /prompts`, `PUT`, and `PATCH`, and reuses
  their exact detail message.
- Steps 1–3 of the restore processing order run **before** any write, so no
  failed restore ever mutates state or creates a snapshot.

---

## 6. Testing Requirements (for Module 3)

Per project rules, the feature is not complete until tests pass. Add tests to
`backend/tests/test_api.py` (new `TestVersions` class is consistent with the
existing layout), reusing the `client`, `clear_storage`, `sample_prompt_data`,
and `sample_collection_data` fixtures from `tests/conftest.py`.

Minimum new test cases:

1. Restore happy path returns `200` and the pre-update field values (AC-4.1).
2. Restore appends a snapshot of the replaced state (AC-4.2).
3. Restore preserves `id`/`created_at` and refreshes `updated_at` (AC-4.3).
4. Restore unknown prompt → `404 "Prompt not found"` (AC-4.5).
5. Restore unknown version → `404 "Version not found"` (AC-4.6).
6. Restore with deleted collection → `400 "Collection not found"` and prompt
   unchanged (E-7).
7. Failed `PUT` (e.g. empty title → `422`) creates no snapshot (AC-1.4).

Existing tests that must keep passing unchanged (they already pin the
codified behavior): `test_version_history_created_on_update`,
`test_get_specific_version`, `test_versions_not_found`.
