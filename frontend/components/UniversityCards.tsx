import UniversityCard, { type UniversityCardTier } from "@/components/recommend/UniversityCard";
import styles from "@/components/recommend/recommend.module.css";
import type { Recommendation } from "@/lib/types";

// Temporary tier mapping keeps incoming order until US7 adds final rows.
function tierFor(index: number): UniversityCardTier {
  if (index === 0) return "featured";
  if (index < 3) return "secondary";
  return "compact";
}

export default function UniversityCards({
  degree,
  recommendations,
}: {
  degree: string;
  recommendations: Recommendation[];
}) {
  return (
    <section aria-label="Ranked partner universities" className={styles.cards}>
      {recommendations.map((item, index) => (
        <UniversityCard
          key={item.university}
          recommendation={item}
          degree={degree}
          rank={index + 1}
          tier={tierFor(index)}
        />
      ))}
    </section>
  );
}
