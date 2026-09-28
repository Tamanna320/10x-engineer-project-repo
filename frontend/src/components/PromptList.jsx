import PromptCard from "./PromptCard.jsx";
import LoadingSpinner from "./LoadingSpinner.jsx";
import EmptyState from "./EmptyState.jsx";
import styles from "./PromptList.module.css";

/**
 * Renders the list of PromptCard components for the current page.
 *
 * Shows a LoadingSpinner while data is being fetched, an EmptyState
 * when the list is empty, and a PromptCard for each prompt otherwise.
 * The component is purely presentational — it owns no state and makes
 * no API calls. All data and callbacks arrive via props.
 *
 * @param {Object} props - Component props.
 * @param {Array<{id: string}>} props.prompts - The prompts to render.
 * @param {boolean} props.loading - Whether the prompt list is currently
 *   being fetched; when true a LoadingSpinner replaces the list.
 * @param {(id: string) => void} props.onDelete - Called when the user
 *   clicks delete on a prompt card; forwarded to each PromptCard.
 * @returns {JSX.Element} The prompt list.
 */
function PromptList({ prompts, loading, onDelete }) {
  if (loading) {
    return <LoadingSpinner />;
  }

  if (prompts.length === 0) {
    return <EmptyState message="No prompts found." />;
  }

  return (
    <ul className={styles.list}>
      {prompts.map((prompt) => (
        <li key={prompt.id} className={styles.item}>
          <PromptCard prompt={prompt} onDelete={onDelete} />
        </li>
      ))}
    </ul>
  );
}

export default PromptList;
