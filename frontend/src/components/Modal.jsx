import { useEffect, useRef } from "react";
import styles from "./Modal.module.css";

/**
 * Reusable modal container for dialogs and overlays.
 *
 * Renders nothing when `open` is false. When open, displays a centered
 * dialog over a backdrop overlay. Clicking the backdrop or pressing the
 * Escape key calls `onClose`. The optional `title` is shown in a
 * header; `children` provide the modal body content (e.g. a message
 * and action buttons, or a form). The component is purely a container —
 * it owns no data and makes no API calls.
 *
 * @param {Object} props - Component props.
 * @param {boolean} props.open - Whether the modal is visible.
 * @param {string} [props.title] - Optional title displayed in the
 *   modal header.
 * @param {() => void} props.onClose - Called when the user requests the
 *   modal to close (backdrop click or Escape key).
 * @param {import("react").ReactNode} props.children - The modal body
 *   content.
 * @returns {JSX.Element | null} The modal, or null when closed.
 */
function Modal({ open, title, onClose, children }) {
  const dialogRef = useRef(null);

  useEffect(() => {
    if (!open) {
      return;
    }

    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [open, onClose]);

  if (!open) {
    return null;
  }

  const handleBackdropClick = (event) => {
    if (event.target === event.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className={styles.backdrop}
      onClick={handleBackdropClick}
    >
      <div
        ref={dialogRef}
        className={styles.modal}
        role="dialog"
        aria-modal="true"
        aria-label={title || undefined}
      >
        {title && (
          <header className={styles.header}>
            <h2 className={styles.title}>{title}</h2>
            <button
              type="button"
              className={styles.closeButton}
              onClick={onClose}
              aria-label="Close"
            >
              ×
            </button>
          </header>
        )}

        <div className={styles.body}>{children}</div>
      </div>
    </div>
  );
}

export default Modal;
