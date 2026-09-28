import { useState } from "react";
import TagInput from "./TagInput.jsx";
import ErrorBanner from "./ErrorBanner.jsx";
import styles from "./PromptForm.module.css";

const NO_COLLECTION_VALUE = "";

/**
 * Build the initial form values from the optional `initialValues` prop.
 *
 * When editing, `initialValues` contains the prompt's current fields.
 * When creating, it is undefined and all fields start empty/default.
 *
 * @param {Object | undefined} initialValues - Partial prompt data.
 * @returns {{title: string, content: string, description: string,
 *   collectionId: string | null, tags: string[]}} Form field values.
 */
function buildInitialValues(initialValues) {
  return {
    title: initialValues?.title ?? "",
    content: initialValues?.content ?? "",
    description: initialValues?.description ?? "",
    collectionId: initialValues?.collection_id ?? null,
    tags: initialValues?.tags ?? [],
  };
}

/**
 * Validate form fields client-side and return a map of field-level
 * errors. Validation mirrors the backend's `PromptBase` constraints.
 *
 * @param {{title: string, content: string, description: string}} values
 *   The current form values.
 * @returns {Object<string, string>} Map of field name → error message.
 */
function validate(values) {
  const errors = {};

  if (!values.title.trim()) {
    errors.title = "Title is required.";
  } else if (values.title.length > 200) {
    errors.title = "Title must be 200 characters or fewer.";
  }

  if (!values.content.trim()) {
    errors.content = "Content is required.";
  }

  if (values.description && values.description.length > 500) {
    errors.description = "Description must be 500 characters or fewer.";
  }

  return errors;
}

/**
 * Parse a FastAPI 422 validation error's `detail` array into a map of
 * field-level error messages. Each entry in the detail array has a
 * `loc` array (e.g. `["body", "title"]`) and a `msg` string.
 *
 * @param {Array<{loc: string[], msg: string, type: string}>} detail
 *   The validation error detail array from the API response.
 * @returns {Object<string, string>} Map of field name → error message.
 */
function parseValidationErrors(detail) {
  const fieldErrors = {};
  const fieldMap = {
    title: "title",
    content: "content",
    description: "description",
    collection_id: "collectionId",
    tags: "tags",
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
 * Controlled form for title, content, description, collection, and
 * tags.
 *
 * The form manages its own field values via `useState`, initialized
 * from `initialValues` (for edit mode) or empty defaults (for create
 * mode). On submit, it validates fields client-side, then calls
 * `onSubmit(data)` with the form values. If `onSubmit` returns a
 * rejected promise, the error is handled according to spec §5.2:
 * 422 validation errors → field-level messages, 400 bad collection →
 * inline collection error, 404 → ErrorBanner.
 *
 * @param {Object} props - Component props.
 * @param {Object} [props.initialValues] - Pre-fill values for edit
 *   mode; undefined for create mode.
 * @param {Array<{id: string, name: string}>} props.collections -
 *   Available collections for the collection dropdown.
 * @param {(data: {title: string, content: string,
 *   description: string | null, collection_id: string | null,
 *   tags: string[]}) => void | Promise<void>} props.onSubmit - Called
 *   with the form data on submit. May return a promise so the form can
 *   catch API errors.
 * @param {boolean} props.submitting - Whether a submit is in flight;
 *   disables the submit button when true.
 * @returns {JSX.Element} The prompt form.
 */
function PromptForm({ initialValues, collections, onSubmit, submitting }) {
  const [values, setValues] = useState(() => buildInitialValues(initialValues));
  const [fieldErrors, setFieldErrors] = useState({});
  const [formError, setFormError] = useState(null);

  const handleFieldChange = (name, value) => {
    setValues((prev) => ({ ...prev, [name]: value }));
    setFieldErrors((prev) => ({ ...prev, [name]: undefined }));
  };

  const handleTagsChange = (tags) => {
    setValues((prev) => ({ ...prev, tags }));
    setFieldErrors((prev) => ({ ...prev, tags: undefined }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setFormError(null);

    const clientErrors = validate(values);
    if (Object.keys(clientErrors).length > 0) {
      setFieldErrors(clientErrors);
      return;
    }

    setFieldErrors({});

    const data = {
      title: values.title,
      content: values.content,
      description: values.description || null,
      collection_id: values.collectionId,
      tags: values.tags,
    };

    try {
      await onSubmit(data);
    } catch (err) {
      if (err.status === 422 && Array.isArray(err.detail)) {
        setFieldErrors(parseValidationErrors(err.detail));
      } else if (err.status === 400) {
        setFieldErrors((prev) => ({
          ...prev,
          collectionId: "Collection not found.",
        }));
      } else if (err.status === 404) {
        setFormError("Prompt not found.");
      } else {
        setFormError(err.message);
      }
    }
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit} noValidate>
      {formError && <ErrorBanner message={formError} />}

      <div className={styles.field}>
        <label className={styles.label} htmlFor="prompt-title">
          Title
        </label>
        <input
          id="prompt-title"
          className={styles.input}
          type="text"
          value={values.title}
          onChange={(e) => handleFieldChange("title", e.target.value)}
          disabled={submitting}
          required
        />
        {fieldErrors.title && (
          <p className={styles.fieldError} role="alert">
            {fieldErrors.title}
          </p>
        )}
      </div>

      <div className={styles.field}>
        <label className={styles.label} htmlFor="prompt-content">
          Content
        </label>
        <textarea
          id="prompt-content"
          className={styles.textarea}
          value={values.content}
          onChange={(e) => handleFieldChange("content", e.target.value)}
          disabled={submitting}
          rows={8}
          required
        />
        {fieldErrors.content && (
          <p className={styles.fieldError} role="alert">
            {fieldErrors.content}
          </p>
        )}
      </div>

      <div className={styles.field}>
        <label className={styles.label} htmlFor="prompt-description">
          Description
        </label>
        <textarea
          id="prompt-description"
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

      <div className={styles.field}>
        <label className={styles.label} htmlFor="prompt-collection">
          Collection
        </label>
        <select
          id="prompt-collection"
          className={styles.select}
          value={values.collectionId ?? NO_COLLECTION_VALUE}
          onChange={(e) =>
            handleFieldChange(
              "collectionId",
              e.target.value === NO_COLLECTION_VALUE ? null : e.target.value,
            )
          }
          disabled={submitting}
        >
          <option value={NO_COLLECTION_VALUE}>No Collection</option>
          {collections.map((collection) => (
            <option key={collection.id} value={collection.id}>
              {collection.name}
            </option>
          ))}
        </select>
        {fieldErrors.collectionId && (
          <p className={styles.fieldError} role="alert">
            {fieldErrors.collectionId}
          </p>
        )}
      </div>

      <div className={styles.field}>
        <span className={styles.label}>Tags</span>
        <TagInput
          tags={values.tags}
          onChange={handleTagsChange}
        />
        {fieldErrors.tags && (
          <p className={styles.fieldError} role="alert">
            {fieldErrors.tags}
          </p>
        )}
      </div>

      <button
        type="submit"
        className={styles.submitButton}
        disabled={submitting}
      >
        {submitting ? "Saving…" : "Save"}
      </button>
    </form>
  );
}

export default PromptForm;
