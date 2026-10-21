import { expect, test } from "@playwright/test";
import type { Page } from "@playwright/test";
import type { MappingResult } from "../lib/types";
import { catalogWith } from "./fixtures/recommendations";
import { mockCatalog } from "./helpers/recommendation-fixtures";

// Exact hero copy from the UI contract.
const HERO_TEXT = "Ready to study abroad?";

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

test("the Recommend hero shows only the agreed heading and a decorative plane", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("combobox", { name: "Degree programme" })).toBeVisible();

  // One h1 with the exact contracted text.
  const heading = page.getByRole("heading", { level: 1 });
  await expect(heading).toHaveCount(1);
  await expect(heading).toHaveText(HERO_TEXT);

  // Old eyebrow, headline and supporting copy are gone from Recommend only.
  for (const copy of REMOVED_COPY) {
    await expect(page.locator("main").getByText(copy, { exact: true })).toHaveCount(0);
  }

  // The plane stays decorative and can never take focus.
  const plane = page.locator("main svg").first();
  await expect(plane).toHaveCount(1);
  await expect(plane).toHaveAttribute("aria-hidden", "true");
  expect(await plane.evaluate(el => el.matches("a, button, [tabindex]"))).toBe(false);
  expect(await plane.evaluate(el => getComputedStyle(el).pointerEvents)).toBe("none");

  // Source hero role sizes on desktop (tier 2.5rem/500/1.2).
  expect(await computedStyle(page, "h1", "font-size")).toBe("40px");
  expect(await computedStyle(page, "h1", "font-weight")).toBe("500");
  expect(await computedStyle(page, "h1", "line-height")).toBe("48px");
});

test("the hero matches the reference anchors at 1888x1337", async ({ page }) => {
  await page.setViewportSize({ width: 1888, height: 1337 });
  await page.goto("/");
  await expect(page.getByRole("combobox", { name: "Degree programme" })).toBeVisible();

  const near = (actual: number, target: number, tolerance = 8) =>
    expect(Math.abs(actual - target)).toBeLessThanOrEqual(tolerance);

  // Heading anchor x417/y193 and a single line at the reference width.
  const headingBox = await page.getByRole("heading", { level: 1 }).boundingBox();
  near(headingBox!.x, 417);
  near(headingBox!.y, 193);
  near(headingBox!.height, 48);

  // Plane near x1422/y172 sized 116x115.
  const planeBox = await page.locator("main svg").first().boundingBox();
  near(planeBox!.x, 1422);
  near(planeBox!.y, 172);
  near(planeBox!.width, 116);
  near(planeBox!.height, 115);
});

test.describe("narrow viewport", () => {
  test.use({ viewport: { width: 390, height: 844 } });

  test("mobile keeps readable hero type and no horizontal overflow", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("combobox", { name: "Degree programme" })).toBeVisible();

    // 390px maps the hero to the 2rem source scale with natural wrapping.
    const heading = page.getByRole("heading", { level: 1 });
    await expect(heading).toBeVisible();
    expect(await computedStyle(page, "h1", "font-size")).toBe("32px");
    expect(await computedStyle(page, "h1", "font-weight")).toBe("500");

    const plane = page.locator("main svg").first();
    await expect(plane).toBeVisible();
    await expect(plane).toHaveAttribute("aria-hidden", "true");
    expect(await plane.evaluate(el => getComputedStyle(el).pointerEvents)).toBe("none");

    for (const copy of REMOVED_COPY) {
      await expect(page.locator("main").getByText(copy, { exact: true })).toHaveCount(0);
    }

    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    );
    expect(overflow).toBeLessThanOrEqual(0);
  });
});

test("Compare keeps its own hero copy when the Recommend hero ships", async ({ page }) => {
  await mockCatalog(
    page,
    catalogWith([{ name: "University of Toronto", country: "Canada" }]),
  );
  await page.route("**/api/v1/mappings?**", route =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(compareMappings),
    }),
  );

  await page.goto(
    `/compare?degree=${encodeURIComponent("Computer Science")}&uni=${encodeURIComponent("University of Toronto")}`,
  );

  // Compare content and copy are untouched: no selector leakage from the hero.
  const heading = page.getByRole("heading", { level: 1 });
  await expect(heading).toHaveCount(1);
  await expect(heading).toHaveText("Compare module mappings.");
  await expect(page.getByText("SIDE BY SIDE")).toHaveCount(1);
  await expect(
    page.getByText("Explore qualifying NUS and partner courses for one degree and university."),
  ).toHaveCount(1);
  await expect(page.getByRole("combobox", { name: "Degree programme" })).toBeVisible();
  await expect(page.getByRole("combobox", { name: "Partner university" })).toBeVisible();
  await expect(page.locator(".mapping-row")).toHaveCount(1);
});
