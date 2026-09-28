import { Link } from "react-router-dom";
import styles from "./Sidebar.module.css";

/**
 * Navigation links to the Prompt List and Collection List.
 *
 * Uses React Router's `Link` for client-side navigation (no full page
 * reload), as required by specs/frontend.md §4 (Navigation layer). The
 * component owns no state and makes no API calls.
 *
 * @returns {JSX.Element} The sidebar navigation.
 */
function Sidebar() {
  return (
    <nav className={styles.sidebar}>
      <Link className={styles.link} to="/">
        Prompts
      </Link>
      <Link className={styles.link} to="/collections">
        Collections
      </Link>
    </nav>
  );
}

export default Sidebar;
