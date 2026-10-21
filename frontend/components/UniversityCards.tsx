import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { buttonVariants, Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import type { Recommendation } from "@/lib/types";

export default function UniversityCards(
  { degree, recommendations }: { degree: string; recommendations: Recommendation[] }
) {
  return (
    <section aria-label="Ranked partner universities" className="cards">
      {recommendations.map((item, index) => (
        <Card
          role="article"
          className={`university-card ${index === 0 ? "top-card" : index < 3 ? "half-card" : "third-card"}`}
          key={item.university}
        >
          <CardHeader className="university-card-header">
            <span className="rank">#{index + 1}</span>
            <div className="university-card-heading">
              <CardTitle className="university-card-title text-6xl">
                <h2>{item.university}</h2>
              </CardTitle>
              <Badge variant="secondary" className="country-badge">{item.country}</Badge>
            </div>
          </CardHeader>

          <CardContent className="university-card-content">
            <p className="module-count nus-module-count">
              <strong>{item.distinct_nus_module_count}</strong>
              <span>NUS Modules</span>
            </p>
            <p className="module-count partner-module-count">
              <strong>{item.partner_module_count}</strong>
              <span>{item.university} Modules</span>
            </p>
          </CardContent>

          <CardFooter className="university-card-footer">
            <Link 
            href={`/compare?degree=${encodeURIComponent(degree)}&uni=${encodeURIComponent(item.university)}`}
            >
              <Button variant="link"
                className={buttonVariants({ variant: "default" })}
              >
                View Mappings →
              </Button>
            </Link>
          </CardFooter>
        </Card>
      ))}
    </section>
  );
}
