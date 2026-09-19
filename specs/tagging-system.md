# Feature Specification: Tagging System

| Field           | Value                                                                                            |
| --------------- | ------------------------------------------------------------------------------------------------ |
| Feature         | Prompt Tagging & Tag Discovery                                                                   |
| Status          | Draft — ready for implementation                                                                 |
| Target release  | 0.2.0 (current: 0.1.0)                                                                            |
| Source of truth | `backend/app/{api,models,storage,utils}.py`, `backend/tests/`, `docs/API_REFERENCE.md`, `README.md` |

---

## 1. Overview and Goals

### 1.1 What exists today (verified against the codebase)

- `Prompt` already has `tags: List[str]` (default `[]`) via `PromptBase`
  (`models.py`). Tags are stored **verbatim**: any string, any case,
  duplicates allowed, no normalization.
- `PUT` replaces `tags` wholesale; omitting `tags` in a PUT resets it to
  `[]`. `PATCH` replaces `tags` only if the field is sent (`PromptPatch.tags`
  is `Optional[List[str]]`). Both save a version snapshot per
  `specs/prompt-versions.md`.
- `GET /prompts?tag=<t>` filters by a **single** tag using an exact,
  **case-sensitive** membership test (`filter_prompts_by_tag` in `utils.py`).
  Filters combine cumulatively in the order: `collection_id` → `search` →
  `tag`, then sort by `created_at` descending.
- Covered by existing tests `test_create_prompt_with_tags` and
  `test_filter_prompts_by_tag`.

### 1.2 Goals

- **G-1.** Formalize the existing tag storage and single-tag filter contract
  (no code change).
- **G-2.** **New:** multi-tag filtering — `GET /prompts?tags=a,b` returns
  prompts matching **any** of the given tags; combinable (AND) with the
  existing filters.
- **G-3.** **New:** tag discovery — `GET /tags` lists every distinct tag in
  the system with the number of prompts using it, for UI pickers/tag clouds.
- **G-4.** No breaking changes: no modified model fields, no changed
  behavior for existing parameters or endpoints.

### 1.3 Out of scope

- Tag add/remove endpoints (`POST /prompts/{id}/tags`) — `PATCH` already
  covers tag mutation; avoiding duplicate mutation paths.
- Tag normalization (lowercasing/trimming on write), tag renaming/deletion
  across prompts, tag descriptions, per-collection tags, pagination.

---

## 2. User Stories with testable Acceptance Criteria

**Shared scenario for ACs (create in order):**

| Prompt | Title            | Tags                    |
| ------ | ---------------- | ----------------------- |
| A      | `Python Basics`  | `["python", "beginner"]` |
| B      | `Advanced Python`| `["python", "advanced"]` |
| C      | `Pasta Recipe`   | `["cooking"]`            |

### US-1 — Tag prompts on create/update (existing, formalized)

> As a prompt author, I attach tags so I can organize prompts.

- **AC-1.1:** `POST /prompts` with `tags: ["coding", "review"]` → `201`, and
  the response body contains `"tags": ["coding", "review"]` verbatim.
- **AC-1.2:** `POST /prompts` without `tags` → `201`, response `"tags": []`.
- **AC-1.3:** `PATCH /prompts/{id}` with `{"tags": ["a", "b"]}` → `200` and
  `tags == ["a", "b"]`; a PATCH body without `tags` leaves tags unchanged.

### US-2 — Filter by one tag (existing, formalized)

> As a user, I filter prompts by a tag to find relevant prompts.

- **AC-2.1:** Given scenario A–C, `GET /prompts?tag=python` → `200`,
  `total == 2`, titles `{Python Basics, Advanced Python}`.
- **AC-2.2:** `GET /prompts?tag=Python` (capital P) → `200`, `total == 0`
  (case-sensitive).

### US-3 — Filter by multiple tags (**new**)

> As a user, I filter by several tags at once to broaden or combine searches.

- **AC-3.1:** `GET /prompts?tags=beginner,advanced` → `200`, `total == 2`
  (A and B — match ANY), C excluded.
- **AC-3.2 (AND with `tag`):** `GET /prompts?tag=python&tags=beginner` →
  `200`, `total == 1`, only `Python Basics`.
- **AC-3.3:** `GET /prompts?tags=nonexistent` → `200`, `total == 0`.

### US-4 — Discover all tags (**new**)

> As a user, I want to see all tags in the system with usage counts.

- **AC-4.1:** Given scenario A–C, `GET /tags` → `200` with body:
  ```json
  {"tags": [{"tag": "advanced", "count": 1}, {"tag": "beginner", "count": 1},
            {"tag": "cooking", "count": 1}, {"tag": "python", "count": 2}],
   "total": 4}
  ```
- **AC-4.2:** With no prompts stored, `GET /tags` → `200`,
  `{"tags": [], "total": 0}`.
- **AC-4.3:** After `DELETE /prompts/{B_id}` (204), `GET /tags` shows
  `python` with `count == 1` and no `advanced` entry.

---

## 3. Data Model Changes

### 3.1 Existing models — unchanged

`Prompt.tags: List[str]` stays as-is. No constraint, normalization, or
deduplication is added on write.

### 3.2 New response models (add to `models.py`, Response Models section)

```python
class TagCount(BaseModel):
    """One distinct tag and how many prompts use it."""
    tag: str
    count: int


class TagList(BaseModel):
    """All distinct tags with usage counts."""
    tags: List[TagCount]
    total: int
```

### 3.3 New helpers (add to `utils.py`; `Dict`/`List` already imported)

```python
def filter_prompts_by_tags(prompts: List[Prompt], tags: List[str]) -> List[Prompt]:
    """Keep prompts carrying at least one of the given tags (exact, case-sensitive)."""
    return [p for p in prompts if any(t in p.tags for t in tags)]


def count_tags(prompts: List[Prompt]) -> Dict[str, int]:
    """Map each tag to the number of distinct prompts carrying it."""
    counts: Dict[str, int] = {}
    for p in prompts:
        for t in set(p.tags):  # duplicate tags on one prompt count once
            counts[t] = counts.get(t, 0) + 1
    return counts
```

### 3.4 Storage changes

None — both features compose `storage.get_all_prompts()`.

### 3.5 Normative rules

1. Tags are stored verbatim (no trimming/casing on write).
2. All tag matching is exact and case-sensitive.
3. The `tags` query parameter is comma-separated; parsing strips whitespace
   around segments, drops empty segments, and dedupes. If nothing remains,
   the parameter is ignored (no filtering).
4. `GET /tags` counts each prompt **once per tag**, sorts by tag ascending
   (lexicographic/Unicode code-point), and sets `total` to the number of
   distinct tags.
5. Within `tags`, matching is ANY; across `collection_id`/`search`/`tag`/
   `tags`, filters combine cumulatively (AND), applied in that order, then
   sorted by `created_at` descending (existing pipeline).

---

## 4. API Endpoints

### 4.1 Tag writes on `POST` / `PUT` / `PATCH /prompts[/{id}]` (existing — no change)

- **Purpose:** set/replace a prompt's `tags` as part of normal writes.
- **Shapes/statuses:** unchanged (see `docs/API_REFERENCE.md`); `201`/`200`,
  `400`, `404`, `422` as today. Tag changes via PUT/PATCH create version
  snapshots per `specs/prompt-versions.md`.
- **Testable AC:** AC-1.1–AC-1.3.

### 4.2 `GET /prompts` (existing — one additive query parameter)

- **Purpose:** list/filter prompts; extended with multi-tag filtering.
- **Request (query, all optional, all strings):** `collection_id`, `search`,
  `tag` (unchanged) **+ new `tags`**: comma-separated list, match ANY,
  parsed per rule 3.5.3.
- **Response (`200`, `PromptList`):**
  `{"prompts": [Prompt, ...], "total": int}`, sorted `created_at` desc.
- **Status codes:** `200` (including empty results). No 404/400 paths; all
  parameters are strings, so no 422 path is introduced.
- **Implementation:** add `tags: Optional[str] = None` to `list_prompts`
  and, after the existing `tag` filter:
  ```python
  if tags:
      parsed = [t.strip() for t in tags.split(",") if t.strip()]
      if parsed:
          prompts = filter_prompts_by_tags(prompts, parsed)
  ```
- **Testable ACs:** AC-2.1 (regression), AC-3.1, AC-3.2, AC-3.3.

### 4.3 `GET /tags` (**NEW**)

- **Purpose:** list every distinct tag across all prompts with usage counts.
- **Request:** no parameters, no body.
- **Response (`200`, `TagList`):**
  `{"tags": [{"tag": str, "count": int}, ...], "total": int}`, sorted by
  `tag` ascending; `total` = number of distinct tags.
- **Status codes:** `200` only (empty system → `{"tags": [], "total": 0}`).
- **Implementation:** new `# ============== Tag Endpoints ==============`
  section in `api.py` (between Prompt and Collection sections — no path
  conflicts, verified against existing routes):
  ```python
  @app.get("/tags", response_model=TagList)
  def list_tags():
      counts = count_tags(storage.get_all_prompts())
      tag_items = [TagCount(tag=t, count=c) for t, c in sorted(counts.items())]
      return TagList(tags=tag_items, total=len(tag_items))
  ```
  (`TagCount`/`TagList` need adding to the `app.models` import in `api.py`.)
- **Testable ACs:** AC-4.1, AC-4.2, AC-4.3.

---

## 5. Error Conditions and Edge Cases

| #   | Condition                                                        | Expected result                                                                                  |
| --- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| E-1 | `tag`/`tags` match nothing.                                      | `200` with `{"prompts": [], "total": 0}`.                                                         |
| E-2 | Case mismatch (`tag=Python` vs stored `python`).                 | No match (case-sensitive, rule 3.5.2).                                                            |
| E-3 | `tags=` (empty value).                                           | Parameter ignored; unfiltered list returned.                                                       |
| E-4 | `tags= beginner ,,advanced` (spaces, empty segment).             | Equivalent to `tags=beginner,advanced` (rule 3.5.3).                                              |
| E-5 | Duplicate segments (`tags=a,a`).                                 | Same result as `tags=a`.                                                                          |
| E-6 | One prompt has a duplicated tag (`["python", "python"]`).        | Stored verbatim; prompt appears once in filters; `GET /tags` counts it once for `python`.         |
| E-7 | Prompt with `tags: []`.                                          | Never matches `tag`/`tags` filters; appears in unfiltered `GET /prompts`; contributes no `GET /tags` entries. |
| E-8 | `tag` and `tags` together.                                       | Both applied (AND): prompt must carry `tag` **and** at least one of `tags` (AC-3.2).              |
| E-9 | All four filters combined.                                       | Cumulative AND in pipeline order, then `created_at` desc sort (rule 3.5.5).                        |
| E-10 | Prompt deleted.                                                 | Its tags vanish from `GET /tags` immediately (AC-4.3).                                            |
| E-11 | Tags containing special characters (e.g. `c++`).                | Stored/matched verbatim; clients must URL-encode the query value.                                  |
| E-12 | `PUT` without `tags`.                                           | Tags reset to `[]` (existing full-replace semantics); snapshot saved per versions spec.            |

**Testing notes:** new tests go in `backend/tests/test_api.py` (e.g. a
`TestTags` class, reusing the `client`/`clear_storage` fixtures). Existing
tests `test_create_prompt_with_tags` and `test_filter_prompts_by_tag` must
pass unchanged. Minimum new tests: AC-3.1, AC-3.2, AC-3.3, AC-4.1, AC-4.2,
AC-4.3, E-4, E-6.
