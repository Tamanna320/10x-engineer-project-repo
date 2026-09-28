import styles from "./LoadingSpinner.module.css";

/**
 * Centered spinner shown while data is being fetched.
 *
 * Renders a spinning indicator centered in its container, with an
 * optional message below it. When a message is provided it serves as
 * the accessible label announced by screen readers. When omitted, a
 * visually-hidden "Loading…" label provides a baseline announcement.
 * The component is purely presentational and makes no API calls.
 *
 * @param {Object} props - Component props.
 * @param {string} [props.message] - Optional message displayed below
 *   the spinner.
 * @returns {JSX.Element} The loading spinner.
 */
function LoadingSpinner({ message }) {
  return (
    <div className={styles.container} role="status" aria-live="polite">
      <div
        className={styles.spinner}
        aria-hidden="true"
      />
      <span className={styles.message}>
        {message || "Loading…"}
      </span>
    </div>
  );
}

export default LoadingSpinner;
