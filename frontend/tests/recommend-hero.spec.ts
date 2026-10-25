import { expect, test } from "@playwright/test";
import type { Page } from "@playwright/test";
import type { MappingResult } from "../lib/types";
import { catalogWith, university } from "./fixtures/recommendations";
import { mockCatalog } from "./helpers/recommendation-fixtures";

// Exact hero copy from the UI contract.
const HERO_TEXT = "Ready to Study Abroad?";

// Old hero copy that must disappear from Recommend (main scope keeps the
// header's brand link out of the comparison).
const REMOVED_COPY = [
  "NUS Exchange Planner",
  "Find where your modules can take you.",
  "Choose a degree to rank partner universities by available module mappings.",
];

async function computedStyle(page: Page, locator: string, property: string): Promise<string> {
  return page.locator(locator).first().evaluate((el, prop) => getComputedStyle(el).getPropertyValue(prop), property);
}

const compareMappings: MappingResult = {
  degree: "Computer Science",
  university: "University of Toronto",
  distinct_nus_module_count: 1,
  partner_module_count: 1,
  mappings: [
    {
      nus_course: { code: "CS2106", title: "Introduction to Operating Systems", units: 4 },
      partner_course: { code: "ECE344H1", title: "Operating Systems" },
    },
  ],
};

test("the approved hero uses Comic Sans and decorative travel illustrations", async ({ page }) => {
  await page.goto("/");
  const heading = page.getByRole("heading", { level: 1 });
  await expect(heading).toHaveCount(1);
  await expect(heading).toHaveText(HERO_TEXT);
  expect(await computedStyle(page, "h1", "font-family")).toBe(
    '"Comic Sans MS", "Comic Sans", cursive',
  );
  expect(await computedStyle(page, "h1", "font-weight")).toBe("500");
  const hero = page.getByTestId("recommend-hero");
  expect(await hero.evaluate(el => getComputedStyle(el).backgroundColor)).toBe("rgba(0, 0, 0, 0)");
  expect(await hero.evaluate(el => getComputedStyle(el).borderWidth)).toBe("0px");
  for (const id of ["hero-flight", "hero-destination"]) {
    const illustration = page.getByTestId(id);
    await expect(illustration).toBeVisible();
    await expect(illustration).toHaveAttribute("aria-hidden", "true");
    expect(await illustration.evaluate(el => getComputedStyle(el).pointerEvents)).toBe("none");
    await expect(illustration.locator("a, button, [tabindex]")).toHaveCount(0);
  }
  for (const copy of REMOVED_COPY) {
    await expect(page.locator("main").getByText(copy, { exact: true })).toHaveCount(0);
  }
});

for (const width of [320, 390, 768, 1024, 1888]) {
  test(`hero composition stays inside its column at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 1000 });
    await page.goto("/");
    const hero = await page.getByTestId("recommend-hero").boundingBox();
    const intro = page.getByRole("heading", { level: 1 }).locator(":scope > span").first();
    const title = page.getByRole("heading", { level: 1 }).locator(":scope > span").last();
    for (const element of [intro, title, page.getByTestId("hero-flight"), page.getByTestId("hero-destination")]) {
      const box = await element.boundingBox();
      expect(box!.x).toBeGreaterThanOrEqual(hero!.x);
      expect(box!.x + box!.width).toBeLessThanOrEqual(hero!.x + hero!.width);
      expect(box!.y + box!.height).toBeLessThanOrEqual(hero!.y + hero!.height);
    }
    const introBox = await intro.boundingBox();
    const titleBox = await title.boundingBox();
    expect(introBox!.y + introBox!.height).toBeLessThanOrEqual(titleBox!.y);
    const map = await page.getByTestId("hero-destination").boundingBox();
    const flight = await page.getByTestId("hero-flight").boundingBox();
    expect(map!.y + map!.height / 2).toBeLessThan(flight!.y + flight!.height / 2);
    expect(await page.getByTestId("recommend-hero").evaluate(el => el.scrollWidth - el.clientWidth)).toBeLessThanOrEqual(0);
  });
}

test("Mappings keeps its own hero copy when the Recommend hero ships", async ({ page }) => {
  await mockCatalog(
    page,
    catalogWith([university("University of Toronto", "Canada")]),
  );
  await page.route("**/api/v1/mappings?**", route =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(compareMappings),
    }),
  );

  await page.goto(
    `/mappings?degree=${encodeURIComponent("Computer Science")}&uni=${encodeURIComponent("University of Toronto")}`,
  );

  // Mappings content and copy are untouched: no selector leakage from the hero.
  const heading = page.getByRole("heading", { level: 1 });
  await expect(heading).toHaveCount(1);
  await expect(heading).toHaveText("Module mappings.");
  await expect(page.getByText("SIDE BY SIDE")).toHaveCount(0);
  await expect(
    page.getByText(
      "Explore qualifying NUS and partner course mappings for your degree and your preferred university.",
    ),
  ).toHaveCount(1);
  await expect(page.getByRole("combobox", { name: "Degree programme" })).toBeVisible();
  await expect(page.getByRole("combobox", { name: "Partner university" })).toBeVisible();
  await expect(page.locator(".mapping-row")).toHaveCount(1);
});
