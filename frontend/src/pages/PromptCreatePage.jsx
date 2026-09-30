import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import PromptForm from "../components/PromptForm.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import { createPrompt } from "../api/prompts.js";
import { getCollections } from "../api/collections.js";

/**
 * Create Prompt page.
 *
 * Fetches the collection list on mount (to populate the form's
 * collection dropdown), then renders the shared `PromptForm` in create
 * mode. On submit, the form's values are sent to the backend via
 * `createPrompt`; on success the user is navigated to the Prompt List.
 *
 * The page owns the `submitting` flag so the form can disable its submit
 * button and show "Saving…" while the request is in flight. API errors
 * are surfaced by `PromptForm` itself: it maps 422 responses to
 * field-level messages, 400 (bad collection) to an inline collection
 * error, and other failures to its embedded `ErrorBanner` (see
 * `specs/frontend.md` §5.2).
 *
 * @returns {JSX.Element} The Create Prompt page.
 */
function PromptCreatePage() {
  const navigate = useNavigate();

  const [collections, setCollections] = useState([]);
  const [loadingCollections, setLoadingCollections] = useState(true);
  const [collectionsError, setCollectionsError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  // Fetch collections once on mount to populate the dropdown.
  useEffect(() => {
    let active = true;

    getCollections()
      .then((data) => {
        if (!active) return;
        setCollections(data.collections ?? []);
        setLoadingCollections(false);
      })
      .catch(() => {
        if (!active) return;
        setCollections([]);
        setLoadingCollections(false);
        setCollectionsError("Failed to load collections.");
      });

    return () => {
      active = false;
    };
  }, []);

  const handleRetryCollections = () => {
    setLoadingCollections(true);
    setCollectionsError(null);
    getCollections()
      .then((data) => {
        setCollections(data.collections ?? []);
        setLoadingCollections(false);
      })
      .catch(() => {
        setCollections([]);
        setLoadingCollections(false);
        setCollectionsError("Failed to load collections.");
      });
  };

  const handleSubmit = async (data) => {
    setSubmitting(true);
    try {
      await createPrompt(data);
      navigate("/prompts");
    } finally {
      // If createPrompt rejects, the error propagates to PromptForm,
      // which maps it to field/form errors (422/400/404/other). The
      // submitting flag is always reset here regardless of outcome.
      setSubmitting(false);
    }
  };

  return (
    <div>
      {loadingCollections ? (
        <LoadingSpinner />
      ) : (
        <>
          {collectionsError && (
            <ErrorBanner
              message={collectionsError}
              onRetry={handleRetryCollections}
            />
          )}
          <PromptForm
            collections={collections}
            onSubmit={handleSubmit}
            submitting={submitting}
          />
        </>
      )}
    </div>
  );
}

export default PromptCreatePage;

