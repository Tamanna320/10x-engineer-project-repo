import styles from "./SearchFilterBar.module.css";

const ALL_COLLECTIONS_VALUE = "";

/**
 * Search and filter bar for the Prompt List page.
 *
 * Renders three controlled inputs — a search text field, a collection
 * dropdown, and a single-tag text field — and calls `onChange` with the
 * updated filter values whenever any of them changes. The component
 * owns no state; all filter values are controlled by the parent via
 * props, matching specs/frontend.md §2.2 and §4.
 *
 * @param {Object} props - Component props.
 * @param {string} props.search - The current search query.
 * @param {string | null} props.collectionId - The selected collection
 *   id, or `null` when no collection filter is applied.
 * @param {string} props.tag - The current single-tag filter value.
 * @param {Array<{id: string, name: string}>} props.collections - The
 *   collections available for filtering, used to populate the dropdown.
 * @param {(filters: {search: string, collectionId: string | null, tag: string}) => void}
 *   props.onChange - Called with the updated filter values whenever a
 *   control changes.
 * @returns {JSX.Element} The search and filter bar.
 */
function SearchFilterBar({ search, collectionId, tag, collections, onChange }) {
  const emitChange = (updates) => {
    onChange({ search, collectionId, tag, ...updates });
  };

  const handleSearchChange = (event) => {
    emitChange({ search: event.target.value });
  };

  const handleCollectionChange = (event) => {
    const value = event.target.value;
    emitChange({ collectionId: value === ALL_COLLECTIONS_VALUE ? null : value });
  };

  const handleTagChange = (event) => {
    emitChange({ tag: event.target.value });
  };

  return (
    <div className={styles.bar}>
      <div className={styles.field}>
        <label className={styles.label} htmlFor="filter-search">
          Search
        </label>
        <input
          id="filter-search"
          className={styles.input}
          type="search"
          value={search}
          onChange={handleSearchChange}
          placeholder="Search prompts..."
        />
      </div>

      <div className={styles.field}>
        <label className={styles.label} htmlFor="filter-collection">
          Collection
        </label>
        <select
          id="filter-collection"
          className={styles.select}
          value={collectionId ?? ALL_COLLECTIONS_VALUE}
          onChange={handleCollectionChange}
        >
          <option value={ALL_COLLECTIONS_VALUE}>All Collections</option>
          {collections.map((collection) => (
            <option key={collection.id} value={collection.id}>
              {collection.name}
            </option>
          ))}
        </select>
      </div>

      <div className={styles.field}>
        <label className={styles.label} htmlFor="filter-tag">
          Tag
        </label>
        <input
          id="filter-tag"
          className={styles.input}
          type="text"
          value={tag}
          onChange={handleTagChange}
          placeholder="Filter by tag..."
        />
      </div>
    </div>
  );
}

export default SearchFilterBar;
