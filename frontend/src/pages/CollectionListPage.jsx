import { useEffect, useState } from "react";
import CollectionList from "../components/CollectionList.jsx";
import CollectionForm from "../components/CollectionForm.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import ConfirmDialog from "../components/ConfirmDialog.jsx";
import { getCollections, createCollection, deleteCollection } from "../api/collections.js";

/**
 * Collection List page.
 *
 * Fetches all collections on mount via `getCollections`, renders the
 * shared `CollectionList` and `CollectionForm`, and manages create and
 * delete actions. Creating a collection calls `createCollection` and
 * refreshes the list; deleting a collection opens the shared
 * `ConfirmDialog` and, on confirmation, calls `deleteCollection` and
 * refreshes the list. See `specs/frontend.md` §2.5, §5.1, §5.2, and
 * §5.3.
 *
 * Loading is derived from a `loadedKey`/`collectionsLoaded` flag so
 * that no `setState` is called synchronously inside an effect body
 * (per the `react-hooks/set-state-in-effect` lint rule), while still
 * showing a spinner on initial mount and on every retry/refresh.
 *
 * @returns {JSX.Element} The Collection List page.
 */
function CollectionListPage() {
  
  const [collections, setCollections] = useState([]);
  const [collectionsLoaded, setCollectionsLoaded] = useState(false);
  const [loadError, setLoadError] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const [submitting, setSubmitting] = useState(false);
  const [deleteTargetId, setDeleteTargetId] = useState(null);
  const [deleteError, setDeleteError] = useState(null);

  // Loading is true until the first fetch for the current refresh key
  // resolves. Derived (not set) to satisfy the lint rule.
  const loading = !collectionsLoaded;

  // Fetch collections on mount and whenever a refresh is requested.
  useEffect(() => {
    let active = true;

    getCollections()
      .then((data) => {
        if (!active) return;
        setCollections(data.collections ?? []);
        setCollectionsLoaded(true);
        setLoadError(null);
      })
      .catch(() => {
        if (!active) return;
        setCollections([]);
        setCollectionsLoaded(true);
        setLoadError("Failed to load collections.");
      });

    return () => {
      active = false;
    };
  }, [refreshKey]);

  const handleRetry = () => {
    setCollectionsLoaded(false);
    setLoadError(null);
    setRefreshKey((value) => value + 1);
  };

  const handleCreateSubmit = async (data) => {
    setSubmitting(true);
    try {
      await createCollection(data);
      // Refresh the list to show the newly created collection.
      setCollectionsLoaded(false);
      setRefreshKey((value) => value + 1);
    } finally {
      // If createCollection rejects, the error propagates to
      // CollectionForm, which maps 422 responses to field-level
      // validation messages on the name field (spec §5.2). The
      // submitting flag is always reset here regardless of outcome.
      setSubmitting(false);
    }
  };

  const handleDeleteRequest = (id) => {
    setDeleteError(null);
    setDeleteTargetId(id);
  };

  const handleDeleteCancel = () => {
    setDeleteTargetId(null);
  };

  const handleDeleteConfirm = async () => {
    const id = deleteTargetId;
    setDeleteTargetId(null);
    try {
      await deleteCollection(id);
      setDeleteError(null);
      // Refresh the list to reflect the deletion.
      setCollectionsLoaded(false);
      setRefreshKey((value) => value + 1);
    } catch (err) {
      setDeleteError(
        err.status === 404
          ? "Item not found — it may have been deleted already."
          : "Failed to delete collection.",
      );
      // Refresh so the list reflects the actual server state.
      setCollectionsLoaded(false);
      setRefreshKey((value) => value + 1);
    }
  };

  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "flex-start",
          marginBottom: "1rem",
        }}
      >
      </div>

      {deleteError && <ErrorBanner message={deleteError} />}

      {loadError ? (
        <ErrorBanner
          message="Failed to load collections."
          onRetry={handleRetry}
        />
      ) : (
        <>
          <CollectionForm
            onSubmit={handleCreateSubmit}
            submitting={submitting}
          />
          <CollectionList
            collections={collections}
            loading={loading}
            onDelete={handleDeleteRequest}
          />
        </>
      )}

      <ConfirmDialog
        open={deleteTargetId !== null}
        title="Delete Collection"
        message="Are you sure you want to delete this collection? Prompts in this collection will be unassigned, not deleted. This action cannot be undone."
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
      />
    </div>
  );
}

export default CollectionListPage;

