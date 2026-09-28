import styles from "./ErrorBanner.module.css";

/**
 * Error message with optional retry button.
 *
 * Displays a clearly visible error message for API and other
 * application errors. When `onRetry` is provided, a "Retry" button is
 * rendered alongside the message and invokes the handler on click. The
 * banner announces itself as an error to assistive technologies. The
 * component is purely presentational — it owns no state, performs no
 * API calls, and contains no application-specific error-handling logic.
 *
 * @param {Object} props - Component props.
 * @param {string} props.message - The error message to display.
 * @param {() => void} [props.onRetry] - Optional callback invoked when
 *   the user clicks the Retry button. When omitted, no Retry button is
 *   rendered.
 * @returns {JSX.Element} The error banner.
 */
function ErrorBanner({ message, onRetry }) {
  return (
    <div className={styles.banner} role="alert">
      <p className={styles.message}>{message}</p>
      {onRetry && (
        <button
          type="button"
          className={styles.retryButton}
          onClick={onRetry}
        >
          Retry
        </button>
      )}
    </div>
  );
}

export default ErrorBanner;
