import type { ReactNode } from "react";
import AppHeader from "./AppHeader";
import AppSidebar from "./AppSidebar";
import styles from "./app-shell.module.css";

type AppShellProps = {
  children: ReactNode;
};

export default function AppShell({ children }: AppShellProps) {
  return (
    <div className={styles.frame}>
      <AppHeader />
      <div className={styles.body}>
        <AppSidebar />
        <div className={styles.content}>{children}</div>
      </div>
    </div>
  );
}
