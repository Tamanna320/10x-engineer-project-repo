import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import PromptDetail from "../components/PromptDetail.jsx";
import { getPrompt } from "../api/prompts.js";
import { getCollections } from "../api/collections.js";

/**
 * Prompt Detail page.
 *
 * Reads the prompt id from the `/prompts/:id` route param, fetches the
 * full prompt via `getPrompt`, and renders the existing `PromptDetail`
 * component on success. While loading, a `LoadingSpinner` is shown. On
 * a 404 the user sees "Prompt not found." with a link back to the
 * Prompt List; on other failures an `ErrorBanner` shows "Failed to
 * load prompt." with a Retry button (see `specs/frontend.md` §5.1 and
 * §5.2).
 *
 * The collections list is also fetched on mount (via the existing
 * `getCollections`) so that the prompt's `collection_id` can be
 * resolved to a human-readable collection name for display. A
 * collections-fetch failure does not block rendering the prompt; in
 * that case the detail falls back to the raw `collection_id` (see
 * `PromptDetail.jsx`).
 *
 * Version history, template testing, and detail-page delete are
 * handled by separate components/tasks and are intentionally not
 * included here.
 *
 * @returns {JSX.Element} The Prompt Detail page.
 */
function PromptDetailPage() {
  const { id } = useParams();

  const [prompt, setPrompt] = useState(null);
  const [loadedId, setLoadedId] = useState(null);
  const [error, setError] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const [collections, setCollections] = useState([]);

  // Loading is derived from whether the current id has been loaded yet.
  // This avoids calling setState synchronously inside the effect body
  // (which would trigger the react-hooks/set-state-in-effect rule) while
  // still showing a spinner whenever the id changes or a retry starts.
  const loading = loadedId !== id;
  useEffect(() => {
    let active = true;
    getPrompt(id)
      .then((data) => {
        if (!active) return;
        setPrompt(data);
        setLoadedId(id);
        setError(null);
      })
      .catch((err) => {
        if (!active) return;
        setPrompt(null);
        setLoadedId(id);
        setError(err.status === 404 ? "not_found" : "load_failed");
      });

    return () => {
      active = false;
    };
    // Re-fetch when the id route param changes or a retry is requested.
  }, [id, refreshKey]);

  // Fetch collections once on mount to resolve collection_id → name.
  // A failure is non-fatal here — it only means the collection name
  // cannot be resolved, so the prompt detail falls back to the id.
  useEffect(() => {
    let active = true;
    getCollections()
      .then((data) => {
        if (!active) return;
        setCollections(data.collections ?? []);
      })
      .catch(() => {
        if (!active) return;
        // Keep collections empty so the detail falls back to the id.
        setCollections([]);
      });

    return () => {
      active = false;
    };
  }, []);

  const handleRetry = () => {
    // Reset loadedId so the derived loading flag becomes true again,
    // then bump refreshKey to re-trigger the fetch effect.
    setLoadedId(null);
    setRefreshKey((value) => value + 1);
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error === "not_found") {
    return (
      <div>
        <ErrorBanner message="Prompt not found." />
        <p>
          <Link to="/prompts">Back to Prompts</Link>
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <ErrorBanner
        message="Failed to load prompt."
        onRetry={handleRetry}
      />
    );
  }

  // Resolve the collection id to a human-readable name. If the
  // collections fetch failed or the collection was deleted, fall back
  // to the raw collection_id so the field still shows something.
  const resolvedCollectionName = prompt.collection_id
    ? collections.find((c) => c.id === prompt.collection_id)?.name
    : undefined;

  return (
    <div>
      <PromptDetail
        prompt={prompt}
        collectionName={resolvedCollectionName}
      />
    </div>
  );
}

export default PromptDetailPage;

