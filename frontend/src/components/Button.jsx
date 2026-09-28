import styles from "./Button.module.css";

/**
 * Shared styled button with variants (primary, secondary, danger).
 *
 * Renders a native `<button>` element so that native behavior — focus,
 * keyboard activation (Enter/Space), form submission, and the disabled
 * state — is preserved. The visual style is controlled by `variant`;
 * content is supplied through `children`. The component is purely
 * presentational — it owns no state, makes no API calls, and contains
 * no routing or application-specific logic.
 *
 * @param {Object} props - Component props.
 * @param {"primary" | "secondary" | "danger"} [props.variant="primary"]
 *   Visual style of the button. Defaults to `"primary"` when omitted.
 * @param {() => void} props.onClick - Called when the user clicks the
 *   button. Not invoked while the button is disabled (native behavior).
 * @param {import("react").ReactNode} props.children - The button
 *   content, also serving as its accessible name.
 * @param {boolean} [props.disabled=false] - When true, the button is
 *   non-interactive, removed from the tab order, and announced as
 *   disabled to assistive technologies via the native attribute.
 * @returns {JSX.Element} The styled button.
 */
function Button({ variant = "primary", onClick, children, disabled = false }) {
  const variantClass = styles[variant] || styles.primary;

  return (
    <button
      className={`${styles.button} ${variantClass}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
}

export default Button;
