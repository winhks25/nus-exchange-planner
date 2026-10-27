import { expect, test } from "@playwright/test";

for (const path of ["/", "/mappings"]) {
  test(`faculty transitions and constrained search on ${path}`, async ({ page }) => {
    await page.route("**/api/v1/catalog", async route => {
      const data = await (await route.fetch()).json();
      data.faculties = [{ id: 1, name: "Alpha Faculty" }, { id: 2, name: "Zeta Faculty" }];
      data.degrees = data.degrees.map((d: { name: string }) => ({ ...d,
        faculty_ids: d.name === "Computer Science" ? [2, 1] : [2] }));
      await route.fulfill({ json: data });
    });
    await page.goto(path);
    const faculty = page.getByRole("combobox", { name: "Faculty", exact: true });
    const degree = page.getByRole("combobox", { name: /Degree programme/i });
    await degree.fill("Computer Science");
    await degree.press("Enter");
    await expect(faculty).toHaveValue("Alpha Faculty");
    await degree.fill("uncommitted search");
    await degree.press("Tab");
    await expect(degree).toHaveValue("Computer Science");
    await faculty.fill("Zeta");
    await faculty.press("Enter");
    await expect(degree).toHaveValue("Computer Science");
    await degree.fill("Artificial Intelligence");
    await degree.press("Enter");
    await expect(faculty).toHaveValue("Zeta Faculty");
    await faculty.fill("Alpha");
    await faculty.press("Enter");
    await expect(degree).toHaveValue("");
    await degree.fill("Artificial");
    await expect(page.getByRole("option")).toHaveCount(0);
    await expect(faculty).toHaveValue("Alpha Faculty");
    await degree.press("Escape");
    await degree.fill("Computer Science");
    await degree.press("Enter");
    await page.locator(".faculty-clear").click();
    await expect(degree).toHaveValue("Computer Science");
    await expect(faculty).toHaveValue("");
    await degree.click();
    await expect(page.getByRole("option")).toHaveCount(6);
    if (path === "/mappings") {
      await page.reload();
      await expect(degree).toHaveValue("Computer Science");
      await expect(faculty).toHaveValue("");
    }
  });
}

for (const path of ["/", "/universities"]) {
  test(`immediate dependent geographic filtering on ${path}`, async ({ page }) => {
    await page.goto(path);
    if (path === "/") {
      const degree = page.getByRole("combobox", { name: /Degree programme/i });
      await degree.fill("Computer Science");
      await degree.press("Enter");
    }
    const cards = page.getByRole("article");
    await expect(cards).toHaveCount(5);
    await page.getByRole("button", { name: "Continent", exact: true }).click();
    await page.getByRole("checkbox", { name: "Asia", exact: true }).check();
    await expect(cards).toHaveCount(3);
    await page.getByRole("checkbox", { name: "North America", exact: true }).check();
    await expect(cards).toHaveCount(4);
    await page.getByRole("button", { name: "Country", exact: true }).click();
    await expect(page.getByRole("checkbox", { name: "Australia", exact: true })).toHaveCount(0);
    await page.getByRole("checkbox", { name: "Canada", exact: true }).check();
    await page.getByRole("checkbox", { name: "Japan", exact: true }).check();
    await expect(cards).toHaveCount(2);
    await page.getByRole("button", { name: "City", exact: true }).click();
    await page.getByRole("checkbox", { name: "Toronto", exact: true }).check();
    await expect(cards).toHaveCount(1);
    await page.getByRole("checkbox", { name: "Kyoto", exact: true }).check();
    await expect(cards).toHaveCount(2);
    await page.getByRole("button", { name: "Continent", exact: true }).click();
    await page.getByRole("checkbox", { name: "North America", exact: true }).uncheck();
    await expect(cards).toHaveCount(1);
    await expect(cards.first()).toContainText("Kyoto");
    await expect(page.locator(".geo-chips").filter({ hasText: /Canada|Toronto/ })).toHaveCount(0);
    await page.getByRole("button", { name: "Continent", exact: true }).click();
    while (await page.locator(".geo-clear").count()) await page.locator(".geo-clear").first().click();
    await expect(cards).toHaveCount(5);
  });

  test(`country-only catalog still exposes geographic filters on ${path}`, async ({ page }) => {
    await page.route("**/api/v1/catalog", async route => {
      const data = await (await route.fetch()).json();
      data.universities = data.universities.map((u: object) => ({ ...u, city: null, continent: null }));
      await route.fulfill({ json: data });
    });
    await page.goto(path);
    await expect(page.getByRole("button", { name: "Continent", exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "City", exact: true })).toBeVisible();
    await page.getByRole("button", { name: "Country", exact: true }).click();
    await page.getByRole("checkbox", { name: "Canada", exact: true }).check();
    if (path === "/") {
      const degree = page.getByRole("combobox", { name: /Degree programme/i });
      await degree.fill("Computer Science");
      await degree.press("Enter");
    }
    await expect(page.getByRole("article")).toHaveCount(1);
    await expect(page.getByRole("article")).toContainText("Toronto");
  });
}


test("filters remain usable on a narrow phone", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  for (const path of ["/", "/mappings", "/universities"]) {
    await page.goto(path);
    await expect(page.getByRole("combobox", { name: "Faculty", exact: true })).toBeVisible();
    if (path !== "/mappings") {
      await page.getByRole("button", { name: "Country", exact: true }).click();
      await page.getByRole("checkbox", { name: "Canada", exact: true }).check();
      await page.getByRole("checkbox", { name: "Canada", exact: true }).press("Escape");
      await expect(page.getByRole("button", { name: "Country", exact: true })).toBeFocused();
    }
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  }
});
