import LoadingSpinner from "./LoadingSpinner.jsx";
import EmptyState from "./EmptyState.jsx";
import styles from "./CollectionList.module.css";

const EMPTY_MESSAGE =
  "No collections yet. Create one to organize your prompts.";

/**
 * Renders the list of collections with name, description, and delete
 * action.
 *
 * The component is purely presentational — it owns no state and makes
 * no API calls. It shows a `LoadingSpinner` while data is being
 * fetched, an `EmptyState` when the list is empty, and a row for each
 * collection otherwise. Each row displays the collection's name and
 * description and a delete button that delegates to the parent via
 * `onDelete`.
 *
 * @param {Object} props - Component props.
 * @param {Array<{id: string, name: string, description: string | null}>}
 *   props.collections - The collections to render.
 * @param {boolean} props.loading - Whether the collection list is
 *   currently being fetched; when true a LoadingSpinner replaces the
 *   list.
 * @param {(id: string) => void} props.onDelete - Called with the
 *   collection id when the user clicks the delete button on a row.
 * @returns {JSX.Element} The collection list.
 */
function CollectionList({ collections, loading, onDelete }) {
  if (loading) {
    return <LoadingSpinner />;
  }

  if (collections.length === 0) {
    return <EmptyState message={EMPTY_MESSAGE} />;
  }

  return (
    <ul className={styles.list}>
      {collections.map((collection) => {
        const handleDelete = () => {
          onDelete(collection.id);
        };

        return (
          <li key={collection.id} className={styles.item}>
            <article className={styles.card}>
              <div className={styles.header}>
                <h3 className={styles.name}>{collection.name}</h3>
                <button
                  type="button"
                  className={styles.deleteButton}
                  onClick={handleDelete}
                >
                  Delete
                </button>
              </div>

              {collection.description && (
                <p className={styles.description}>{collection.description}</p>
              )}
            </article>
          </li>
        );
      })}
    </ul>
  );
}

export default CollectionList;
