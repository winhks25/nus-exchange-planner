import { expect, test } from "@playwright/test";

// These assertions require the importer-backed PostgreSQL server.
test.skip(
  process.env.TEST_CATALOG_BACKEND !== "postgres",
  "database regression suite runs with TEST_CATALOG_BACKEND=postgres",
);

const CS_TORONTO = {
  degree: "Computer Science",
  university: "University of Toronto",
  partnerModules: 7,
  distinctModules: 3,
  mappings: 7,
};

async function expectUrlPair(
  page: import("@playwright/test").Page,
  degree: string,
  university: string,
) {
  await expect
    .poll(() => {
      const params = new URL(page.url()).searchParams;
      return [params.get("degree"), params.get("uni")];
    })
    .toEqual([degree, university]);
}

test("direct mapping entry loads repaired PostgreSQL rows", async ({ page }) => {
  await page.goto(
    `/mappings?degree=${encodeURIComponent(CS_TORONTO.degree)}&uni=${encodeURIComponent(CS_TORONTO.university)}`,
  );

  await expect(page.getByRole("combobox", { name: "Degree programme" })).toHaveValue(
    CS_TORONTO.degree,
  );
  await expect(page.getByRole("combobox", { name: "Partner university" })).toHaveValue(
    CS_TORONTO.university,
  );
  const counts = page.getByRole("group", { name: "Mapping counts" });
  await expect(counts).toContainText(`${CS_TORONTO.partnerModules} mappable partner modules`);
  await expect(counts).toContainText(`${CS_TORONTO.distinctModules} distinct NUS modules`);
  await expect(counts).toContainText(`${CS_TORONTO.mappings} mappings`);
  await expect(page.locator(".mapping-row")).toHaveCount(CS_TORONTO.mappings);
});

test("degree selection navigates to imported Toronto recommendations", async ({ page }) => {
  await page.goto("/");
  const picker = page.getByRole("combobox", { name: "Degree Programme" });
  await expect(picker).toBeVisible();
  await picker.click();
  await picker.fill("Artificial Intelligence");
  await picker.press("Enter");

  const cards = page.getByRole("article");
  await expect(cards).toHaveCount(5);
  const toronto = cards.first();
  await expect(toronto).toContainText("#1");
  await expect(toronto).toContainText("University of Toronto");
  await expect(toronto).toContainText("6 NUS Modules");
  await expect(toronto).toContainText("10 Partner University Modules");

  await toronto.getByRole("link", { name: /View Mappings/ }).click();
  await expect(page).toHaveURL(/degree=Artificial%20Intelligence&uni=University%20of%20Toronto/);
  await expect(page.locator(".mapping-row")).toHaveCount(10);
  await expect(page.getByRole("group", { name: "Mapping counts" })).toContainText(
    "10 mappable partner modules",
  );
});

test("mapping selectors update URL state and counts", async ({ page }) => {
  await page.goto("/mappings");
  const degree = page.getByRole("combobox", { name: "Degree programme" });
  const university = page.getByRole("combobox", { name: "Partner university" });

  await degree.click();
  await degree.fill("Business Analytics");
  await degree.press("Enter");
  await university.click();
  await university.fill("University of Toronto");
  await university.press("Enter");

  await expectUrlPair(page, "Business Analytics", "University of Toronto");
  await expect(page.getByRole("group", { name: "Mapping counts" })).toContainText(
    "19 mappable partner modules",
  );
  await expect(page.locator(".mapping-row")).toHaveCount(19);

  await university.click();
  await university.fill("Kyoto");
  await university.press("Enter");
  await expectUrlPair(page, "Business Analytics", "Kyoto University");
  await expect(page.getByRole("group", { name: "Mapping counts" })).toContainText(
    "2 distinct NUS modules",
  );
  await expect(page.locator(".mapping-row")).toHaveCount(2);
});

test("browser back and forward restore PostgreSQL pages", async ({ page }) => {
  await page.goto(
    "/mappings?degree=Computer%20Science&uni=University%20of%20Toronto",
  );
  await expect(page.locator(".mapping-row")).toHaveCount(7);

  await page.goto("/mappings?degree=Computer%20Science&uni=Kyoto%20University");
  await expect(page.locator(".mapping-row")).toHaveCount(1);

  await page.goBack();
  await expectUrlPair(page, "Computer Science", "University of Toronto");
  await expect(page.locator(".mapping-row")).toHaveCount(7);

  await page.goForward();
  await expectUrlPair(page, "Computer Science", "Kyoto University");
  await expect(page.locator(".mapping-row")).toHaveCount(1);
});

test("valid empty pair and unavailable service have clear states", async ({ page }) => {
  await page.goto(
    "/mappings?degree=Artificial%20Intelligence&uni=University%20of%20Western%20Australia",
  );
  await expect(page.getByText(/No qualifying mappings/)).toBeVisible();
  await expect(page.getByRole("group", { name: "Mapping counts" })).toContainText(
    "0 mappable partner modules",
  );
  await expect(page.locator(".mapping-row")).toHaveCount(0);

  await page.route("**/api/v1/mappings?**", route =>
    route.fulfill({
      status: 503,
      contentType: "application/json",
      body: '{"detail":"Catalog data is unavailable"}',
    }),
  );
  await page.goto(
    "/mappings?degree=Computer%20Science&uni=University%20of%20Toronto",
  );
  await expect(page.locator("main [role=alert]")).toContainText(
    "mapping service is unavailable",
  );
  await expect(page.locator(".mapping-row")).toHaveCount(0);
});

test("loading state stays visible while PostgreSQL responds", async ({ page }) => {
  await page.goto("/mappings");
  const degree = page.getByRole("combobox", { name: "Degree programme" });
  const university = page.getByRole("combobox", { name: "Partner university" });
  await expect(degree).toBeVisible();

  await page.route("**/api/v1/mappings?**", async route => {
    await new Promise(resolve => setTimeout(resolve, 700));
    await route.continue();
  });

  await degree.click();
  await degree.fill("Computer Science");
  await degree.press("Enter");
  await university.fill("University of Toronto");
  await university.press("Enter");

  await expect(page.getByRole("status").filter({ hasText: "Loading mappings…" })).toBeVisible();
  await expect(page.locator(".mapping-row")).toHaveCount(7);
});

test("rapid selection ignores a late PostgreSQL response", async ({ page }) => {
  await page.route("**/api/v1/mappings?**", async route => {
    if (route.request().url().includes("University%20of%20Toronto")) {
      await new Promise(resolve => setTimeout(resolve, 800));
    }
    try {
      await route.continue();
    } catch {
      // The superseded request is aborted by the page.
    }
  });

  await page.goto(
    "/mappings?degree=Computer%20Science&uni=University%20of%20Toronto",
  );
  const university = page.getByRole("combobox", { name: "Partner university" });
  await expect(university).toHaveValue("University of Toronto");
  await university.fill("Kyoto");
  await university.press("ArrowDown");
  await university.press("Enter");

  await expect(page.getByText("1 distinct NUS modules")).toBeVisible();
  await page.waitForTimeout(1000);
  await expect(page.getByText("1 distinct NUS modules")).toBeVisible();
  await expect(page.locator(".mapping-row")).toHaveCount(1);
});

test("mobile layout keeps nineteen PostgreSQL mappings readable", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(
    "/mappings?degree=Business%20Analytics&uni=University%20of%20Toronto",
  );

  await expect(page.getByRole("combobox", { name: "Degree programme" })).toHaveValue(
    "Business Analytics",
  );
  await expect(page.locator(".mapping-row")).toHaveCount(19);
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
  ).toBe(true);
  await expect(page.locator(".mapping-row").first()).toBeVisible();
});
