import styles from "./loading-state.module.css";

type LoadingStateProps = {
  label?: string;
  variant?: "page" | "results";
};

// Shared status UI; consumers own the main landmark and request state.
export default function LoadingState({
  label = "Loading page…",
  variant = "page",
}: LoadingStateProps) {
  return (
    <div className={`${styles.loading} ${styles[variant]}`} role="status">
      <span className={styles.ring} aria-hidden="true" />
      <span className={styles.label}>{label}</span>
    </div>
  );
}
