import Link from "next/link";
import type { Recommendation } from "@/lib/types";
export default function UniversityCards({ degree, recommendations }: { degree: string; recommendations: Recommendation[] }) {
  return <section aria-label="Ranked partner universities" className="cards">
    {recommendations.map((item, index) => <article className={`card ${index === 0 ? "top-card" : index < 3 ? "half-card" : "third-card"}`} key={item.university}>
      <div className="rank">#{index + 1}</div>
      <div><h2>{item.university}</h2><p>{item.country}</p></div>
      <div className="card-count"><strong>{item.partner_module_count}</strong><span>mappable partner modules</span></div>
      <dl className="card-secondary-counts">
        <div><dt>distinct NUS modules</dt><dd>{item.distinct_nus_module_count}</dd></div>
        <div><dt>mappings</dt><dd>{item.mapping_count}</dd></div>
      </dl>
      <Link href={`/compare?degree=${encodeURIComponent(degree)}&uni=${encodeURIComponent(item.university)}`}>View Mappings →</Link>
    </article>)}
  </section>;
}
