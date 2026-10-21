import styles from "./recommend.module.css";

// Recommend hero: the exact agreed heading plus a decorative paper plane.
export default function RecommendHero() {
  return (
    <div className={styles.hero}>
      <h1 className={styles.heading}>Ready to study abroad?</h1>
      <svg
        viewBox="0 0 116 115"
        fill="none"
        stroke="currentColor"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
        className={styles.plane}
      >
        {/* Outlined paper plane, lucide-style send geometry at 116/115 scale. */}
        <path d="M106 9.7 72.5 106.3 52 62.8 9.7 43.5 106 9.7Z" />
        <path className={styles.planeDetail} d="M106 9.7 52 62.8" />
      </svg>
    </div>
  );
}
