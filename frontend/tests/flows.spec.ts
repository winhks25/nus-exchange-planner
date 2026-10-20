import { expect, test } from "@playwright/test";

test("Recommend keyboard search, ranking, zero card, and Compare deep link", async ({ page }) => {
  await page.goto("/");
  const picker = page.getByRole("combobox", { name: "Degree programme" });
  await expect(picker).toBeVisible();
  await expect(page.getByRole("region", { name: "Ranked partner universities" })).toHaveCount(0);
  await picker.click();
  await expect(page.getByRole("option")).toHaveCount(6);
  await picker.fill("computer science");
  await picker.press("ArrowDown");
  await expect(picker).toHaveAttribute("aria-activedescendant", /option-0/);
  await picker.press("Enter");
  await expect(picker).toHaveValue("Computer Science");
  const cards = page.getByRole("article");
  await expect(cards).toHaveCount(5);
  await expect(cards.first()).toContainText("University of Toronto");
  await expect(cards.first().locator(".card-count")).toHaveText("6mappable partner modules");
  await expect(cards.first().locator(".card-secondary-counts")).toContainText("distinct NUS modules3");
  await expect(cards.first().locator(".card-secondary-counts")).toContainText("mappings6");
  const zeroCards = cards.filter({ hasText: "0mappable partner modules" });
  await expect(zeroCards).toHaveCount(2);
  for (const card of await zeroCards.all()) {
    await expect(card.locator(".card-secondary-counts")).toContainText("distinct NUS modules0");
    await expect(card.locator(".card-secondary-counts")).toContainText("mappings0");
  }
  await cards.first().getByRole("link", { name: /View Mappings/ }).click();
  await expect(page).toHaveURL(/compare\?degree=Computer%20Science&uni=University%20of%20Toronto/);
  await expect(page.getByRole("combobox", { name: "Degree programme" })).toHaveValue("Computer Science");
  await expect(page.getByLabel("Partner university")).toHaveValue("University of Toronto");
  await expect(page.getByText("3 distinct NUS modules")).toBeVisible();
  await expect(page.locator(".mapping-row")).toHaveCount(6);
});

test("Artificial Intelligence counts reconcile from Recommend to Compare", async ({ page }) => {
  await page.goto("/");
  const picker = page.getByRole("combobox", { name: "Degree programme" });
  await picker.click();
  await picker.fill("Artificial Intelligence");
  await picker.press("Enter");
  const cards = page.getByRole("article");
  await expect(cards).toHaveCount(5);
  const toronto = cards.first();
  await expect(toronto.locator(".rank")).toHaveText("#1");
  await expect(toronto).toContainText("University of Toronto");
  await expect(toronto.locator(".card-count")).toHaveText("9mappable partner modules");
  await expect(toronto.locator(".card-secondary-counts")).toContainText("distinct NUS modules6");
  await expect(toronto.locator(".card-secondary-counts")).toContainText("mappings9");
  await toronto.getByRole("link", { name: /View Mappings/ }).click();
  await expect(page).toHaveURL(/degree=Artificial%20Intelligence&uni=University%20of%20Toronto/);
  const summary = page.locator(".result-count");
  await expect(summary).toContainText("9 mappable partner modules");
  await expect(summary).toContainText("6 distinct NUS modules");
  await expect(summary).toContainText("9 mappings");
  await expect(page.getByText(/One NUS module can have several partner mappings/)).toBeVisible();
  await expect(page.locator(".mapping-row")).toHaveCount(9);
  await page.getByLabel("Partner university").selectOption("University of Western Australia, The");
  await expect(summary).toContainText("0 mappable partner modules");
  await expect(summary).toContainText("0 distinct NUS modules");
  await expect(summary).toContainText("0 mappings");
  await expect(page.locator(".mapping-row")).toHaveCount(0);
  await expect(page.getByText(/No qualifying mappings/)).toBeVisible();
});

test("clearing selection, invalid link, and zero match", async ({ page }) => {
  await page.goto("/compare?degree=bad&uni=University%20of%20Toronto");
  await expect(page.getByText(/unknown degree or partner university/)).toBeVisible();
  await expect(page.getByRole("combobox", { name: "Degree programme" })).toHaveValue("");
  await expect(page.getByLabel("Partner university")).toHaveValue("University of Toronto");
  const picker = page.getByRole("combobox", { name: "Degree programme" });
  await picker.fill("Computer Science"); await picker.press("Enter");
  await expect(page.locator(".mapping-row")).toHaveCount(6);
  await picker.fill("");
  await expect(page.locator(".mapping-row")).toHaveCount(0);
  await picker.fill("Computer Science"); await picker.press("Enter");
  await page.getByLabel("Partner university").selectOption("Yonsei University");
  await expect(page.getByText(/No qualifying mappings/)).toBeVisible();
  await expect(page.getByRole("link", { name: "Back to Recommend" })).toBeVisible();
});

test("no match and service error have clear states", async ({ page }) => {
  await page.goto("/");
  const picker = page.getByRole("combobox", { name: "Degree programme" });
  await picker.fill("impossible programme");
  await expect(page.getByText("Program not available. Check the degree list.")).toBeVisible();
  await expect(page.getByText("Choose a degree to see results.")).toBeVisible();
  await page.route("**/api/v1/catalog", route => route.fulfill({ status: 503, contentType: "application/json", body: '{"detail":"Catalog data is unavailable"}' }));
  await page.reload();
  await expect(page.locator("main [role=alert]")).toContainText("mapping service is unavailable");
  await expect(page.getByRole("article")).toHaveCount(0);
});

test("keyboard boundaries, Escape, and zero-count navigation", async ({ page }) => {
  await page.goto("/");
  const picker = page.getByRole("combobox", { name: "Degree programme" });
  await picker.fill("Computer Science"); await picker.press("Enter");
  await expect(page.getByRole("article")).toHaveCount(5);
  await picker.click();
  await picker.press("End");
  await expect(picker).toHaveAttribute("aria-activedescendant", /option-5/);
  await picker.press("Home");
  await expect(picker).toHaveAttribute("aria-activedescendant", /option-0/);
  await picker.press("Escape");
  await expect(picker).toHaveValue("Computer Science");
  await expect(picker).toHaveAttribute("aria-expanded", "false");
  const zero = page.getByRole("article").filter({ hasText: "Yonsei University" });
  await expect(zero.locator(".card-count")).toHaveText("0mappable partner modules");
  await zero.getByRole("link", { name: /View Mappings/ }).click();
  await expect(page.getByText(/No qualifying mappings/)).toBeVisible();
});

test("Compare ignores a delayed response for an old pair", async ({ page }) => {
  await page.route("**/api/v1/mappings?**", async route => {
    if (route.request().url().includes("University%20of%20Toronto")) await new Promise(resolve => setTimeout(resolve, 800));
    try { await route.continue(); } catch { /* The old request may be aborted. */ }
  });
  await page.goto("/compare?degree=Computer%20Science&uni=University%20of%20Toronto");
  await expect(page.getByLabel("Partner university")).toHaveValue("University of Toronto");
  await page.getByLabel("Partner university").selectOption("Kyoto University");
  await expect(page.getByText("1 distinct NUS modules")).toBeVisible();
  await page.waitForTimeout(1000);
  await expect(page.getByText("1 distinct NUS modules")).toBeVisible();
  await expect(page.locator(".mapping-row")).toHaveCount(1);
});

test("warmed Recommend result renders within one second", async ({ page }) => {
  await page.goto("/");
  const picker = page.getByRole("combobox", { name: "Degree programme" });
  await expect(picker).toBeVisible();
  await picker.fill("Computer Science");
  const start = await page.evaluate(() => performance.now());
  await picker.press("Enter");
  await expect(page.getByRole("article")).toHaveCount(5);
  const elapsed = await page.evaluate(startTime => performance.now() - startTime, start);
  console.log(`WARM_RENDER_MS=${elapsed.toFixed(1)}`);
  expect(elapsed).toBeLessThan(1000);
});

test("Compare leaves absent partner units blank and keeps source titles", async ({ page }) => {
  await page.route("**/api/v1/mappings?**", route => route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({
    degree: "Computer Science", university: "University of Toronto", distinct_nus_module_count: 1,
    mappings: [{ nus_course: { code: "CS2106", title: "Introduction to Operating", units: 4 }, partner_course: { code: "ECE344H1", title: "Operating Systems" } }],
  }) }));
  await page.goto("/compare?degree=Computer%20Science&uni=University%20of%20Toronto");
  await expect(page.getByText("Introduction to Operating")).toBeVisible();
  const sides = page.locator(".mapping-row .course");
  await expect(sides.first()).toContainText("4 units");
  await expect(sides.last()).not.toContainText("units");
});
