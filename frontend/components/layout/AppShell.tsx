import type { ReactNode } from "react";
import AppHeader from "./AppHeader";
import styles from "./app-shell.module.css";

type AppShellProps = {
  // Temporary navigation slot until US3 moves it into the shared sidebar.
  navigation?: ReactNode;
  children: ReactNode;
};

export default function AppShell({ navigation, children }: AppShellProps) {
  return (
    <div className={styles.frame}>
      <AppHeader />
      {navigation ? (
        <nav aria-label="Primary" className={styles.tempNav}>
          {navigation}
        </nav>
      ) : null}
      <div className={styles.content}>{children}</div>
    </div>
  );
}
