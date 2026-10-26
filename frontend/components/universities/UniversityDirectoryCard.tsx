import { useState } from "react";
import type { University } from "@/lib/types";
import styles from "./universities.module.css";

type Props = {
  university: University;
};

const FALLBACK_IMAGE = "/images/university-fallback.svg";

// Official links only: anything that is not an http(s) URL is treated as
// missing rather than rendered, so a corrupted catalog value cannot become a
// protocol-relative or javascript: link.
function safeWebsite(url: string | null): string | null {
  if (typeof url !== "string") return null;
  return url.startsWith("https://") || url.startsWith("http://") ? url : null;
}

// Directory card (US4): photograph (or local fallback), name, location tags,
// attribution, official website, and the mappings action. US5 adds
// state-preserving navigation to the mappings link.
export default function UniversityDirectoryCard({ university }: Props) {
  // One-way swap: a failed photograph renders the local fallback and never
  // retries, so a broken URL cannot loop between the two sources.
  const [photoFailed, setPhotoFailed] = useState(false);
  const photoSrc = photoFailed ? null : university.image;
  const website = safeWebsite(university.website);
  const href = `/mappings?uni=${encodeURIComponent(university.name)}`;

  return (
    <article className={styles.card}>
      <div className={styles.media}>
        {photoSrc !== null ? (
          <img
            className={styles.mediaImage}
            src={photoSrc}
            alt={`Campus photograph of ${university.name}`}
            loading="lazy"
            onError={() => setPhotoFailed(true)}
          />
        ) : (
          <img
            className={styles.mediaImage}
            src={FALLBACK_IMAGE}
            alt=""
            aria-hidden="true"
            loading="lazy"
          />
        )}
      </div>
      {/* Attribution belongs to the photograph, not the fallback artwork. */}
      <div className={styles.body}>
        {photoSrc !== null && university.image_attribution !== null && (
          <p className={styles.credit}>{university.image_attribution}</p>
        )}
        <h2 className={styles.name}>{university.name}</h2>
        <div className={styles.location}>
          {/* A missing city is unknown and stays unrendered, never guessed. */}
          {university.city !== null && <span className={styles.tag}>{university.city}</span>}
          <span className={styles.tag}>{university.country}</span>
        </div>
        <footer className={styles.footer}>
          {website ? (
            <a className={styles.website} href={website} target="_blank" rel="noopener noreferrer">
              {new URL(website).hostname}
            </a>
          ) : (
            <span className={styles.unavailable}>Website unavailable</span>
          )}
          <a className={styles.action} href={href}>
            {"View Mappings -->"}
          </a>
        </footer>
      </div>
    </article>
  );
}
