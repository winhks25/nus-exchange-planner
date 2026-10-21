import { expect, test } from "@playwright/test";
import type { Recommendation } from "../lib/types";
import {
  longNameRecommendations,
  recommendationResultVariants,
} from "./fixtures/recommendations";
import { openRecommendWithFixtures } from "./helpers/recommendation-fixtures";

// Exact action copy from the card contract.
const ACTION_TEXT = "View Mappings -->";

const zeroCount: Recommendation = {
  university: "Zero Count University",
  country: "New Zealand",
  distinct_nus_module_count: 0,
  partner_module_count: 0,
  mapping_count: 0,
};

const oneCount: Recommendation = {
  university: "Single Count University",
  country: "Japan",
  distinct_nus_module_count: 1,
  partner_module_count: 1,
  mapping_count: 7,
};

test("each tier shows real details, two counts and one encoded action", async ({ page }) => {
  await openRecommendWithFixtures(page, {
    recommendations: recommendationResultVariants.six,
  });

  const cards = page.getByRole("article");
  await expect(cards).toHaveCount(6);

  // Index order controls the tier without changing API order.
  const tiers = ["featured", "secondary", "secondary", "compact", "compact", "compact"];
  for (const [index, tier] of tiers.entries()) {
    await expect(cards.nth(index)).toHaveAttribute("data-tier", tier);
    await expect(cards.nth(index)).toContainText(`#${index + 1}`);
  }

  const first = cards.first();
  await expect(first.getByRole("heading", { level: 2 })).toHaveText(
    "University of Aurora Bay",
  );
  await expect(first.getByText("Canada", { exact: true })).toBeVisible();
  await expect(first).toContainText("6 NUS Modules");
  await expect(first).toContainText("9 Partner University Modules");

  // mapping_count is retained in data but never rendered as a card metric.
  await expect(cards.nth(4)).not.toContainText("22");
  await expect(first).not.toContainText("distinct");
  await expect(first).not.toContainText("mappable");

  const action = first.getByRole("link", { name: ACTION_TEXT, exact: true });
  await expect(action).toHaveCount(1);
  await expect(action).toHaveText(ACTION_TEXT);
  await expect(action).toHaveAttribute(
    "href",
    "/compare?degree=Computer%20Science&uni=University%20of%20Aurora%20Bay",
  );

  // The action is the card's only control and is not nested in another control.
  await expect(first.locator("a, button, input, select, textarea, [tabindex]")).toHaveCount(1);
  await expect(first.locator("a button, a [role=button]")).toHaveCount(0);
  for (const card of await cards.all()) {
    await expect(card.getByRole("link", { name: ACTION_TEXT, exact: true })).toHaveCount(1);
  }
});

test("zero and one counts keep the exact plural labels", async ({ page }) => {
  await openRecommendWithFixtures(page, { recommendations: [zeroCount, oneCount] });

  const cards = page.getByRole("article");
  await expect(cards).toHaveCount(2);
  await expect(cards.nth(0)).toContainText("0 NUS Modules");
  await expect(cards.nth(0)).toContainText("0 Partner University Modules");
  await expect(cards.nth(1)).toContainText("1 NUS Modules");
  await expect(cards.nth(1)).toContainText("1 Partner University Modules");
  await expect(cards.nth(1)).not.toContainText("7");
});

test("long names and countries stay complete above the action", async ({ page }) => {
  await openRecommendWithFixtures(page, { recommendations: longNameRecommendations });

  const cards = page.getByRole("article");
  await expect(cards).toHaveCount(2);

  const first = cards.first();
  await expect(first.getByRole("heading", { level: 2 })).toHaveText(
    longNameRecommendations[0].university,
  );
  await expect(
    first.getByText(longNameRecommendations[0].country, { exact: true }),
  ).toBeVisible();

  const countBox = await first.locator("p").first().boundingBox();
  const actionBox = await first.getByRole("link", { name: ACTION_TEXT, exact: true }).boundingBox();
  expect(countBox).not.toBeNull();
  expect(actionBox).not.toBeNull();
  expect(actionBox!.y).toBeGreaterThanOrEqual(countBox!.y + countBox!.height - 1);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true,
  );
  await expect(first).toContainText(`${longNameRecommendations[0].distinct_nus_module_count} NUS Modules`);
});
