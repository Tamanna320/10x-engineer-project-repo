/**
 * Prompt-related API helpers for the PromptLab frontend.
 *
 * Every function maps one-to-one to an endpoint defined in
 * `backend/app/api.py` and documented in `docs/API_REFERENCE.md`.
 * All HTTP communication goes through the shared helpers in
 * `./client.js`, which handle base URL, JSON serialization, and
 * consistent error handling via `ApiError`.
 *
 * Errors are never caught here — the `ApiError` thrown by `client.js`
 * propagates to the calling page/component so it can render the
 * appropriate error UI (see specs/frontend.md §5.2).
 */

import { apiGet, apiPost, apiPut, apiPatch, apiDelete } from "./client";

/**
 * @typedef {Object} Prompt
 * @property {string} id - Server-generated UUID4.
 * @property {string} title - Prompt title (1–200 chars).
 * @property {string} content - Prompt text; may contain `{{variable}}` placeholders.
 * @property {string|null} description - Optional summary (max 500 chars).
 * @property {string|null} collection_id - Owning collection ID, or null.
 * @property {string[]} tags - Tags for categorization and filtering.
 * @property {string} created_at - Creation timestamp (UTC ISO 8601).
 * @property {string} updated_at - Last update timestamp (UTC ISO 8601).
 */

/**
 * @typedef {Object} PromptCreateData
 * @property {string} title - Prompt title (1–200 chars).
 * @property {string} content - Prompt text (min 1 char).
 * @property {string|null} [description] - Optional summary (max 500 chars).
 * @property {string|null} [collection_id] - Owning collection ID.
 * @property {string[]} [tags] - Tags (defaults to [] server-side).
 */

/**
 * @typedef {PromptCreateData} PromptUpdateData Full-replacement body for PUT.
 */

/**
 * @typedef {Object} PromptPatchData
 * @property {string} [title] - New title (1–200 chars).
 * @property {string} [content] - New content (min 1 char).
 * @property {string|null} [description] - New description (max 500 chars).
 * @property {string|null} [collection_id] - New collection ID (null to unassign).
 * @property {string[]} [tags] - Replacement tag list.
 */

/**
 * @typedef {Object} PromptListResponse
 * @property {Prompt[]} prompts - Matching prompts (newest first).
 * @property {number} total - Number of matching prompts.
 */

/**
 * @typedef {Object} PromptTestResponse
 * @property {string} prompt_id - ID of the rendered prompt.
 * @property {string} rendered_content - Content with variables substituted.
 */

/**
 * @typedef {Object} PromptVersion
 * @property {number} version - Sequential version number (starts at 1).
 * @property {string} title - Title at time of snapshot.
 * @property {string} content - Content at time of snapshot.
 * @property {string|null} description - Description at time of snapshot.
 * @property {string|null} collection_id - Collection ID at time of snapshot.
 * @property {string[]} tags - Tags at time of snapshot.
 * @property {string} saved_at - When the snapshot was saved (UTC ISO 8601).
 */

/**
 * @typedef {Object} VersionListResponse
 * @property {PromptVersion[]} versions - Saved snapshots (oldest first).
 * @property {number} total - Number of saved versions.
 */

/**
 * @typedef {Object} PromptListFilters
 * @property {string|null} [collection_id] - Filter by collection ID.
 * @property {string|null} [search] - Case-insensitive substring match on
 *   title and description.
 * @property {string|null} [tag] - Exact (case-sensitive) single-tag filter.
 */

/**
 * Fetch the list of prompts, optionally filtered.
 *
 * Maps to `GET /prompts` (`list_prompts` in `backend/app/api.py`).
 *
 * The params object is passed directly to `apiGet`, which uses
 * `buildQueryString` from `client.js` to serialize it. Only the three
 * filters defined by the frontend specification are supported:
 * `collection_id`, `search`, and `tag`. The `tags` multi-tag parameter
 * exists in the backend but is explicitly excluded by
 * `specs/frontend.md` and is therefore not accepted here.
 *
 * `buildQueryString` automatically omits keys whose values are `null`,
 * `undefined`, or an empty string, so only the filters the caller
 * actually provides are sent to the backend.
 *
 * @param {PromptListFilters} [filters] - Optional filter values. All
 *   keys are optional; omit the whole argument to fetch every prompt.
 * @returns {Promise<PromptListResponse>} The matching prompts and total count.
 * @throws {ApiError} On non-2xx responses or network failures.
 */
export function getPrompts(filters) {
  return apiGet("/prompts", filters);
}

/**
 * Retrieve a single prompt by its ID.
 *
 * Maps to `GET /prompts/{prompt_id}` (`get_prompt` in
 * `backend/app/api.py`). Returns the full prompt including
 * server-generated `id`, `created_at`, and `updated_at`.
 *
 * @param {string} promptId - The prompt's unique ID.
 * @returns {Promise<Prompt>} The prompt with the given ID.
 * @throws {ApiError} 404 if no prompt exists with the given ID.
 */
export function getPrompt(promptId) {
  return apiGet(`/prompts/${promptId}`);
}

/**
 * Create a new prompt.
 *
 * Maps to `POST /prompts` (`create_prompt` in `backend/app/api.py`).
 * The server assigns `id`, `created_at`, and `updated_at`.
 *
 * @param {PromptCreateData} data - The prompt fields to create.
 * @returns {Promise<Prompt>} The newly created prompt.
 * @throws {ApiError} 400 if `collection_id` references a non-existent
 *   collection; 422 on validation failure.
 */
export function createPrompt(data) {
  return apiPost("/prompts", data);
}

/**
 * Fully replace an existing prompt (PUT semantics).
 *
 * Maps to `PUT /prompts/{prompt_id}` (`update_prompt` in
 * `backend/app/api.py`). All editable fields are replaced with the
 * values in `data`; omitted optional fields fall back to server
 * defaults. The previous state is saved as a version automatically.
 *
 * @param {string} promptId - The prompt's unique ID.
 * @param {PromptUpdateData} data - The full set of replacement fields.
 * @returns {Promise<Prompt>} The updated prompt.
 * @throws {ApiError} 404 if not found; 400 for a bad `collection_id`;
 *   422 on validation failure.
 */
export function updatePrompt(promptId, data) {
  return apiPut(`/prompts/${promptId}`, data);
}

/**
 * Partially update an existing prompt (PATCH semantics).
 *
 * Maps to `PATCH /prompts/{prompt_id}` (`patch_prompt` in
 * `backend/app/api.py`). Only the fields present in `data` are
 * changed; omitted fields keep their current values. Sending
 * `collection_id: null` unassigns the prompt from its collection.
 * The previous state is saved as a version automatically.
 *
 * @param {string} promptId - The prompt's unique ID.
 * @param {PromptPatchData} data - The fields to change.
 * @returns {Promise<Prompt>} The updated prompt.
 * @throws {ApiError} 404 if not found; 400 for a bad `collection_id`;
 *   422 on validation failure.
 */
export function patchPrompt(promptId, data) {
  return apiPatch(`/prompts/${promptId}`, data);
}

/**
 * Delete a prompt by its ID.
 *
 * Maps to `DELETE /prompts/{prompt_id}` (`delete_prompt` in
 * `backend/app/api.py`). The prompt's version history is deleted
 * along with it. Resolves to `null` on success (204 No Content).
 *
 * @param {string} promptId - The prompt's unique ID.
 * @returns {Promise<null>} Resolves to `null` on success.
 * @throws {ApiError} 404 if no prompt exists with the given ID.
 */
export function deletePrompt(promptId) {
  return apiDelete(`/prompts/${promptId}`);
}

/**
 * Render a prompt template with test variable values.
 *
 * Maps to `POST /prompts/{prompt_id}/test` (`test_prompt` in
 * `backend/app/api.py`). The request body follows the
 * `PromptTestRequest` schema: `{ "variables": { ... } }`.
 *
 * @param {string} promptId - The prompt's unique ID.
 * @param {Object.<string, string>} variables - A mapping of template
 *   variable names (without `{{ }}`) to the values to substitute.
 * @returns {Promise<PromptTestResponse>} The rendered result.
 * @throws {ApiError} 404 if the prompt is not found; 400 if values are
 *   missing for one or more template variables.
 */
export function testPrompt(promptId, variables) {
  return apiPost(`/prompts/${promptId}/test`, { variables });
}

/**
 * List the saved version history of a prompt.
 *
 * Maps to `GET /prompts/{prompt_id}/versions` (`list_versions` in
 * `backend/app/api.py`). Versions are returned in the order they were
 * saved (oldest first). A prompt that has never been updated returns
 * an empty list.
 *
 * @param {string} promptId - The prompt's unique ID.
 * @returns {Promise<VersionListResponse>} The saved versions and total count.
 * @throws {ApiError} 404 if no prompt exists with the given ID.
 */
export function getVersions(promptId) {
  return apiGet(`/prompts/${promptId}/versions`);
}

/**
 * Restore a prompt to a previously saved version.
 *
 * Maps to `POST /prompts/{prompt_id}/versions/{version_number}/restore`
 * (`restore_prompt_version` in `backend/app/api.py`). Before
 * restoring, the prompt's current state is saved as a new version so
 * the restore can be undone.
 *
 * @param {string} promptId - The prompt's unique ID.
 * @param {number} versionNumber - The sequential version number to
 *   restore (starts at 1).
 * @returns {Promise<Prompt>} The restored prompt.
 * @throws {ApiError} 404 if the prompt or version is not found; 400 if
 *   the version's `collection_id` references a collection that no
 *   longer exists.
 */
export function restoreVersion(promptId, versionNumber) {
  return apiPost(`/prompts/${promptId}/versions/${versionNumber}/restore`);
}
