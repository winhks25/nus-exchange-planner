import Link from "next/link";
import styles from "./app-shell.module.css";

// The header row carries only the site name, on every route.
export default function AppHeader() {
  return (
    <header className={styles.header}>
      <Link href="/" className={styles.brand}>
        NUS Exchange Planner
      </Link>
    </header>
  );
}
