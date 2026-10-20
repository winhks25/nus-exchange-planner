import Link from "next/link";
import type { Recommendation } from "@/lib/types";

export default function UniversityCards(
  { degree, recommendations }: { degree: string; recommendations: Recommendation[] }
) {
  return (
    <section aria-label="Ranked partner universities" className="cards">
      {recommendations.map((item, index) => (
        <article
          className={`card ${index === 0 ? "top-card" : index < 3 ? "half-card" : "third-card"}`}
          key={item.university}
        >
          <div className="rank">#{index + 1}</div>
          <div>
            <h2>{item.university}</h2>
            <p>{item.country}</p>
          </div>

          {/* number of mappable modules */}
          <div className="card-count flex flex-col">
            {/* NUS */}
            <div>
              <strong>{item.distinct_nus_module_count}</strong>
              <span> NUS Modules</span>
            </div>
            
            {/* Partner Uniersity */}
            <div>
              <strong>{item.partner_module_count}</strong>
              <span> {item.university} Modules</span>
            </div>
          </div>
        
          <Link href={`/compare?degree=${encodeURIComponent(degree)}&uni=${encodeURIComponent(item.university)}`}>
            View Mappings →
          </Link>
        </article>
      ))}
    </section>
  );
}
