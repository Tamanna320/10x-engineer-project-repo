import Header from "./Header.jsx";
import Sidebar from "./Sidebar.jsx";
import styles from "./Layout.module.css";

/**
 * Page shell that renders the Header, Sidebar, and active page content.
 *
 * The component is purely structural: it composes the Header and Sidebar
 * and renders the active page inside its `children` prop. It owns no
 * state and makes no API calls.
 *
 * @param {Object} props - Component props.
 * @param {React.ReactNode} props.children - The active page content to
 *   render in the main content area.
 * @returns {JSX.Element} The layout shell.
 */
function Layout({ children }) {
  return (
    <div className={styles.layout}>
      <Header />
      <div className={styles.body}>
        <Sidebar />
        <main className={styles.content}>{children}</main>
      </div>
    </div>
  );
}

export default Layout;
