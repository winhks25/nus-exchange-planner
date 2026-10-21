import type { Catalog, Degree, Recommendation, Recommendations, University } from "../../lib/types";

export const fixtureDegree: Degree = {
  name: "Computer Science",
  degree: "Bachelor of Computing (Computer Science)",
};

export const alternateFixtureDegree: Degree = {
  name: "Business Analytics",
  degree: "Bachelor of Business Analytics",
};

export const fixtureDegrees: Degree[] = [fixtureDegree, alternateFixtureDegree];

const apiUniversities: University[] = [
  { name: "University of Aurora Bay", country: "Canada" },
  { name: "Northwind Institute of Technology", country: "Canada" },
  { name: "Yonsei Metropolitan University", country: "South Korea" },
  { name: "Seoul Advanced Studies University", country: "South Korea" },
  { name: "University of Western Coast, The", country: "Australia" },
  { name: "Kyoto International University", country: "Japan" },
  { name: "Osaka Collaborative University", country: "Japan" },
  { name: "Melbourne Coastal University", country: "Australia" },
];

export const apiRecommendations: Recommendation[] = [
  {
    university: "University of Aurora Bay",
    country: "Canada",
    distinct_nus_module_count: 6,
    partner_module_count: 9,
    mapping_count: 9,
  },
  {
    university: "Northwind Institute of Technology",
    country: "Canada",
    distinct_nus_module_count: 3,
    partner_module_count: 4,
    mapping_count: 5,
  },
  {
    university: "Yonsei Metropolitan University",
    country: "South Korea",
    distinct_nus_module_count: 0,
    partner_module_count: 0,
    mapping_count: 0,
  },
  {
    university: "Seoul Advanced Studies University",
    country: "South Korea",
    distinct_nus_module_count: 17,
    partner_module_count: 11,
    mapping_count: 18,
  },
  {
    university: "University of Western Coast, The",
    country: "Australia",
    distinct_nus_module_count: 19,
    partner_module_count: 7,
    mapping_count: 22,
  },
  {
    university: "Kyoto International University",
    country: "Japan",
    distinct_nus_module_count: 2,
    partner_module_count: 1,
    mapping_count: 1,
  },
  {
    university: "Osaka Collaborative University",
    country: "Japan",
    distinct_nus_module_count: 1,
    partner_module_count: 1,
    mapping_count: 1,
  },
  {
    university: "Melbourne Coastal University",
    country: "Australia",
    distinct_nus_module_count: 5,
    partner_module_count: 3,
    mapping_count: 4,
  },
];

export const longNameRecommendations: Recommendation[] = [
  {
    university:
      "The University of Extremely Long Synthetic Name for International Exchange Studies",
    country: "United Kingdom of Great Britain and Northern Ireland",
    distinct_nus_module_count: 4,
    partner_module_count: 2,
    mapping_count: 3,
  },
  {
    university: "Institute for Advanced Interdisciplinary Coastal and Marine Research",
    country: "Federative Republic of a Very Long Synthetic Country Name",
    distinct_nus_module_count: 7,
    partner_module_count: 12,
    mapping_count: 14,
  },
];

export const recommendationResultVariants = {
  zero: [],
  one: apiRecommendations.slice(0, 1),
  two: apiRecommendations.slice(0, 2),
  five: apiRecommendations.slice(0, 5),
  six: apiRecommendations.slice(0, 6),
  seven: apiRecommendations.slice(0, 7),
} satisfies Record<string, Recommendation[]>;

export const fixtureCatalog: Catalog = {
  degrees: fixtureDegrees,
  universities: apiUniversities,
};

export function catalogWith(universities: University[] = apiUniversities): Catalog {
  return { degrees: fixtureDegrees, universities };
}

export function recommendationsFor(
  degree: string,
  recommendations: Recommendation[],
): Recommendations {
  return { degree, recommendations };
}

export type VisualCardFixture = Recommendation & { id: string };

export const VISUAL_DISPLAY_RANK = 1;

export const visualRecommendations: VisualCardFixture[] = Array.from(
  { length: 6 },
  (_, index) => ({
    id: `visual-fixture-${index + 1}`,
    university: "University Name",
    country: "Country",
    distinct_nus_module_count: 10,
    partner_module_count: 12,
    mapping_count: 12,
  }),
);
