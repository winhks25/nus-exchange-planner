import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import type { Recommendation } from "@/lib/types";
import { cn } from "@/lib/utils";
import styles from "./recommend.module.css";

export type UniversityCardTier = "featured" | "secondary" | "compact";

type Props = {
  recommendation: Recommendation;
  degree: string;
  rank: number;
  tier: UniversityCardTier;
};

// Tier classes only change size and type, never content.
const tierStyles: Record<UniversityCardTier, string> = {
  featured: styles.cardFeatured,
  secondary: styles.cardSecondary,
  compact: styles.cardCompact,
};

// One card renders API values; ordering and grouping stay in the collection.
export default function UniversityCard({
  recommendation,
  degree,
  rank,
  tier,
}: Props) {
  const { university, country, distinct_nus_module_count, partner_module_count } =
    recommendation;
  const href = `/mappings?degree=${encodeURIComponent(degree)}&uni=${encodeURIComponent(university)}`;

  return (
    <Card role="article" data-tier={tier} className={cn(styles.card, tierStyles[tier])}>
      <CardHeader className={styles.cardHeader}>
        <span className={styles.cardRank}>#{rank}</span>
        <div className={styles.cardHeading}>
          <CardTitle className={styles.cardTitle}>
            <h2>{university}</h2>
          </CardTitle>
          <Badge variant="secondary" className={styles.cardCountry}>
            {country}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className={styles.cardContent}>
        {/* NUS is the primary metric; the partner count stays secondary. */}
        <p className={styles.cardNus}>
          <strong>{distinct_nus_module_count}</strong> NUS Modules
        </p>
        <p className={styles.cardPartner}>
          <strong>{partner_module_count}</strong> Partner University Modules
        </p>
      </CardContent>

      <CardFooter className={styles.cardFooter}>
        {/* One plain anchor keeps the deep link and focus stop intact. */}
        <a className={styles.cardAction} href={href}>
          {"View Mappings -->"}
        </a>
      </CardFooter>
    </Card>
  );
}
