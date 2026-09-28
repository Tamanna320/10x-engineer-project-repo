/**
 * Collection-related API helpers for the PromptLab frontend.
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

import { apiGet, apiPost, apiDelete } from "./client";

/**
 * @typedef {Object} Collection
 * @property {string} id - Server-generated UUID4.
 * @property {string} name - Collection name (1–100 chars).
 * @property {string|null} description - Optional summary (max 500 chars).
 * @property {string} created_at - Creation timestamp (UTC ISO 8601).
 */

/**
 * @typedef {Object} CollectionCreateData
 * @property {string} name - Collection name (1–100 chars).
 * @property {string|null} [description] - Optional summary (max 500 chars).
 */

/**
 * @typedef {Object} CollectionListResponse
 * @property {Collection[]} collections - Every stored collection.
 * @property {number} total - Number of stored collections.
 */

/**
 * Fetch the list of all collections.
 *
 * Maps to `GET /collections` (`list_collections` in
 * `backend/app/api.py`). Used to populate the collection filter
 * dropdown on the prompt list/form screens and the collection list on
 * the Collection List screen.
 *
 * @returns {Promise<CollectionListResponse>} The stored collections
 *   and total count.
 * @throws {ApiError} On non-2xx responses or network failures.
 */
export function getCollections() {
  return apiGet("/collections");
}

/**
 * Create a new collection.
 *
 * Maps to `POST /collections` (`create_collection` in
 * `backend/app/api.py`). The server assigns `id` and `created_at`
 * automatically.
 *
 * @param {CollectionCreateData} data - The collection fields to create.
 * @returns {Promise<Collection>} The newly created collection.
 * @throws {ApiError} 422 on validation failure (e.g. missing or
 *   invalid `name`).
 */
export function createCollection(data) {
  return apiPost("/collections", data);
}

/**
 * Delete a collection by its ID.
 *
 * Maps to `DELETE /collections/{collection_id}` (`delete_collection`
 * in `backend/app/api.py`). All prompts belonging to the collection
 * are first unassigned (their `collection_id` set to `null`) rather
 * than deleted; the collection itself is then removed. Resolves to
 * `null` on success (204 No Content).
 *
 * @param {string} collectionId - The collection's unique ID.
 * @returns {Promise<null>} Resolves to `null` on success.
 * @throws {ApiError} 404 if no collection exists with the given ID.
 */
export function deleteCollection(collectionId) {
  return apiDelete(`/collections/${collectionId}`);
}
