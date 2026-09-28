import { useState } from "react";
import { restoreVersion } from "../api/prompts.js";
import ErrorBanner from "./ErrorBanner.jsx";
import EmptyState from "./EmptyState.jsx";
import ConfirmDialog from "./ConfirmDialog.jsx";
import styles from "./VersionHistory.module.css";

const EMPTY_MESSAGE =
  "No version history yet. Versions are saved automatically when you edit this prompt.";

/**
 * Lists saved versions with their fields and a "Restore" button per row.
 *
 * Receives the version list via props (fetched by the parent page) and
 * delegates the restore API call to the spec-defined API layer
 * (`restoreVersion`). When the user clicks "Restore", a confirmation
 * dialog is shown; on confirm, the API call is made and `onRestore` is
 * called on success so the parent can refetch the prompt and versions.
 * Restore errors are shown as an `ErrorBanner` inside the version
 * section, and the empty state shows an `EmptyState` message.
 *
 * @param {Object} props - Component props.
 * @param {string} props.promptId - The id of the prompt whose versions
 *   are listed.
 * @param {Array<{version: number, title: string, content: string,
 *   description: string | null, collection_id: string | null,
 *   tags: string[], saved_at: string}>} props.versions - The saved
 *   version snapshots to display.
 * @param {(versionNumber: number) => void} props.onRestore - Called
 *   after a version is successfully restored, so the parent can refetch.
 * @returns {JSX.Element} The version history section.
 */
function VersionHistory({ promptId, versions, onRestore }) {
  const [confirmVersion, setConfirmVersion] = useState(null);
  const [restoringVersion, setRestoringVersion] = useState(null);
  const [error, setError] = useState(null);

  // Empty state (spec §5.3)
  if (versions.length === 0) {
    return (
      <section className={styles.history}>
        <h3 className={styles.title}>Version History</h3>
        <EmptyState message={EMPTY_MESSAGE} />
      </section>
    );
  }

  const handleRestoreClick = (versionNumber) => {
    setConfirmVersion(versionNumber);
    setError(null);
  };

  const handleConfirm = async () => {
    const versionNumber = confirmVersion;
    setConfirmVersion(null);
    setRestoringVersion(versionNumber);
    setError(null);

    try {
      await restoreVersion(promptId, versionNumber);
      onRestore(versionNumber);
    } catch (err) {
      // Map errors to spec §5.2 messages; fall back to the API message
      if (err.status === 400) {
        setError("Collection not found — cannot restore this version.");
      } else if (err.status === 404) {
        setError("Version not found.");
      } else {
        setError(err.message);
      }
    } finally {
      setRestoringVersion(null);
    }
  };

  const handleCancel = () => {
    setConfirmVersion(null);
  };

  return (
    <section className={styles.history}>
      <h3 className={styles.title}>Version History</h3>

      {error && <ErrorBanner message={error} />}

      <ul className={styles.list}>
        {versions.map((version) => (
          <li key={version.version} className={styles.versionRow}>
            <div className={styles.versionHeader}>
              <span className={styles.versionNumber}>
                Version {version.version}
              </span>
              <time
                dateTime={version.saved_at}
                className={styles.savedAt}
              >
                {new Date(version.saved_at).toLocaleString()}
              </time>
            </div>

            <h4 className={styles.versionTitle}>{version.title}</h4>

            {version.description && (
              <p className={styles.versionDescription}>
                {version.description}
              </p>
            )}

            {version.tags.length > 0 && (
              <ul className={styles.tags}>
                {version.tags.map((tag) => (
                  <li key={tag} className={styles.tag}>
                    {tag}
                  </li>
                ))}
              </ul>
            )}

            <pre className={styles.content}>
              <code>{version.content}</code>
            </pre>

            <button
              type="button"
              className={styles.restoreButton}
              onClick={() => handleRestoreClick(version.version)}
              disabled={restoringVersion !== null}
            >
              {restoringVersion === version.version
                ? "Restoring…"
                : "Restore"}
            </button>
          </li>
        ))}
      </ul>

      {confirmVersion !== null && (
        <ConfirmDialog
          open={true}
          title="Restore Version"
          message={`Restore this prompt to version ${confirmVersion}? The current state will be saved as a new version before restoring.`}
          onConfirm={handleConfirm}
          onCancel={handleCancel}
        />
      )}
    </section>
  );
}

export default VersionHistory;
