import Modal from "./Modal.jsx";
import styles from "./ConfirmDialog.module.css";

/**
 * Reusable confirmation modal for destructive actions.
 *
 * Wraps the `Modal` component and displays a confirmation message with
 * Confirm and Cancel buttons. Confirm calls `onConfirm`; Cancel and all
 * other close paths (backdrop click, Escape key, close button) call
 * `onCancel`. The component is purely presentational — it owns no state
 * and makes no API calls.
 *
 * @param {Object} props - Component props.
 * @param {boolean} props.open - Whether the dialog is visible.
 * @param {string} props.title - The dialog title, shown in the modal
 *   header.
 * @param {string} props.message - The confirmation message displayed in
 *   the dialog body.
 * @param {() => void} props.onConfirm - Called when the user clicks the
 *   Confirm button.
 * @param {() => void} props.onCancel - Called when the user clicks the
 *   Cancel button or closes the modal via backdrop/Escape/close button.
 * @returns {JSX.Element | null} The confirmation dialog, or null when
 *   closed.
 */
function ConfirmDialog({ open, title, message, onConfirm, onCancel }) {
  return (
    <Modal open={open} title={title} onClose={onCancel}>
      <p className={styles.message}>{message}</p>
      <div className={styles.actions}>
        <button
          type="button"
          className={styles.cancelButton}
          onClick={onCancel}
        >
          Cancel
        </button>
        <button
          type="button"
          className={styles.confirmButton}
          onClick={onConfirm}
          autoFocus
        >
          Confirm
        </button>
      </div>
    </Modal>
  );
}

export default ConfirmDialog;
