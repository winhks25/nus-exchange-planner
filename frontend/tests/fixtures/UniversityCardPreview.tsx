import UniversityCard, { type UniversityCardTier } from "@/components/recommend/UniversityCard";
import styles from "@/components/recommend/recommend.module.css";
import { fixtureDegree, VISUAL_DISPLAY_RANK, visualRecommendations } from "./recommendations";

// The harness repeats the drawing's rank; production keeps real ordinals.
const previewTiers: UniversityCardTier[] = [
  "featured",
  "secondary",
  "secondary",
  "compact",
  "compact",
  "compact",
];

export default function UniversityCardPreview() {
  return (
    <main className="preview-shell" data-testid="card-preview">
      <section aria-label="Ranked partner universities" className={styles.cards}>
        {visualRecommendations.map((recommendation, index) => (
          <UniversityCard
            key={recommendation.id}
            recommendation={recommendation}
            degree={fixtureDegree.name}
            rank={VISUAL_DISPLAY_RANK}
            tier={previewTiers[index]}
          />
        ))}
      </section>
    </main>
  );
}
