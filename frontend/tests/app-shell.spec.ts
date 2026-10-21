import { expect, test } from "@playwright/test";

const BRAND_TEXT = "nus exchange planner";

// Exact sidebar link contract: label text and route.
const NAV_ITEMS = [
  { label: "Recommend", href: "/" },
  { label: "Compare", href: "/compare" },
];

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

test.describe("shared navigation sidebar", () => {
  for (const route of ["/", "/compare"]) {
    test(`direct load of ${route} marks only that route active`, async ({ page }) => {
      await page.goto(route);

      const nav = page.getByRole("navigation");
      await expect(nav).toHaveCount(1);

      // Exact labels and routes on both links.
      for (const { label, href } of NAV_ITEMS) {
        const link = nav.getByRole("link", { name: label, exact: true });
        await expect(link).toHaveCount(1);
        await expect(link).toHaveAttribute("href", href);
      }

      // Only the link matching the current route carries aria-current.
      for (const { label, href } of NAV_ITEMS) {
        const link = nav.getByRole("link", { name: label, exact: true });
        if (href === route) {
          await expect(link).toHaveAttribute("aria-current", "page");
        } else {
          await expect(link).not.toHaveAttribute("aria-current");
        }
      }
    });
  }

  test("keyboard activation navigates and moves the active state", async ({ page }) => {
    await page.goto("/");
    const nav = page.getByRole("navigation");

    // The sidebar links are reachable by tabbing after the header brand.
    await page.locator("header").getByRole("link").focus();
    await page.keyboard.press("Tab");
    expect(await page.evaluate(() => document.activeElement!.textContent)).toBe("Recommend");
    await page.keyboard.press("Tab");
    expect(await page.evaluate(() => document.activeElement!.textContent)).toBe("Compare");

    // Enter on the focused Compare link navigates and updates aria-current.
    await page.keyboard.press("Enter");
    const compare = nav.getByRole("link", { name: "Compare", exact: true });
    await page.waitForURL("**/compare");
    await expect(compare).toHaveAttribute("aria-current", "page");
    await expect(
      nav.getByRole("link", { name: "Recommend", exact: true }),
    ).not.toHaveAttribute("aria-current");
  });

  test("back and forward restore the active link on the persistent shell", async ({ page }) => {
    await page.goto("/compare");
    const nav = page.getByRole("navigation");
    await expect(nav.getByRole("link", { name: "Compare", exact: true })).toHaveAttribute(
      "aria-current",
      "page",
    );

    // Mark the rendered nav node so it is recognizable across history steps.
    await nav.evaluate(el => {
      (el as HTMLElement).dataset.shellProbe = "us3";
    });

    await nav.getByRole("link", { name: "Recommend", exact: true }).click();
    await expect(page).toHaveURL(/\/$/);
    await expect(nav.getByRole("link", { name: "Recommend", exact: true })).toHaveAttribute(
      "aria-current",
      "page",
    );

    // Back to /compare: same nav node, Compare active again.
    await page.goBack();
    await expect(page).toHaveURL(/\/compare/);
    await expect(nav).toHaveCount(1);
    expect(await nav.evaluate(el => (el as HTMLElement).dataset.shellProbe)).toBe("us3");
    await expect(nav.getByRole("link", { name: "Compare", exact: true })).toHaveAttribute(
      "aria-current",
      "page",
    );

    // Forward to /: Recommend active again.
    await page.goForward();
    await expect(page).toHaveURL(/\/$/);
    await expect(nav.getByRole("link", { name: "Recommend", exact: true })).toHaveAttribute(
      "aria-current",
      "page",
    );
  });

  test.describe("narrow viewport", () => {
    test.use({ viewport: { width: 390, height: 844 } });

    test("narrow screens show one visible compact navigation region", async ({ page }) => {
      await page.goto("/");

      const nav = page.getByRole("navigation");
      await expect(nav).toHaveCount(1);
      await expect(nav).toBeVisible();
      for (const { label, href } of NAV_ITEMS) {
        const link = nav.getByRole("link", { name: label, exact: true });
        await expect(link).toBeVisible();
        await expect(link).toHaveAttribute("href", href);
      }

      // The compact row sits below the site-name-only header.
      const headerBox = await page.locator("header").boundingBox();
      const navBox = await nav.boundingBox();
      expect(navBox!.y).toBeGreaterThanOrEqual(headerBox!.y + headerBox!.height);
    });
  });
});

test.describe("reference sidebar geometry at 1888x1337", () => {
  test.use({ viewport: { width: 1888, height: 1337 } });

  test("the Recommend rail matches the reference anchors", async ({ page }) => {
    await page.goto("/");

    const nav = page.getByRole("navigation");
    const navBox = await nav.boundingBox();

    // Rail starts at the frame edge; the divider edge sits at x303.
    expectNear(navBox!.x, 18);
    expectNear(navBox!.x + navBox!.width, 303);

    // Link rows at y210 and y284 with icon x45 and text x83 anchors.
    for (const [{ label }, top] of NAV_ITEMS.map((item, i) => [item, i === 0 ? 210 : 284] as const)) {
      const link = nav.getByRole("link", { name: label, exact: true });
      const linkBox = await link.boundingBox();
      expectNear(linkBox!.y, top);

      // Icons are decorative line art aligned to the row anchors.
      const iconBox = await link.locator("svg").boundingBox();
      expectNear(iconBox!.x, 45);
      const textBox = await link.locator("span").boundingBox();
      expectNear(textBox!.x, 83);
    }
  });

  test("the Compare rail keeps identical sidebar dimensions", async ({ page }) => {
    await page.goto("/");
    const navBox = await page.getByRole("navigation").boundingBox();

    await page.goto("/compare");
    const compareNavBox = await page.getByRole("navigation").boundingBox();

    expect(compareNavBox!.x).toBe(navBox!.x);
    expect(compareNavBox!.width).toBe(navBox!.width);
    expect(compareNavBox!.y).toBe(navBox!.y);
    expectNear(compareNavBox!.x + compareNavBox!.width, 303);
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
