import { Map, MapPin, Plane } from "lucide-react";
import styles from "./recommend.module.css";

export default function RecommendHero() {
  return (
    <div className={styles.hero} data-testid="recommend-hero">
      <div className={styles.composition}>
        <h1 className={styles.heading}>
          <span className={styles.intro}>Ready to</span>{" "}
          <span className={styles.title}>Study <span className={styles.underline}>Abroad?</span></span>
        </h1>

        <div className={styles.flight} aria-hidden="true" data-testid="hero-flight">
          <span className={styles.flightLoop} />
          <span className={styles.flightTail} />
          <Plane className={styles.plane} aria-hidden="true" />
        </div>

        <div className={styles.destination} aria-hidden="true" data-testid="hero-destination">
          <Map className={styles.map} aria-hidden="true" />
          <MapPin className={styles.pin} aria-hidden="true" />
          <span className={styles.rays} />
        </div>
      </div>
    </div>
  );
}
