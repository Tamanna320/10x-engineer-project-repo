/**
 * Shared API client for the PromptLab frontend.
 *
 * Provides a configurable base URL, a thin `fetch` wrapper with
 * consistent JSON handling, and a uniform error type so that feature
 * modules (`prompts.js`, `collections.js`) can call the backend through
 * one consistent interface.
 *
 * The API base URL is read from the `VITE_API_BASE_URL` environment
 * variable, defaulting to `http://localhost:8000`.
 */

/**
 * Base URL for all API requests.
 *
 * Reads `VITE_API_BASE_URL` from the Vite environment, falling back to
 * `http://localhost:8000` when the variable is not set.
 *
 * @type {string}
 */
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Error thrown for non-2xx API responses or network failures.
 *
 * Carries the HTTP status code and the raw `detail` payload returned by
 * the backend so callers can distinguish application errors (e.g. 404
 * "Prompt not found") from validation errors (422 with a `detail` array
 * of field-level messages). Network failures use a status of `0`.
 */
class ApiError extends Error {
  /**
   * @param {string} message - Human-readable error summary.
   * @param {number} status - HTTP status code (0 for network failures).
   * @param {string|Array<{loc: (string|number)[], msg: string, type: string}>} [detail]
   *   The raw `detail` value from the response body — a string for
   *   application errors or an array of validation error objects for
   *   422 responses. Omitted for network failures.
   */
  constructor(message, status, detail) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    if (detail !== undefined) {
      this.detail = detail;
    }
  }
}

/**
 * Build a query string from a params object, omitting keys whose values
 * are `null`, `undefined`, or empty strings.
 *
 * @param {Object.<string, string|number|null|undefined>} [params]
 *   Key/value pairs to serialize. The falsy-ish values listed above are
 *   skipped; all other values are coerced to strings and URL-encoded.
 * @returns {string} A query string beginning with "?" when at least one
 *   param survives filtering, or an empty string when none do.
 *
 * @example
 * buildQueryString({ search: "email", tag: null, collection_id: "c1" });
 * // → "?search=email&collection_id=c1"
 */
function buildQueryString(params = {}) {
  const entries = Object.entries(params).filter(
    ([, value]) => value !== null && value !== undefined && value !== "",
  );

  if (entries.length === 0) {
    return "";
  }

  const search = new URLSearchParams();
  for (const [key, value] of entries) {
    search.append(key, String(value));
  }
  return `?${search.toString()}`;
}

/**
 * Extract a human-readable message from an API error response body.
 *
 * Application errors return `{"detail": "..."}` (a string), while
 * validation errors return `{"detail": [...]}` (an array). When the
 * body cannot be parsed or has no `detail`, a fallback message based on
 * the status code is used.
 *
 * @param {Response} response - The fetch Response object.
 * @param {number} status - The HTTP status code.
 * @returns {Promise<{message: string, detail?: string|Array}>} The
 *   extracted message and, when present, the raw detail payload.
 */
async function parseErrorBody(response, status) {
  let detail;

  try {
    const body = await response.json();
    if (body && "detail" in body) {
      detail = body.detail;
    }
  } catch {
    // Response had no JSON body (or it was unparseable); fall back below.
  }

  let message;
  if (typeof detail === "string") {
    message = detail;
  } else if (Array.isArray(detail) && detail.length > 0) {
    message = detail
      .map((err) => (err && err.msg ? err.msg : String(err)))
      .join("; ");
  } else {
    message = `Request failed with status ${status}`;
  }

  return { message, detail };
}

/**
 * Core fetch wrapper that performs a JSON request against the API and
 * returns the parsed response body.
 *
 * Automatically prepends {@link BASE_URL} to `path`, sets the
 * `Content-Type: application/json` header for requests with a body, and
 * converts non-2xx responses into {@link ApiError} instances with a
 * consistent shape. `204 No Content` responses resolve to `null`.
 *
 * @param {string} path - The API path (e.g. `/prompts` or
 *   `/prompts/123/versions`). Must begin with a leading slash.
 * @param {Object} [options] - Request options.
 * @param {string} [options.method="GET"] - HTTP method.
 * @param {Object|null} [options.body] - JSON-serializable request body.
 * @param {string} [options.query] - An optional pre-built query string
 *   (from {@link buildQueryString}) appended to the path.
 * @returns {Promise<Object|null>} The parsed JSON response, or `null`
 *   for `204 No Content` responses.
 * @throws {ApiError} On non-2xx responses or network failures.
 */
async function request(path, options = {}) {
  const { method = "GET", body = null, query = "" } = options;

  const headers = {};
  if (body !== null) {
    headers["Content-Type"] = "application/json";
  }

  let response;
  try {
    response = await fetch(`${BASE_URL}${path}${query}`, {
      method,
      headers,
      body: body !== null ? JSON.stringify(body) : null,
    });
  } catch {
    throw new ApiError("Network error — unable to reach the API.", 0);
  }

  if (response.status === 204) {
    return null;
  }

  if (!response.ok) {
    const { message, detail } = await parseErrorBody(
      response,
      response.status,
    );
    throw new ApiError(message, response.status, detail);
  }

  // Successful response — parse the JSON body.
  try {
    return await response.json();
  } catch {
    // Non-JSON success response (unexpected for this API).
    return null;
  }
}

/**
 * Perform a GET request with optional query parameters.
 *
 * @param {string} path - The API path, e.g. `/prompts`.
 * @param {Object.<string, string|number|null|undefined>} [params]
 *   Query parameters. `null`, `undefined`, and empty-string values are
 *   omitted.
 * @returns {Promise<Object|null>} The parsed JSON response.
 * @throws {ApiError} On non-2xx responses or network failures.
 */
export function apiGet(path, params) {
  return request(path, { query: buildQueryString(params) });
}

/**
 * Perform a POST request with a JSON body.
 *
 * @param {string} path - The API path, e.g. `/prompts`.
 * @param {Object|null} [body] - The JSON-serializable request body.
 * @returns {Promise<Object|null>} The parsed JSON response.
 * @throws {ApiError} On non-2xx responses or network failures.
 */
export function apiPost(path, body = null) {
  return request(path, { method: "POST", body });
}

/**
 * Perform a PUT request with a JSON body.
 *
 * @param {string} path - The API path, e.g. `/prompts/123`.
 * @param {Object|null} [body] - The JSON-serializable request body.
 * @returns {Promise<Object|null>} The parsed JSON response.
 * @throws {ApiError} On non-2xx responses or network failures.
 */
export function apiPut(path, body = null) {
  return request(path, { method: "PUT", body });
}

/**
 * Perform a PATCH request with a JSON body.
 *
 * @param {string} path - The API path, e.g. `/prompts/123`.
 * @param {Object|null} [body] - The JSON-serializable request body.
 * @returns {Promise<Object|null>} The parsed JSON response.
 * @throws {ApiError} On non-2xx responses or network failures.
 */
export function apiPatch(path, body = null) {
  return request(path, { method: "PATCH", body });
}

/**
 * Perform a DELETE request.
 *
 * @param {string} path - The API path, e.g. `/prompts/123`.
 * @returns {Promise<null>} Resolves to `null` on success (204 No Content).
 * @throws {ApiError} On non-2xx responses or network failures.
 */
export function apiDelete(path) {
  return request(path, { method: "DELETE" });
}

export { BASE_URL, ApiError, request, buildQueryString };
