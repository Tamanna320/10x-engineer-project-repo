# Refactor Note: Prompt Version Restore

## Summary

A small, safe cleanup of the `restore_prompt_version` endpoint in
`backend/app/api.py`. No behavior, error messages, or API contract were
changed.

## Code Smell Addressed

**Unnecessary temporary variables / redundant intermediate assignments.**

The original implementation introduced three intermediate variables that were
each referenced exactly once before going out of scope:

| Variable            | Used for                                  |
| ------------------- | ----------------------------------------- |
| `collection`        | Held the result of `storage.get_collection()` only to check truthiness. |
| `old_version`       | Held a `PromptVersion` object only to pass it to `storage.save_version()`. |
| `restored_prompt`   | Held the rebuilt `Prompt` only to pass it to `storage.update_prompt()`. |

These added visual noise without improving readability.

## Commits

| Label                  | Commit   |
| ---------------------- | -------- |
| Before refactor        | `89d9032` |
| After refactor         | `71f68a3` |

## Changes Made

### 1. Removed the temporary `collection` variable

The collection-existence check used a nested two-level `if` with an
intermediate variable:

```python
# Before
if version.collection_id is not None:
    collection = storage.get_collection(version.collection_id)
    if not collection:
        raise HTTPException(status_code=400, detail="Collection not found")
```

Simplified to a single flat condition:

```python
# After
if version.collection_id is not None and not storage.get_collection(version.collection_id):
    raise HTTPException(status_code=400, detail="Collection not found")
```

### 2. Removed the temporary `old_version` variable

The snapshot was built in a separate variable, then passed to
`storage.save_version()`. Inlined the `PromptVersion` constructor directly
into the `save_version` call:

```python
# Before
old_version = PromptVersion(
    version=len(storage.get_versions(prompt_id)) + 1,
    title=existing.title,
    ...
)
storage.save_version(prompt_id, old_version)

# After
storage.save_version(prompt_id, PromptVersion(
    version=len(storage.get_versions(prompt_id)) + 1,
    title=existing.title,
    ...
))
```

### 3. Removed the temporary `restored_prompt` variable

The rebuilt prompt was assigned to a variable, then immediately returned via
`storage.update_prompt()`. Inlined the `Prompt` constructor directly into the
return statement:

```python
# Before
restored_prompt = Prompt(
    id=existing.id,
    title=version.title,
    ...
    updated_at=get_current_time()
)
return storage.update_prompt(prompt_id, restored_prompt)

# After
return storage.update_prompt(prompt_id, Prompt(
    id=existing.id,
    title=version.title,
    ...
    updated_at=get_current_time()
))
```

## Public Interface — Unchanged

The refactor introduced **no API changes**:

| Aspect                        | Before | After |
| ----------------------------- | ------ | ----- |
| HTTP method                   | `POST` | `POST` |
| Endpoint path                 | `/prompts/{prompt_id}/versions/{version_number}/restore` | same |
| Request parameters            | `prompt_id` (path), `version_number` (path), no body | same |
| Success response              | `200` → `Prompt` | same |
| 404 — prompt not found        | `{"detail": "Prompt not found"}` | same |
| 404 — version not found       | `{"detail": "Version not found"}` | same |
| 400 — collection not found    | `{"detail": "Collection not found"}` | same |

## Observable Behavior — Unchanged

All runtime behavior is identical, including:

- **Validation order:** prompt existence → version existence → collection
  existence. No state changes occur before all checks pass.
- **Version snapshotting:** the current prompt state is saved as a new
  `PromptVersion` before the restore overwrites it.
- **Field restoration:** `title`, `content`, `description`, `collection_id`,
  and `tags` are copied from the selected version.
- **Identity preservation:** `id` and `created_at` are preserved from the
  existing prompt.
- **Timestamp refresh:** `updated_at` is set to `get_current_time()`.
- **Repeatable restores:** each call appends exactly one new snapshot.

## Verification

The full test suite was run after the refactor:

```
pytest tests/ -v --cov=app --cov-report=term-missing
```

Results:

- **186 passed**, 0 failed
- **Coverage: 100%** across all modules (`api.py`, `models.py`,
  `storage.py`, `utils.py`, `__init__.py`)
