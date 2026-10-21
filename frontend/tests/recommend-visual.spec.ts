import { expect, test } from "@playwright/test";
import { recommendationResultVariants } from "./fixtures/recommendations";
import { openRecommendWithFixtures } from "./helpers/recommendation-fixtures";

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
