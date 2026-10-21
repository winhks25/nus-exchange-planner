import { RecommendationRows } from "@/components/UniversityCards";
import { fixtureDegree, VISUAL_DISPLAY_RANK, visualRecommendations } from "./recommendations";

// The harness repeats the drawing's rank; production keeps real ordinals.
const previewCards = visualRecommendations.map(recommendation => ({
  key: recommendation.id,
  recommendation,
  rank: VISUAL_DISPLAY_RANK,
}));

export default function UniversityCardPreview() {
  return (
    <main className="preview-shell" data-testid="card-preview">
      <RecommendationRows degree={fixtureDegree.name} cards={previewCards} />
    </main>
  );
}
