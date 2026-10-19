import Link from "next/link";
import type { Recommendation } from "@/lib/types";
export default function UniversityCards({ degree, recommendations }: { degree: string; recommendations: Recommendation[] }) {
  return <section aria-label="Ranked partner universities" className="cards">{recommendations.map((item, index) => <article className={`card ${index === 0 ? "top-card" : ""}`} key={item.university}>
    <div className="rank">#{index + 1}</div><div><h2>{item.university}</h2><p>{item.country}</p></div><div className="card-count"><strong>{item.module_count}</strong><span>mappable modules</span></div>
    <Link href={`/compare?degree=${encodeURIComponent(degree)}&uni=${encodeURIComponent(item.university)}`}>View Mappings →</Link>
  </article>)}</section>;
}
