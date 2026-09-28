import { Link } from "react-router-dom";
import styles from "./PromptDetail.module.css";

/**
 * Displays the prompt's title, description, content, tags, collection,
 * and timestamps.
 *
 * This component is purely presentational — it owns no state and makes
 * no API calls. It renders the full prompt data passed via the `prompt`
 * prop. Version history and template testing are handled by their own
 * separate components (VersionHistory, TemplateTester) per spec §2.3,
 * not here.
 *
 * @param {Object} props - Component props.
 * @param {Object} props.prompt - The prompt to display.
 * @param {string} props.prompt.id - The prompt's unique identifier.
 * @param {string} props.prompt.title - The prompt's title.
 * @param {string} props.prompt.content - The full prompt text.
 * @param {string | null} [props.prompt.description] - Optional summary.
 * @param {string | null} [props.prompt.collection_id] - Optional
 *   collection id the prompt belongs to.
 * @param {string[]} props.prompt.tags - Tags for categorization.
 * @param {string} props.prompt.created_at - ISO timestamp of creation.
 * @param {string} props.prompt.updated_at - ISO timestamp of last update.
 * @returns {JSX.Element} The prompt detail view.
 */
function PromptDetail({ prompt }) {
  const created = new Date(prompt.created_at).toLocaleString();
  const updated = new Date(prompt.updated_at).toLocaleString();

  return (
    <article className={styles.detail}>
      <header className={styles.header}>
        <h2 className={styles.title}>{prompt.title}</h2>
        <div className={styles.actions}>
          <Link to={`/prompts/${prompt.id}/edit`} className={styles.actionLink}>
            Edit
          </Link>
          <Link to="/" className={styles.actionLink}>
            Back
          </Link>
        </div>
      </header>

      {prompt.description && (
        <p className={styles.description}>{prompt.description}</p>
      )}

      {prompt.tags.length > 0 && (
        <ul className={styles.tags}>
          {prompt.tags.map((tag) => (
            <li key={tag} className={styles.tag}>
              {tag}
            </li>
          ))}
        </ul>
      )}

      <div className={styles.meta}>
        <p className={styles.metaItem}>
          <span className={styles.metaLabel}>Collection:</span>{" "}
          {prompt.collection_id ? (
            <Link
              to={`/collections`}
              className={styles.collectionLink}
            >
              {prompt.collection_id}
            </Link>
          ) : (
            <span className={styles.metaValue}>None</span>
          )}
        </p>
        <p className={styles.metaItem}>
          <span className={styles.metaLabel}>Created:</span>{" "}
          <time dateTime={prompt.created_at} className={styles.metaValue}>
            {created}
          </time>
        </p>
        <p className={styles.metaItem}>
          <span className={styles.metaLabel}>Updated:</span>{" "}
          <time dateTime={prompt.updated_at} className={styles.metaValue}>
            {updated}
          </time>
        </p>
      </div>

      <div className={styles.contentSection}>
        <h3 className={styles.sectionTitle}>Content</h3>
        <pre className={styles.content}>
          <code>{prompt.content}</code>
        </pre>
      </div>
    </article>
  );
}

export default PromptDetail;
