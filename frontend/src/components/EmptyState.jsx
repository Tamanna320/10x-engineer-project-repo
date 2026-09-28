import styles from "./EmptyState.module.css";

/**
 * Friendly message and icon when a list is empty.
 *
 * Displays a centered, decorative icon and the provided empty-state
 * message. When both `actionLabel` and `onAction` are provided, a
 * button labeled with `actionLabel` is rendered that invokes `onAction`
 * on click. The component is purely presentational — it owns no state,
 * makes no API calls, and contains no filtering or application-specific
 * logic. The parent screen decides which message and action (if any)
 * to provide.
 *
 * @param {Object} props - Component props.
 * @param {string} props.message - The empty-state message to display.
 * @param {string} [props.actionLabel] - Optional label for the action
 *   button. The button is only rendered when both `actionLabel` and
 *   `onAction` are provided.
 * @param {() => void} [props.onAction] - Optional callback invoked when
 *   the user clicks the action button.
 * @returns {JSX.Element} The empty state.
 */
function EmptyState({ message, actionLabel, onAction }) {
  const hasAction = Boolean(actionLabel) && Boolean(onAction);

  return (
    <div className={styles.container} role="status">
      <svg
        className={styles.icon}
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <path d="M22 12h-6l-2 3h-4l-2-3H2" />
        <path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z" />
      </svg>
      <p className={styles.message}>{message}</p>
      {hasAction && (
        <button
          type="button"
          className={styles.actionButton}
          onClick={onAction}
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}

export default EmptyState;
