import { Link } from "react-router-dom";
import styles from "./PromptCard.module.css";

/**
 * A single prompt summary card with title, tags, description, and action
 * buttons (View, Edit, Delete).
 *
 * The card is purely presentational — it owns no state and makes no API
 * calls. The delete action delegates to the parent via `onDelete`. View
 * and Edit use React Router `Link` for client-side navigation, matching
 * specs/frontend.md §1 routes and §4 navigation layer.
 *
 * @param {Object} props - Component props.
 * @param {Object} props.prompt - The prompt to display.
 * @param {string} props.prompt.id - The prompt's unique identifier.
 * @param {string} props.prompt.title - The prompt's title.
 * @param {string} [props.prompt.description] - Optional short summary.
 * @param {string[]} props.prompt.tags - Tags for categorization.
 * @param {(id: string) => void} props.onDelete - Called with the prompt
 *   id when the user clicks the Delete button.
 * @returns {JSX.Element} The prompt card.
 */
function PromptCard({ prompt, onDelete }) {
  const handleDelete = () => {
    onDelete(prompt.id);
  };

  return (
    <article className={styles.card}>
      <div className={styles.header}>
        <h3 className={styles.title}>
          <Link to={`/prompts/${prompt.id}`} className={styles.titleLink}>
            {prompt.title}
          </Link>
        </h3>
      </div>

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

      <div className={styles.actions}>
        <Link to={`/prompts/${prompt.id}`} className={styles.actionLink}>
          View
        </Link>
        <Link to={`/prompts/${prompt.id}/edit`} className={styles.actionLink}>
          Edit
        </Link>
        <button
          type="button"
          className={styles.deleteButton}
          onClick={handleDelete}
        >
          Delete
        </button>
      </div>
    </article>
  );
}

export default PromptCard;
