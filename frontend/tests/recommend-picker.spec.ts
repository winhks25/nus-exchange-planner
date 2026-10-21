import { expect, test } from "@playwright/test";
import type { Recommendation } from "../lib/types";
import {
  catalogWith,
  fixtureCatalog,
  fixtureDegree,
  recommendationsFor,
  recommendationResultVariants,
} from "./fixtures/recommendations";
import { installRecommendationFixtures, mockCatalog } from "./helpers/recommendation-fixtures";

// Exact Recommend picker copy from the UI contract.
const RECOMMEND_LABEL = "Degree Programme";
const RECOMMEND_PLACEHOLDER = "Choose your degree programme";
// Compare keeps its original wording after the Recommend restyle.
const COMPARE_LABEL = "Degree programme";
const COMPARE_PLACEHOLDER = "Search degree programmes";

const artificialIntelligenceDegree = {
  name: "Artificial Intelligence",
  degree: "Bachelor of Computing (Artificial Intelligence)",
};

const slowRecommendation: Recommendation = {
  university: "Slow University",
  country: "Canada",
  distinct_nus_module_count: 1,
  partner_module_count: 1,
  mapping_count: 1,
};

const fastRecommendation: Recommendation = {
  university: "Fast University",
  country: "Japan",
  distinct_nus_module_count: 2,
  partner_module_count: 2,
  mapping_count: 2,
};

test("Recommend centres the picker with the exact label and placeholder", async ({ page }) => {
  await page.setViewportSize({ width: 1888, height: 1337 });
  await mockCatalog(page);
  await page.goto("/");

  const picker = page.getByRole("combobox", { name: RECOMMEND_LABEL, exact: true });
  await expect(picker).toBeVisible();
  await expect(picker).toHaveAttribute("placeholder", RECOMMEND_PLACEHOLDER);
  await expect(page.locator("main label")).toHaveText(RECOMMEND_LABEL);
  await expect(page.getByRole("article")).toHaveCount(0);

  // Reference picker anchor at 1888px: 526x60 at x726/y405.
  const box = await picker.boundingBox();
  expect(box).not.toBeNull();
  expect(Math.abs(box!.x - 726)).toBeLessThanOrEqual(8);
  expect(Math.abs(box!.y - 405)).toBeLessThanOrEqual(8);
  expect(Math.abs(box!.width - 526)).toBeLessThanOrEqual(8);
  expect(Math.abs(box!.height - 60)).toBeLessThanOrEqual(8);

  // The label text is centred over the field near x990.
  const labelCenter = await page.locator("main label").evaluate(element => {
    const range = document.createRange();
    range.selectNodeContents(element);
    const rect = range.getBoundingClientRect();
    return rect.x + rect.width / 2;
  });
  expect(Math.abs(labelCenter - 990)).toBeLessThanOrEqual(8);
});

test("focus lists every degree and filters by major and full title", async ({ page }) => {
  await installRecommendationFixtures(page, {
    recommendations: recommendationResultVariants.two,
  });
  await page.goto("/");

  const picker = page.getByRole("combobox", { name: RECOMMEND_LABEL, exact: true });
  await picker.focus();
  await expect(page.getByRole("option")).toHaveCount(2);

  // Match the major name.
  await picker.fill("business analytics");
  await expect(page.getByRole("option")).toHaveCount(1);
  await expect(page.getByRole("option")).toContainText("Business Analytics");

  // Match the full degree title.
  await picker.fill("computing");
  await expect(page.getByRole("option")).toHaveCount(1);
  await expect(page.getByRole("option")).toContainText("Computer Science");

  await picker.fill("bachelor");
  await expect(page.getByRole("option")).toHaveCount(2);

  await picker.fill("impossible programme");
  await expect(page.getByRole("option")).toHaveCount(0);
  await expect(page.getByText("Program not available. Check the degree list.")).toBeVisible();
});

test("arrow, Home, End, Enter and Escape keys keep the picker usable", async ({ page }) => {
  await installRecommendationFixtures(page, {
    recommendations: recommendationResultVariants.two,
  });
  await page.goto("/");

  const picker = page.getByRole("combobox", { name: RECOMMEND_LABEL, exact: true });
  await picker.focus();
  await expect(page.getByRole("option")).toHaveCount(2);

  await picker.press("ArrowDown");
  await expect(picker).toHaveAttribute("aria-activedescendant", /option-0/);
  await picker.press("ArrowDown");
  await expect(picker).toHaveAttribute("aria-activedescendant", /option-1/);
  await picker.press("ArrowUp");
  await expect(picker).toHaveAttribute("aria-activedescendant", /option-0/);
  await picker.press("End");
  await expect(picker).toHaveAttribute("aria-activedescendant", /option-1/);
  await picker.press("Home");
  await expect(picker).toHaveAttribute("aria-activedescendant", /option-0/);

  await picker.press("Enter");
  await expect(picker).toHaveValue("Computer Science");
  await expect(picker).toHaveAttribute("aria-expanded", "false");

  // Escape closes the reopened list and keeps the committed degree.
  await picker.click();
  await expect(picker).toHaveAttribute("aria-expanded", "true");
  await picker.press("Escape");
  await expect(picker).toHaveValue("Computer Science");
  await expect(picker).toHaveAttribute("aria-expanded", "false");
});

test("clearing the degree removes results immediately", async ({ page }) => {
  await installRecommendationFixtures(page, {
    recommendations: recommendationResultVariants.two,
  });
  await page.goto("/");

  const picker = page.getByRole("combobox", { name: RECOMMEND_LABEL, exact: true });
  await picker.fill("Computer Science");
  await picker.press("Enter");
  await expect(page.getByRole("article")).toHaveCount(2);

  await picker.fill("");
  await expect(page.getByRole("article")).toHaveCount(0);
  await expect(page.getByText("Choose a degree to see results.")).toBeVisible();
  await expect(picker).toHaveAttribute("placeholder", RECOMMEND_PLACEHOLDER);
});

test("a delayed old recommendation response cannot replace the new degree", async ({ page }) => {
  await mockCatalog(page, {
    degrees: [fixtureDegree, artificialIntelligenceDegree],
    universities: [],
  });
  await page.route("**/api/v1/recommendations?**", async route => {
    const degree = new URL(route.request().url()).searchParams.get("degree");
    if (degree === "Computer Science") await new Promise(resolve => setTimeout(resolve, 800));
    const recommendations =
      degree === "Computer Science" ? [slowRecommendation] : [fastRecommendation];
    await route
      .fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(recommendationsFor(degree ?? "", recommendations)),
      })
      .catch(() => undefined);
  });
  await page.goto("/");

  const picker = page.getByRole("combobox", { name: RECOMMEND_LABEL, exact: true });
  await picker.fill("Computer Science");
  await picker.press("Enter");
  await picker.fill("Artificial Intelligence");
  await picker.press("Enter");

  await expect(page.getByRole("article")).toHaveCount(1);
  await expect(page.getByRole("article")).toContainText("Fast University");
  await page.waitForTimeout(1000);
  await expect(page.getByRole("article")).toHaveCount(1);
  await expect(page.getByRole("article")).toContainText("Fast University");
  await expect(page.getByText("Slow University")).toHaveCount(0);
});

test("catalog loading and error keep the picker state explicit", async ({ page }) => {
  await page.route("**/api/v1/catalog", async route => {
    await new Promise(resolve => setTimeout(resolve, 400));
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(fixtureCatalog),
    });
  });
  await page.goto("/");
  await expect(page.getByRole("status")).toHaveText("Loading degree programmes…");
  await expect(page.getByRole("combobox", { name: RECOMMEND_LABEL, exact: true })).toBeVisible();

  await page.unroute("**/api/v1/catalog");
  await page.route("**/api/v1/catalog", route =>
    route.fulfill({
      status: 503,
      contentType: "application/json",
      body: '{"detail":"Catalog data is unavailable"}',
    }),
  );
  await page.reload();
  await expect(page.locator("main [role=alert]")).toContainText("mapping service is unavailable");
  await expect(page.getByRole("combobox")).toHaveCount(0);
});

test("Compare retains its original degree label and placeholder", async ({ page }) => {
  await mockCatalog(page, catalogWith());
  await page.goto("/compare");

  const picker = page.getByRole("combobox", { name: COMPARE_LABEL, exact: true });
  await expect(picker).toBeVisible();
  await expect(picker).toHaveAttribute("placeholder", COMPARE_PLACEHOLDER);
  await expect(page.locator("main label").first()).toHaveText(COMPARE_LABEL);
});
