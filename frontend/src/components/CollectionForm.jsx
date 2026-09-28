import { useState } from "react";
import styles from "./CollectionForm.module.css";

/**
 * Parse a FastAPI 422 validation error's `detail` array into a map of
 * field-level error messages. Each entry has a `loc` array (e.g.
 * `["body", "name"]`) and a `msg` string. Only fields relevant to the
 * collection form are mapped.
 *
 * @param {Array<{loc: string[], msg: string, type: string}>} detail
 *   The validation error detail array from the API response.
 * @returns {Object<string, string>} Map of field name → error message.
 */
function parseValidationErrors(detail) {
  const fieldErrors = {};
  const fieldMap = {
    name: "name",
    description: "description",
  };

  for (const item of detail) {
    const fieldName = item.loc?.[item.loc.length - 1];
    const mapped = fieldMap[fieldName];
    if (mapped) {
      fieldErrors[mapped] = item.msg;
    }
  }

  return fieldErrors;
}

/**
 * Inline form to create a new collection (name + description).
 *
 * The form manages its own field values via `useState`, starting empty
 * since this is a create-only form. On submit, it validates the name
 * field client-side, then calls `onSubmit(data)` with the form values.
 * If `onSubmit` returns a rejected promise, a 422 validation error is
 * shown as a field-level message on the name field (spec §5.2); other
 * errors are shown as a field-level message on the name field as a
 * fallback, since the spec only defines the name field for error
 * display.
 *
 * @param {Object} props - Component props.
 * @param {(data: {name: string, description: string | null}) => void | Promise<void>}
 *   props.onSubmit - Called with the form data on submit. May return
 *   a promise so the form can catch API errors.
 * @param {boolean} props.submitting - Whether a submit is in flight;
 *   disables the submit button when true.
 * @returns {JSX.Element} The collection creation form.
 */
function CollectionForm({ onSubmit, submitting }) {
  const [values, setValues] = useState({ name: "", description: "" });
  const [fieldErrors, setFieldErrors] = useState({});

  const handleFieldChange = (name, value) => {
    setValues((prev) => ({ ...prev, [name]: value }));
    setFieldErrors((prev) => ({ ...prev, [name]: undefined }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!values.name.trim()) {
      setFieldErrors({ name: "Name is required." });
      return;
    }
    if (values.name.length > 100) {
      setFieldErrors({ name: "Name must be 100 characters or fewer." });
      return;
    }
    if (values.description && values.description.length > 500) {
      setFieldErrors({ description: "Description must be 500 characters or fewer." });
      return;
    }

    setFieldErrors({});

    const data = {
      name: values.name,
      description: values.description || null,
    };

    try {
      await onSubmit(data);
      setValues({ name: "", description: "" });
    } catch (err) {
      if (err.status === 422 && Array.isArray(err.detail)) {
        setFieldErrors(parseValidationErrors(err.detail));
      } else {
        setFieldErrors({ name: err.message });
      }
    }
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit} noValidate>
      <div className={styles.field}>
        <label className={styles.label} htmlFor="collection-name">
          Name
        </label>
        <input
          id="collection-name"
          className={styles.input}
          type="text"
          value={values.name}
          onChange={(e) => handleFieldChange("name", e.target.value)}
          disabled={submitting}
          required
        />
        {fieldErrors.name && (
          <p className={styles.fieldError} role="alert">
            {fieldErrors.name}
          </p>
        )}
      </div>

      <div className={styles.field}>
        <label className={styles.label} htmlFor="collection-description">
          Description
        </label>
        <textarea
          id="collection-description"
          className={styles.textarea}
          value={values.description}
          onChange={(e) => handleFieldChange("description", e.target.value)}
          disabled={submitting}
          rows={3}
        />
        {fieldErrors.description && (
          <p className={styles.fieldError} role="alert">
            {fieldErrors.description}
          </p>
        )}
      </div>

      <button
        type="submit"
        className={styles.submitButton}
        disabled={submitting}
      >
        {submitting ? "Creating…" : "Create Collection"}
      </button>
    </form>
  );
}

export default CollectionForm;
