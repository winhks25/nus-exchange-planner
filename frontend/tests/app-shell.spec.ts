import { expect, test } from "@playwright/test";

const BRAND_TEXT = "nus exchange planner";

function expectNear(actual: number, target: number, tolerance = 8) {
  expect(Math.abs(actual - target)).toBeLessThanOrEqual(tolerance);
}

async function frameGeometry(page: import("@playwright/test").Page) {
  return page.locator("header").evaluate(el => {
    const box = el.parentElement!.getBoundingClientRect();
    return { x: box.x, y: box.y, width: box.width, right: box.right };
  });
}

test.describe("header content", () => {
  for (const route of ["/", "/compare"]) {
    test(`the header row holds only the brand link on ${route}`, async ({ page }) => {
      await page.goto(route);

      const header = page.locator("header");
      await expect(header).toHaveCount(1);

      const brand = header.getByRole("link");
      await expect(brand).toHaveCount(1);
      await expect(brand).toHaveText(BRAND_TEXT);
      await expect(brand).toHaveAttribute("href", "/");

      // No navigation, icon, search, subtitle or actions belong in the header.
      await expect(header.locator("nav, svg, img, input, button, textarea, p, h1, ul, li")).toHaveCount(0);
    });
  }
});

test.describe("reference geometry at 1888x1337", () => {
  test.use({ viewport: { width: 1888, height: 1337 } });

  test("the Recommend frame and header match the reference anchors", async ({ page }) => {
    await page.goto("/");
    const header = page.locator("header");
    await expect(header).toBeVisible();
    await expect(header.getByRole("link")).toHaveCount(1);

    expectNear((await frameGeometry(page)).x, 18);
    expectNear((await frameGeometry(page)).y, 14);
    expectNear((await frameGeometry(page)).width, 1745);

    const headerBox = await header.boundingBox();
    expectNear(headerBox!.y + headerBox!.height, 102);
    expectNear(headerBox!.height, 88);

    const brandBox = await header.getByRole("link").boundingBox();
    expectNear(brandBox!.x, 83);
    expectNear(brandBox!.y, 44);
  });

  test("the Compare frame keeps the same shell geometry", async ({ page }) => {
    await page.goto("/compare");

    const header = page.locator("header");
    await expect(header).toBeVisible();
    await expect(header.getByRole("link")).toHaveCount(1);

    expectNear((await frameGeometry(page)).x, 18);
    expectNear((await frameGeometry(page)).y, 14);
    expectNear((await frameGeometry(page)).width, 1745);
  });
});

test.describe("narrow screen containment", () => {
  test.use({ viewport: { width: 390, height: 844 } });

  test("the shell stays contained at 390px", async ({ page }) => {
    await page.goto("/");

    const header = page.locator("header");
    await expect(header).toBeVisible();
    await expect(header.getByRole("link")).toHaveText(BRAND_TEXT);

    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    );
    expect(overflow).toBeLessThanOrEqual(0);

    const frame = await frameGeometry(page);
    expect(frame.x).toBe(12);
    expect(frame.right).toBeLessThanOrEqual(390);

    const brandBox = await header.getByRole("link").boundingBox();
    expect(brandBox!.x).toBeGreaterThanOrEqual(0);

    await expect(page.getByRole("navigation")).toBeVisible();
    await expect(page.locator("header nav")).toHaveCount(0);
  });
});

test.describe("shell persistence", () => {
  test("client navigation keeps one shell and identical header dimensions", async ({ page }) => {
    await page.goto("/");
    const header = page.locator("header");
    await expect(page.getByRole("combobox", { name: "Degree programme" })).toBeVisible();
    const boxBefore = await header.boundingBox();

    // Mark the rendered node so it can be recognized after navigation.
    await header.evaluate(el => {
      (el as HTMLElement).dataset.shellProbe = "us2";
    });

    await page.getByRole("navigation").getByRole("link", { name: "Compare" }).click();
    await page.waitForURL("**/compare");
    await expect(page.getByRole("heading", { name: "Compare module mappings." })).toBeVisible();

    expect(await page.evaluate(() => performance.getEntriesByType("navigation").length)).toBe(1);
    await expect(header).toHaveCount(1);
    expect(await header.evaluate(el => (el as HTMLElement).dataset.shellProbe)).toBe("us2");

    const boxAfter = await header.boundingBox();
    expect(boxAfter!.width).toBe(boxBefore!.width);
    expect(boxAfter!.height).toBe(boxBefore!.height);

    await expect(page.locator("header nav")).toHaveCount(0);
  });
});
