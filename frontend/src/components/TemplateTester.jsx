import { useState } from "react";
import { testPrompt } from "../api/prompts.js";
import styles from "./TemplateTester.module.css";

const VARIABLE_PATTERN = /\{\{(\w+)\}\}/g;

/**
 * Extract unique template variable names from prompt content.
 *
 * Uses the same pattern as the backend's `extract_variables` utility:
 * variable names are one or more word characters (letters, digits,
 * underscore) wrapped in double curly braces. Names are deduplicated
 * while preserving order of first appearance, since one input field
 * per unique variable is sufficient for rendering.
 *
 * @param {string} content - The prompt content to scan.
 * @returns {string[]} Unique variable names in order of first appearance.
 */
function extractVariables(content) {
  const seen = new Set();
  const variables = [];
  for (const match of content.matchAll(VARIABLE_PATTERN)) {
    const name = match[1];
    if (!seen.has(name)) {
      seen.add(name);
      variables.push(name);
    }
  }
  return variables;
}

/**
 * Template testing section for the Prompt Detail page.
 *
 * Extracts `{{variables}}` from the prompt's content, provides an
 * input field for each unique variable, and calls the `/test` endpoint
 * via the API layer when the user clicks "Render". Shows the rendered
 * output on success, an inline error on failure, and a "Rendering…"
 * message while the request is in flight.
 *
 * @param {Object} props - Component props.
 * @param {Object} props.prompt - The prompt to test.
 * @param {string} props.prompt.id - The prompt's unique identifier.
 * @param {string} props.prompt.content - The prompt content containing
 *   optional `{{variable}}` placeholders.
 * @returns {JSX.Element} The template tester section.
 */
function TemplateTester({ prompt }) {
  const variables = extractVariables(prompt.content);

  const [values, setValues] = useState({});
  const [rendering, setRendering] = useState(false);
  const [renderedContent, setRenderedContent] = useState(null);
  const [error, setError] = useState(null);

  // No variables: show content as-is with a note (spec §5.3)
  if (variables.length === 0) {
    return (
      <section className={styles.tester}>
        <h3 className={styles.title}>Template Tester</h3>
        <p className={styles.note}>
          This prompt has no template variables — no input needed.
        </p>
        <pre className={styles.output}>
          <code>{prompt.content}</code>
        </pre>
      </section>
    );
  }

  const handleInputChange = (name, value) => {
    setValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleRender = async () => {
    setRendering(true);
    setError(null);
    setRenderedContent(null);

    try {
      const response = await testPrompt(prompt.id, values);
      setRenderedContent(response.rendered_content);
    } catch (err) {
      setError(err.message);
    } finally {
      setRendering(false);
    }
  };

  return (
    <section className={styles.tester}>
      <h3 className={styles.title}>Template Tester</h3>

      <div className={styles.inputs}>
        {variables.map((name) => (
          <div key={name} className={styles.field}>
            <label className={styles.label} htmlFor={`var-${name}`}>
              {name}
            </label>
            <input
              id={`var-${name}`}
              className={styles.input}
              type="text"
              value={values[name] ?? ""}
              onChange={(e) => handleInputChange(name, e.target.value)}
              disabled={rendering}
            />
          </div>
        ))}
      </div>

      <button
        type="button"
        className={styles.renderButton}
        onClick={handleRender}
        disabled={rendering}
      >
        {rendering ? "Rendering…" : "Render"}
      </button>

      {error && (
        <p className={styles.error} role="alert">
          {error}
        </p>
      )}

      {(rendering || renderedContent !== null) && !error && (
        <div className={styles.outputSection}>
          <h4 className={styles.outputLabel}>Rendered Output</h4>
          <pre className={styles.output}>
            <code>{rendering ? "Rendering…" : renderedContent}</code>
          </pre>
        </div>
      )}
    </section>
  );
}

export default TemplateTester;
