import UniversityCard from "@/components/recommend/UniversityCard";
import styles from "@/components/recommend/recommend.module.css";
import type { Recommendation } from "@/lib/types";

export type RankedCard = {
  key: string;
  recommendation: Recommendation;
  rank: number;
};

type RecommendationRowsProps = {
  degree: string;
  cards: RankedCard[];
};

// Split ordered results into the reference 1-2-3 rows without dropping items.
function splitRows(cards: RankedCard[]) {
  const [featured, ...rest] = cards;
  const secondary = rest.slice(0, 2);
  const compact = rest.slice(2);
  const compactRows: RankedCard[][] = [];

  for (let index = 0; index < compact.length; index += 3) {
    compactRows.push(compact.slice(index, index + 3));
  }

  return { featured, secondary, compactRows };
}

export function RecommendationRows({ degree, cards }: RecommendationRowsProps) {
  const { featured, secondary, compactRows } = splitRows(cards);

  return (
    <section aria-label="Ranked partner universities" className={styles.cards}>
      {featured && (
        <div className={styles.featuredRow}>
          <UniversityCard
            recommendation={featured.recommendation}
            degree={degree}
            rank={featured.rank}
            tier="featured"
          />
        </div>
      )}

      {secondary.length > 0 && (
        <div className={styles.secondaryRow}>
          {secondary.map(card => (
            <UniversityCard
              key={card.key}
              recommendation={card.recommendation}
              degree={degree}
              rank={card.rank}
              tier="secondary"
            />
          ))}
        </div>
      )}

      {compactRows.map(row => (
        <div className={styles.compactRow} key={row[0].key}>
          {row.map(card => (
            <UniversityCard
              key={card.key}
              recommendation={card.recommendation}
              degree={degree}
              rank={card.rank}
              tier="compact"
            />
          ))}
        </div>
      ))}
    </section>
  );
}

export default function UniversityCards({
  degree,
  recommendations,
}: {
  degree: string;
  recommendations: Recommendation[];
}) {
  return (
    <RecommendationRows
      degree={degree}
      cards={recommendations.map((recommendation, index) => ({
        key: recommendation.university,
        recommendation,
        rank: index + 1,
      }))}
    />
  );
}
