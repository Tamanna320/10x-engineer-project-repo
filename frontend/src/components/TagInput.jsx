import { useState } from "react";
import styles from "./TagInput.module.css";

/**
 * Comma-separated tag entry that produces a `string[]`.
 *
 * Renders a text input where the user types tags separated by commas.
 * When a comma is entered, the text before it is added as a tag. The
 * Enter key also adds the current input as a tag. Blurring the input
 * (e.g. by clicking the form's Save button) also commits any pending
 * text, so a tag typed but not delimited is not lost. Each tag has a
 * remove button. Tags are preserved exactly as entered — no
 * lowercasing or deduplication is applied. Only delimiter whitespace
 * around commas is stripped, as part of standard comma-separated
 * parsing.
 *
 * @param {Object} props - Component props.
 * @param {string[]} props.tags - The current tags array, controlled
 *   by the parent.
 * @param {(tags: string[]) => void} props.onChange - Called with the
 *   updated tags array whenever a tag is added or removed.
 * @returns {JSX.Element} The tag input component.
 */
function TagInput({ tags, onChange }) {
  const [input, setInput] = useState("");

  const handleInputChange = (event) => {
    const value = event.target.value;

    if (value.includes(",")) {
      // Split on commas; all segments before the last become tags
      const segments = value.split(",");
      const lastSegment = segments.pop();
      const newTags = segments
        .map((s) => s.trim())
        .filter((s) => s.length > 0);

      if (newTags.length > 0) {
        onChange([...tags, ...newTags]);
      }

      setInput(lastSegment);
    } else {
      setInput(value);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      const trimmed = input.trim();
      if (trimmed) {
        onChange([...tags, trimmed]);
        setInput("");
      }
    } else if (event.key === "Backspace" && input === "" && tags.length > 0) {
      onChange(tags.slice(0, -1));
    }
  };

  // Commit any pending text as a tag when the input loses focus (e.g.
  // the user clicks the form's Save button), so a tag typed but not
  // delimited with Enter or a comma is not lost on submit.
  const handleBlur = () => {
    const trimmed = input.trim();
    if (trimmed) {
      onChange([...tags, trimmed]);
      setInput("");
    }
  };

  const handleRemoveTag = (index) => {
    onChange(tags.filter((_, i) => i !== index));
  };

  return (
    <div className={styles.container}>
      {tags.length > 0 && (
        <ul className={styles.tagList}>
          {tags.map((tag, index) => (
            <li key={index} className={styles.tag}>
              <span className={styles.tagText}>{tag}</span>
              <button
                type="button"
                className={styles.removeButton}
                onClick={() => handleRemoveTag(index)}
                aria-label={`Remove tag ${tag}`}
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}

      <input
        className={styles.input}
        type="text"
        value={input}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        onBlur={handleBlur}
        placeholder="Add tags (comma-separated)..."
        aria-label="Add tag"
      />
    </div>
  );
}

export default TagInput;

