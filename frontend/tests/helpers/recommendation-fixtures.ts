import { expect, type Page, type Route } from "@playwright/test";
import type { Catalog, Degree, Recommendation } from "../../lib/types";
import {
  apiRecommendations,
  fixtureCatalog,
  fixtureDegree,
  recommendationsFor,
} from "../fixtures/recommendations";

export type RecommendationFixtureOptions = {
  catalog?: Catalog;
  degree?: Degree;
  recommendations?: Recommendation[];
};

export type InstalledRecommendationFixtures = {
  catalog: Catalog;
  degree: Degree;
  recommendations: Recommendation[];
};

async function fulfillJson(route: Route, json: unknown): Promise<void> {
  await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(json) });
}

export async function mockCatalog(page: Page, catalog: Catalog = fixtureCatalog): Promise<void> {
  await page.route("**/api/v1/catalog", route => fulfillJson(route, catalog));
}

export async function mockRecommendations(
  page: Page,
  degree: string,
  recommendations: Recommendation[],
): Promise<void> {
  await page.route("**/api/v1/recommendations?**", route =>
    fulfillJson(route, recommendationsFor(degree, recommendations)),
  );
}

export async function installRecommendationFixtures(
  page: Page,
  options: RecommendationFixtureOptions = {},
): Promise<InstalledRecommendationFixtures> {
  const catalog = options.catalog ?? fixtureCatalog;
  const degree = options.degree ?? fixtureDegree;
  const recommendations = options.recommendations ?? apiRecommendations;

  await mockCatalog(page, catalog);
  await mockRecommendations(page, degree.name, recommendations);

  return { catalog, degree, recommendations };
}

export async function selectDegree(
  page: Page,
  degreeName: string,
  expectedResultCount: number,
): Promise<void> {
  const picker = page.getByRole("combobox", { name: /degree programme/i });
  await expect(picker).toBeVisible();
  await picker.click();
  await picker.fill(degreeName);
  await picker.press("Enter");

  const cards = page.getByRole("article");
  await expect(cards).toHaveCount(expectedResultCount);
  if (expectedResultCount === 0) {
    await expect(page.getByText("Finding partner universities…")).toHaveCount(0);
    await expect(page.getByRole("region", { name: "Ranked partner universities" })).toHaveCount(1);
  }
}

export async function openRecommendWithFixtures(
  page: Page,
  options: RecommendationFixtureOptions = {},
): Promise<InstalledRecommendationFixtures> {
  const fixtures = await installRecommendationFixtures(page, options);

  await page.goto("/");
  await selectDegree(page, fixtures.degree.name, fixtures.recommendations.length);

  return fixtures;
}
