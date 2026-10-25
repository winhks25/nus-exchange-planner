import type { University } from "@/lib/types";
import styles from "./universities.module.css";

type Props = {
  university: University;
};

// Directory card (US3 initial): name, location tags, and the mappings link.
// US4 adds media and website presentation; US5 adds state-preserving navigation.
export default function UniversityDirectoryCard({ university }: Props) {
  const href = `/mappings?uni=${encodeURIComponent(university.name)}`;

  return (
    <article className={styles.card}>
      <h2 className={styles.name}>{university.name}</h2>
      <div className={styles.location}>
        {/* A missing city is unknown and stays unrendered, never guessed. */}
        {university.city !== null && <span className={styles.tag}>{university.city}</span>}
        <span className={styles.tag}>{university.country}</span>
      </div>
      <a className={styles.action} href={href}>
        {"View Mappings -->"}
      </a>
    </article>
  );
}
