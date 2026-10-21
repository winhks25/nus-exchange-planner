import { expect, test } from "@playwright/test";
import type { Recommendation } from "../lib/types";
import {
  apiRecommendations,
  fixtureDegree,
  longNameRecommendations,
  recommendationsFor,
  recommendationResultVariants,
} from "./fixtures/recommendations";
import { mockCatalog, openRecommendWithFixtures } from "./helpers/recommendation-fixtures";

// Reference anchors use the 1888px canvas; approximate values allow 8px.
const TOLERANCE = 8;

function expectNear(actual: number, target: number, tolerance = TOLERANCE) {
  expect(Math.abs(actual - target)).toBeLessThanOrEqual(tolerance);
}

test.describe("reference collection at 1888x1337", () => {
  test.use({ viewport: { width: 1888, height: 1337 } });

  test("six results form the centred 1-2-3 rows", async ({ page }) => {
    await openRecommendWithFixtures(page, {
      recommendations: recommendationResultVariants.six,
    });

    const cards = page.getByRole("article");
    await expect(cards).toHaveCount(6);

    const boxes = await Promise.all(
      [0, 1, 2, 3, 4, 5].map(async index => {
        const box = await cards.nth(index).boundingBox();
        expect(box).not.toBeNull();
        return box!;
      }),
    );

    // One featured card, centred and narrower than the rows below.
    expectNear(boxes[0].width, 634);
    expectNear(boxes[0].x, 678);
    expectNear(boxes[0].y, 512);
    expectNear(boxes[0].height, 270);

    // Two secondary cards share a row.
    expectNear(boxes[1].width, 505);
    expectNear(boxes[1].x, 440);
    expectNear(boxes[2].x, 1010);
    expectNear(boxes[1].y, 839);
    expectNear(boxes[2].y, 839);
    expectNear(boxes[1].height, 214);

    // Three compact cards share the final row.
    for (const [index, targetX] of [
      [3, 391],
      [4, 835],
      [5, 1244],
    ] as const) {
      expectNear(boxes[index].width, 355);
      expectNear(boxes[index].x, targetX);
      expectNear(boxes[index].y, 1095);
    }

    // Rows stay ordered and never overlap.
    expect(boxes[1].y).toBeGreaterThan(boxes[0].y + boxes[0].height);
    expect(boxes[3].y).toBeGreaterThan(boxes[1].y + boxes[1].height);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
      true,
    );

    // Theme is asserted through computed styles, not a sketch pixel baseline.
    const cardTheme = await cards.first().evaluate(element => {
      const style = getComputedStyle(element);
      return {
        background: style.backgroundColor,
        border: style.borderTopWidth,
        radius: style.borderRadius,
      };
    });
    expect(cardTheme).toEqual({
      background: "rgb(34, 35, 36)",
      border: "1px",
      radius: "5.6px",
    });
  });
});

test.describe("six-card surfaces", () => {
  test.use({ viewport: { width: 1888, height: 1337 } });

  test("production keeps real ordinals and unique universities", async ({ page }) => {
    await openRecommendWithFixtures(page, {
      recommendations: recommendationResultVariants.six,
    });

    const cards = page.getByRole("article");
    await expect(cards).toHaveCount(6);

    // Fixture order is API order; ranks are not copied from the sketch.
    for (let index = 0; index < 6; index += 1) {
      await expect(cards.nth(index)).toContainText(`#${index + 1}`);
      await expect(cards.nth(index).getByRole("heading", { level: 2 })).toHaveText(
        apiRecommendations[index].university,
      );
    }
  });

  test("the isolated harness renders the six reference cards in rows", async ({ page }) => {
    await page.goto("http://127.0.0.1:18767/");

    const cards = page.getByRole("article");
    await expect(cards).toHaveCount(6);

    const boxes = await Promise.all(
      [0, 1, 2, 3, 4, 5].map(async index => {
        const box = await cards.nth(index).boundingBox();
        expect(box).not.toBeNull();
        return box!;
      }),
    );

    // The harness reuses the collection tiers and widths.
    expectNear(boxes[0].width, 634);
    expectNear(boxes[1].width, 505);
    expectNear(boxes[2].width, 505);
    expectNear(boxes[3].width, 355);
    expectNear(boxes[1].y, boxes[2].y);
    expectNear(boxes[3].y, boxes[4].y);
    expectNear(boxes[4].y, boxes[5].y);

    // Repeated copy and #1 stay confined to this test surface.
    for (const card of await cards.all()) {
      await expect(card).toContainText("#1");
      await expect(card).toContainText("University Name");
      await expect(card).toContainText("10 NUS Modules");
      await expect(card).toContainText("12 Partner University Modules");
    }
  });
});


function expectedTier(index: number): string {
  if (index === 0) return "featured";
  if (index < 3) return "secondary";
  return "compact";
}

test.describe("collection variants at 1888x1337", () => {
  test.use({ viewport: { width: 1888, height: 1337 } });

  for (const [name, recommendations] of Object.entries(recommendationResultVariants)) {
    test(`${name} results keep one ordered collection`, async ({ page }) => {
      await openRecommendWithFixtures(page, { recommendations });

      const cards = page.getByRole("article");
      await expect(cards).toHaveCount(recommendations.length);

      for (let index = 0; index < recommendations.length; index += 1) {
        await expect(cards.nth(index)).toBeVisible();
        await expect(cards.nth(index)).toHaveAttribute("data-tier", expectedTier(index));
        await expect(cards.nth(index)).toContainText(`#${index + 1}`);
      }

      if (recommendations.length > 0) {
        const last = await cards.last().boundingBox();
        expect(last).not.toBeNull();
        await cards.last().getByRole("link", { name: "View Mappings -->" }).scrollIntoViewIfNeeded();
        await expect(
          cards.last().getByRole("link", { name: "View Mappings -->" }),
        ).toBeVisible();
      }

      expect(
        await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
      ).toBe(true);
    });
  }

  test("long titles grow inside the reference row widths", async ({ page }) => {
    await openRecommendWithFixtures(page, {
      recommendations: longNameRecommendations,
    });

    const cards = page.getByRole("article");
    await expect(cards).toHaveCount(2);
    await expect(cards.nth(0).getByRole("heading", { level: 2 })).toHaveText(
      longNameRecommendations[0].university,
    );
    await expect(cards.nth(1).getByRole("heading", { level: 2 })).toHaveText(
      longNameRecommendations[1].university,
    );

    const featured = await cards.nth(0).boundingBox();
    const secondary = await cards.nth(1).boundingBox();
    if (!featured || !secondary) throw new Error("Expected card boxes");
    expectNear(featured.width, 634);
    expectNear(secondary.width, 505);
    await expect(cards.nth(0).getByRole("link", { name: "View Mappings -->" })).toBeVisible();
    await expect(cards.nth(1).getByRole("link", { name: "View Mappings -->" })).toBeVisible();
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
    ).toBe(true);
  });

  test("the initial idle page has no collection", async ({ page }) => {
    await mockCatalog(page);
    await page.goto("/");

    await expect(page.getByRole("article")).toHaveCount(0);
    await expect(page.getByRole("region", { name: "Ranked partner universities" })).toHaveCount(0);
  });
});

test.describe("responsive collection", () => {
  test("1440 keeps the 1-2-3 composition", async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await openRecommendWithFixtures(page, {
      recommendations: recommendationResultVariants.six,
    });

    const cards = page.getByRole("article");
    await expect(cards).toHaveCount(6);
    const boxes = await Promise.all([1, 2, 3, 4, 5].map(index => cards.nth(index).boundingBox()));
    const [second, third, fourth, fifth, sixth] = boxes;
    if (!second || !third || !fourth || !fifth || !sixth) throw new Error("Expected card boxes");
    expectNear(second.y, third.y);
    expectNear(fourth.y, fifth.y);
    expectNear(fifth.y, sixth.y);
    expect(fourth.y).toBeGreaterThan(second.y);
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
    ).toBe(true);
  });

  test("1280 continues compact results in pairs", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 900 });
    await openRecommendWithFixtures(page, {
      recommendations: recommendationResultVariants.six,
    });

    const cards = page.getByRole("article");
    await expect(cards).toHaveCount(6);
    const boxes = await Promise.all([1, 2, 3, 4, 5].map(index => cards.nth(index).boundingBox()));
    const [second, third, fourth, fifth, sixth] = boxes;
    if (!second || !third || !fourth || !fifth || !sixth) throw new Error("Expected card boxes");
    expectNear(second.y, third.y);
    expectNear(fourth.y, fifth.y);
    expect(sixth.y).toBeGreaterThan(fourth.y);
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
    ).toBe(true);
  });

  test("tablet and phone stack every card in order", async ({ page }) => {
    await openRecommendWithFixtures(page, {
      recommendations: recommendationResultVariants.six,
    });

    for (const width of [768, 390]) {
      await page.setViewportSize({ width, height: 900 });
      const cards = page.getByRole("article");
      await expect(cards).toHaveCount(6);

      const boxes = await Promise.all(
        [0, 1, 2, 3, 4, 5].map(index => cards.nth(index).boundingBox()),
      );
      const first = boxes[0];
      if (!first) throw new Error("Expected card box");
      for (const [index, box] of boxes.entries()) {
        if (!box) throw new Error(`Expected card box ${index}`);
        expectNear(box.x, first.x);
        expectNear(box.width, first.width);
        if (index > 0) expect(box.y).toBeGreaterThan(boxes[index - 1]!.y);
      }

      expect(
        await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
      ).toBe(true);
    }

    // Phone type and hit target rules still apply at the end of the stack.
    const phoneTitle = await page
      .getByRole("article")
      .first()
      .getByRole("heading", { level: 2 })
      .evaluate(element => getComputedStyle(element).fontSize);
    expect(phoneTitle).toBe("24px");
    const actionHeight = await page
      .getByRole("article")
      .first()
      .getByRole("link", { name: "View Mappings -->" })
      .evaluate(element => element.getBoundingClientRect().height);
    expect(actionHeight).toBeGreaterThanOrEqual(44);
  });

  test.describe("200% zoom emulation", () => {
    test.use({ viewport: { width: 944, height: 669 }, deviceScaleFactor: 2 });

    test("the collection stacks without horizontal scroll", async ({ page }) => {
      await openRecommendWithFixtures(page, {
        recommendations: recommendationResultVariants.six,
      });

      await expect(page.getByRole("article")).toHaveCount(6);
      expect(
        await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
      ).toBe(true);
    });
  });

  test("rapid degree changes leave only the current collection", async ({ page }) => {
    const aiDegree = {
      name: "Artificial Intelligence",
      degree: "Bachelor of Computing (Artificial Intelligence)",
    };
    const slow: Recommendation = {
      university: "Slow University",
      country: "Canada",
      distinct_nus_module_count: 1,
      partner_module_count: 1,
      mapping_count: 1,
    };
    const fast: Recommendation = {
      university: "Fast University",
      country: "Japan",
      distinct_nus_module_count: 2,
      partner_module_count: 2,
      mapping_count: 2,
    };

    await mockCatalog(page, {
      degrees: [fixtureDegree, aiDegree],
      universities: [],
    });
    await page.route("**/api/v1/recommendations?**", async route => {
      const degree = new URL(route.request().url()).searchParams.get("degree");
      if (degree === fixtureDegree.name) await new Promise(resolve => setTimeout(resolve, 800));
      const list = degree === fixtureDegree.name ? [slow] : [fast];
      await route
        .fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify(recommendationsFor(degree ?? "", list)),
        })
        .catch(() => undefined);
    });
    await page.goto("/");

    const picker = page.getByRole("combobox", { name: "Degree Programme", exact: true });
    await picker.fill(fixtureDegree.name);
    await picker.press("Enter");
    await picker.fill(aiDegree.name);
    await picker.press("Enter");

    const cards = page.getByRole("article");
    await expect(cards).toHaveCount(1);
    await expect(cards.first()).toContainText("Fast University");
    await expect(cards.first()).toHaveAttribute("data-tier", "featured");
    await page.waitForTimeout(1000);
    await expect(cards).toHaveCount(1);
    await expect(cards.first()).toContainText("Fast University");
    await expect(page.getByText("Slow University")).toHaveCount(0);
  });
});
