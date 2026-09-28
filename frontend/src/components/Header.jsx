import { useEffect, useState } from "react";
import styles from "./Header.module.css";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Top bar with the PromptLab title and API health status indicator.
 *
 * Checks GET /health when the component mounts. Shows a green indicator
 * when the API health check succeeds and a red indicator when it fails.
 * When the API is unreachable, the indicator has the tooltip "API unreachable".
 *
 * @returns {JSX.Element} The header bar.
 */
function Header() {
  const [isHealthy, setIsHealthy] = useState(false);

  useEffect(() => {
    let active = true;

    async function checkHealth() {
      try {
        const response = await fetch(`${BASE_URL}/health`);
        if (!active) return;
        setIsHealthy(response.ok);
      } catch {
        if (!active) return;
        setIsHealthy(false);
      }
    }

    checkHealth();

    return () => {
      active = false;
    };
  }, []);

  const indicatorClassName = isHealthy ? styles.healthy : styles.unhealthy;

  return (
    <header className={styles.header}>
      <h1 className={styles.title}>PromptLab</h1>
      <span
        className={`${styles.indicator} ${indicatorClassName}`}
        title={isHealthy ? "API healthy" : "API unreachable"}
        aria-label={isHealthy ? "API healthy" : "API unreachable"}
        role="status"
      />
    </header>
  );
}

export default Header;
