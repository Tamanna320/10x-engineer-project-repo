import { useEffect, useRef } from "react";
import styles from "./Modal.module.css";

/**
 * Selector for all natively focusable element types that are not
 * disabled and not hidden. Used by the focus trap to cycle Tab/Shift+Tab
 * within the modal.
 */
const FOCUSABLE_SELECTOR = [
  "a[href]",
  "button:not([disabled])",
  "input:not([disabled])",
  "textarea:not([disabled])",
  "select:not([disabled])",
  '[tabindex]:not([tabindex="-1"])',
].join(",");

/**
 * Return the focusable elements inside `container` as an array, in DOM
 * order.
 *
 * @param {HTMLElement} container - The element to search within.
 * @returns {HTMLElement[]} Focusable elements, possibly empty.
 */
function getFocusableElements(container) {
  return Array.from(
    container.querySelectorAll(FOCUSABLE_SELECTOR),
  ).filter(
    (el) => !el.hasAttribute("hidden") && el.offsetParent !== null,
  );
}

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
 * While open, keyboard focus is trapped within the dialog (Tab and
 * Shift+Tab cycle only through focusable elements inside the modal) and,
 * on close, focus is restored to the element that had focus before the
 * modal opened (if that element still exists and is focusable).
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
  const previouslyFocusedRef = useRef(null);

  useEffect(() => {
    if (!open) {
      return;
    }

    // Remember the element that had focus before the modal opened so
    // focus can be restored when it closes.
    previouslyFocusedRef.current = document.activeElement;

    const dialog = dialogRef.current;

    // Move focus into the dialog on open. Prefer the first focusable
    // element; fall back to the dialog container itself so keyboard
    // users have a starting point inside the dialog.
    const focusable = dialog ? getFocusableElements(dialog) : [];
    if (focusable.length > 0) {
      focusable[0].focus();
    } else if (dialog) {
      dialog.focus();
    }

    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        onClose();
        return;
      }

      if (event.key !== "Tab") {
        return;
      }

      const currentDialog = dialogRef.current;
      if (!currentDialog) {
        return;
      }

      const elements = getFocusableElements(currentDialog);
      if (elements.length === 0) {
        // Keep focus from escaping when there are no focusable children.
        event.preventDefault();
        return;
      }

      const first = elements[0];
      const last = elements[elements.length - 1];

      if (event.shiftKey) {
        if (
          document.activeElement === first ||
          !currentDialog.contains(document.activeElement)
        ) {
          event.preventDefault();
          last.focus();
        }
      } else {
        if (
          document.activeElement === last ||
          !currentDialog.contains(document.activeElement)
        ) {
          event.preventDefault();
          first.focus();
        }
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);

      // Restore focus to the element that opened the modal, if it still
      // exists and can receive focus. Guard against elements that were
      // removed from the DOM while the modal was open.
      const previous = previouslyFocusedRef.current;
      if (previous && typeof previous.focus === "function") {
        try {
          if (
            document.contains(previous) &&
            previous.offsetParent !== null
          ) {
            previous.focus();
          }
        } catch {
          // The element may have been removed or become non-focusable;
          // silently skip restoring focus.
        }
      }
      previouslyFocusedRef.current = null;
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
        tabIndex={-1}
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
