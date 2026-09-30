import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import SearchFilterBar from "../components/SearchFilterBar.jsx";
import PromptList from "../components/PromptList.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import EmptyState from "../components/EmptyState.jsx";
import ConfirmDialog from "../components/ConfirmDialog.jsx";
import Button from "../components/Button.jsx";
import { getPrompts, deletePrompt } from "../api/prompts.js";
import { getCollections } from "../api/collections.js";
import styles from "./PromptListPage.module.css";

/**
 * Prompt List page.
 *
 * Fetches prompts and collections on mount, manages search/collection/tag
 * filter state, and supports deleting a prompt after confirmation. Uses
 * only existing components and the API helpers in `src/api`. See
 * `specs/frontend.md` §2.2, §5.1, §5.2, and §5.3.
 *
 * @returns {JSX.Element} The Prompt List page.
 */
function PromptListPage() {
  const navigate = useNavigate();

  const [prompts, setPrompts] = useState([]);
  const [total, setTotal] = useState(0);
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteError, setDeleteError] = useState(null);
  const [filters, setFilters] = useState({
    search: "",
    collectionId: null,
    tag: "",
  });
  const [deleteTargetId, setDeleteTargetId] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  // Fetch collections once on mount to populate the filter dropdown.
  useEffect(() => {
    let active = true;
    getCollections()
      .then((data) => {
        if (active) setCollections(data.collections ?? []);
      })
      .catch(() => {
        // Collections only drive the filter dropdown; a failure does not
        // block the prompt list. Keep the dropdown empty on error.
        if (active) setCollections([]);
      });
    return () => {
      active = false;
    };
  }, []);

  // Fetch prompts on mount and whenever the filters or refresh key change.
  // Loading and error state are toggled by the handlers that trigger a
  // refetch (initial mount, filter change, retry, delete); inside this
  // effect, state is only updated from the async result callbacks.
  useEffect(() => {
    let active = true;

    const params = {};
    if (filters.search.trim() !== "") {
      params.search = filters.search.trim();
    }
    if (filters.collectionId !== null) {
      params.collection_id = filters.collectionId;
    }
    if (filters.tag.trim() !== "") {
      params.tag = filters.tag.trim();
    }

    getPrompts(params)
      .then((data) => {
        if (!active) return;
        setPrompts(data.prompts ?? []);
        setTotal(data.total ?? 0);
        setLoading(false);
      })
      .catch(() => {
        if (!active) return;
        setPrompts([]);
        setTotal(0);
        setLoading(false);
        setError("Failed to load prompts.");
      });

    return () => {
      active = false;
    };
  }, [filters.search, filters.collectionId, filters.tag, refreshKey]);

  const hasFilters =
    filters.search.trim() !== "" ||
    filters.collectionId !== null ||
    filters.tag.trim() !== "";

  const handleFilterChange = (next) => {
    setFilters(next);
    setLoading(true);
    setError(null);
  };

  const handleClearFilters = () => {
    setFilters({ search: "", collectionId: null, tag: "" });
    setLoading(true);
    setError(null);
  };

  const handleRetry = () => {
    setRefreshKey((value) => value + 1);
    setLoading(true);
    setError(null);
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
    setLoading(true);
    try {
      await deletePrompt(id);
      setDeleteError(null);
      setRefreshKey((value) => value + 1);
    } catch (err) {
      setDeleteError(
        err.status === 404
          ? "Item not found — it may have been deleted already."
          : "Failed to delete prompt.",
      );
      // Refresh so the list reflects the actual server state.
      setRefreshKey((value) => value + 1);
    }
  };

  const handleCreatePrompt = () => {
    navigate("/prompts/new");
  };

  const handleViewCollections = () => {
    navigate("/collections");
  };
 
  return (
    <div className={styles.page}>
      <div className={styles.pageHeader}>
        <h1 className={styles.heading}>Prompts</h1>
        <div className={styles.headerActions}>
          <Button variant="secondary" onClick={handleViewCollections}>
            Collections
          </Button>
        <Button onClick={handleCreatePrompt}>New Prompt</Button>
      </div>
    </div>

      <SearchFilterBar
        search={filters.search}
        collectionId={filters.collectionId}
        tag={filters.tag}
        collections={collections}
        onChange={handleFilterChange}
      />

      {deleteError && <ErrorBanner message={deleteError} />}

      {error ? (
        <ErrorBanner message="Failed to load prompts." onRetry={handleRetry} />
      ) : loading ? (
        <LoadingSpinner />
      ) : total === 0 ? (
        hasFilters ? (
          <EmptyState
            message="No prompts match your filters."
            actionLabel="Clear Filters"
            onAction={handleClearFilters}
          />
        ) : (
          <EmptyState
            message="No prompts yet. Create your first prompt."
          />
        )
      ) : (
        <PromptList
          prompts={prompts}
          loading={false}
          onDelete={handleDeleteRequest}
        />
      )}

      <ConfirmDialog
        open={deleteTargetId !== null}
        title="Delete Prompt"
        message="Are you sure you want to delete this prompt? This action cannot be undone."
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
      />
    </div>
  );
}

export default PromptListPage;

