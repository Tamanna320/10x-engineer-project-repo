import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import PromptForm from "../components/PromptForm.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import { getPrompt, updatePrompt } from "../api/prompts.js";
import { getCollections } from "../api/collections.js";

/**
 * Edit Prompt page.
 *
 * Reads the prompt id from the `/prompts/:id/edit` route param, fetches
 * the existing prompt via `getPrompt` (to pre-fill the form) and the
 * collections via `getCollections` (to populate the form's collection
 * dropdown), then renders the shared `PromptForm` in edit mode. On
 * submit, the form's values are sent to the backend via `updatePrompt`
 * (PUT); on success the user is navigated to that prompt's detail page.
 *
 * Loading is derived from `loadedId`/`collectionsLoaded` flags so that
 * no `setState` is called synchronously inside an effect body (per the
 * `react-hooks/set-state-in-effect` lint rule). API errors are surfaced
 * by `PromptForm` itself for submit failures (422 → field-level
 * messages, 400 → inline collection error, 404 → ErrorBanner); load
 * failures are handled here with `ErrorBanner` (see
 * `specs/frontend.md` §5.1 and §5.2).
 *
 * @returns {JSX.Element} The Edit Prompt page.
 */
function PromptEditPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [prompt, setPrompt] = useState(null);
  const [loadedId, setLoadedId] = useState(null);
  const [loadError, setLoadError] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const [collections, setCollections] = useState([]);
  const [collectionsLoaded, setCollectionsLoaded] = useState(false);
  const [collectionsError, setCollectionsError] = useState(null);
  const [collectionsRefreshKey, setCollectionsRefreshKey] = useState(0);

  const [submitting, setSubmitting] = useState(false);

  // Loading is true until both the prompt and collections have resolved
  // for the current id. Derived (not set) to satisfy the lint rule.
  const loading =
    loadedId !== id || !collectionsLoaded;

  // Fetch the prompt for the current id (and on retry).
  useEffect(() => {
    let active = true;

    getPrompt(id)
      .then((data) => {
        if (!active) return;
        setPrompt(data);
        setLoadedId(id);
        setLoadError(null);
      })
      .catch((err) => {
        if (!active) return;
        setPrompt(null);
        setLoadedId(id);
        setLoadError(err.status === 404 ? "not_found" : "load_failed");
      });

    return () => {
      active = false;
    };
  }, [id, refreshKey]);

  // Fetch collections once (and on collections retry).
  useEffect(() => {
    let active = true;

    getCollections()
      .then((data) => {
        if (!active) return;
        setCollections(data.collections ?? []);
        setCollectionsLoaded(true);
        setCollectionsError(null);
      })
      .catch(() => {
        if (!active) return;
        setCollections([]);
        setCollectionsLoaded(true);
        setCollectionsError("Failed to load collections.");
      });

    return () => {
      active = false;
    };
  }, [collectionsRefreshKey]);

  const handleRetryLoad = () => {
    setLoadedId(null);
    setRefreshKey((value) => value + 1);
  };

  const handleRetryCollections = () => {
    setCollectionsLoaded(false);
    setCollectionsError(null);
    setCollectionsRefreshKey((value) => value + 1);
  };

  const handleSubmit = async (data) => {
    setSubmitting(true);
    try {
      await updatePrompt(id, data);
      navigate(`/prompts/${id}`);
    } finally {
      // If updatePrompt rejects, the error propagates to PromptForm,
      // which maps it to field/form errors (422/400/404/other). The
      // submitting flag is always reset here regardless of outcome.
      setSubmitting(false);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  // A 404 on the prompt takes precedence — the form cannot pre-fill.
  if (loadError === "not_found") {
    return (
      <div>
        <ErrorBanner message="Prompt not found." />
        <p>
          <Link to="/prompts">Back to Prompts</Link>
        </p>
      </div>
    );
  }

  if (loadError) {
    return (
      <ErrorBanner
        message="Failed to load prompt."
        onRetry={handleRetryLoad}
      />
    );
  }

  return (
    <div>
      {collectionsError && (
        <ErrorBanner
          message={collectionsError}
          onRetry={handleRetryCollections}
        />
      )}
      <PromptForm
        initialValues={prompt}
        collections={collections}
        onSubmit={handleSubmit}
        submitting={submitting}
      />
    </div>
  );
}

export default PromptEditPage;
