import { expect, test, type Locator } from "@playwright/test";
import type { MappingResult } from "../lib/types";
import {
  catalogWith,
  fixtureDegree,
  recommendationResultVariants,
} from "./fixtures/recommendations";
import { mockCatalog, openRecommendWithFixtures } from "./helpers/recommendation-fixtures";

const SYSTEM_FONT_STACK =
  '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, ' +
  '"Noto Sans", "Liberation Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", ' +
  '"Segoe UI Symbol", "Noto Color Emoji"';

const SURFACE = "rgb(34, 35, 36)";
const BODY_GRAY = "rgb(181, 181, 181)";
const EMPHASIS = "rgb(221, 221, 221)";
const NAV_GRAY = "rgb(163, 163, 163)";
const PLACEHOLDER_GRAY = "rgb(174, 177, 181)";
const BORDER_GRAY = "rgb(72, 72, 72)";
const SUBTLE_GRAY = "rgb(41, 41, 41)";
// Accent follows the user's committed cyan override of --primary/--ring.
const ACCENT = "rgb(0, 197, 255)";
const RING = "rgb(0, 249, 255)";

async function computed(
  locator: Locator,
  properties: string[],
  pseudo?: string,
): Promise<Record<string, string>> {
  return locator.evaluate(
    (element, options) => {
      const style = getComputedStyle(element, options.pseudo ?? null);
      return Object.fromEntries(
        options.properties.map(property => [property, style.getPropertyValue(property).trim()]),
      );
    },
    { properties, pseudo },
  );
}

function normalizedFontStack(value: string): string {
  return value.replace(/\s+/g, " ").trim();
}

const compareMappings: MappingResult = {
  degree: fixtureDegree.name,
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

test("body and existing chrome use the source type scale and gray palette", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("combobox", { name: "Degree programme" })).toBeVisible();

  const declaredStack = await page.evaluate(() =>
    getComputedStyle(document.documentElement).getPropertyValue("--font-system"),
  );
  expect(normalizedFontStack(declaredStack)).toBe(SYSTEM_FONT_STACK);

  const body = await computed(page.locator("body"), [
    "font-family",
    "font-size",
    "line-height",
    "color",
    "background-color",
  ]);
  expect(normalizedFontStack(body["font-family"])).toBe(
    SYSTEM_FONT_STACK.replace("BlinkMacSystemFont", '"system-ui"'),
  );
  expect(body["font-size"]).toBe("16px");
  expect(body["line-height"]).toBe("24px");
  expect(body.color).toBe(BODY_GRAY);
  expect(body["background-color"]).toBe(SURFACE);

  const hero = await computed(page.getByRole("heading", { level: 1 }), [
    "font-size",
    "font-weight",
    "line-height",
    "color",
  ]);
  expect(hero["font-size"]).toBe("40px");
  expect(hero["font-weight"]).toBe("500");
  expect(hero["line-height"]).toBe("48px");
  expect(hero.color).toBe(EMPHASIS);

  const brand = await computed(page.locator("header").getByRole("link"), [
    "font-size",
    "font-weight",
    "color",
  ]);
  expect(brand["font-size"]).toBe("20px");
  expect(brand["font-weight"]).toBe("700");
  // Brand renders in the accent since the rounded-header restyle.
  expect(brand.color).toBe(ACCENT);

  const navLink = page.getByRole("navigation").getByRole("link", { name: "Compare" });
  const nav = await computed(navLink, ["font-size", "font-weight", "color"]);
  expect(nav["font-size"]).toBe("16px");
  expect(nav["font-weight"]).toBe("400");
  expect(nav.color).toBe(NAV_GRAY);
  await expect(navLink).toHaveAttribute("href", "/compare");

  const header = await computed(page.locator("header"), [
    "border-bottom-width",
    "border-bottom-style",
    "border-bottom-color",
  ]);
  expect(header["border-bottom-width"]).toBe("1px");
  expect(header["border-bottom-style"]).toBe("solid");
  expect(header["border-bottom-color"]).toBe(BORDER_GRAY);

  await navLink.hover();
  await expect
    .poll(async () => (await computed(navLink, ["color"])).color)
    .toBe(ACCENT);

  await expect(page.getByRole("link", { name: "Recommend" })).toHaveAttribute("href", "/");
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await expect(page.getByRole("article")).toHaveCount(0);
});

test("cards use source surfaces, radii and tier type sizes", async ({ page }) => {
  await openRecommendWithFixtures(page, {
    recommendations: recommendationResultVariants.six,
  });

  const cards = page.getByRole("article");
  await expect(cards).toHaveCount(6);

  const firstCard = await computed(cards.nth(0), [
    "background-color",
    "border-top-width",
    "border-top-style",
    "border-top-color",
    "border-radius",
    "box-shadow",
  ]);
  expect(firstCard["background-color"]).toBe(SURFACE);
  expect(firstCard["border-top-width"]).toBe("1px");
  expect(firstCard["border-top-style"]).toBe("solid");
  expect(firstCard["border-top-color"]).toBe(BORDER_GRAY);
  expect(firstCard["border-radius"]).toBe("5.6px");
  expect(firstCard["box-shadow"]).toBe("none");

  const titleSizes = await Promise.all(
    [0, 1, 3].map(async index => {
      const title = await computed(cards.nth(index).locator("h2"), [
        "font-size",
        "font-weight",
        "line-height",
        "color",
      ]);
      return title;
    }),
  );
  for (const title of titleSizes) {
    expect(title["font-weight"]).toBe("500");
    expect(title.color).toBe(EMPHASIS);
  }
  expect(titleSizes[0]["font-size"]).toBe("32px");
  expect(titleSizes[0]["line-height"]).toBe("38.4px");
  expect(titleSizes[1]["font-size"]).toBe("24px");
  expect(titleSizes[2]["font-size"]).toBe("20px");

  const nusSizes = await Promise.all(
    [0, 1, 3].map(async index => {
      const metric = await computed(cards.nth(index).locator("p").nth(0), [
        "font-size",
        "font-weight",
        "line-height",
      ]);
      return metric;
    }),
  );
  expect(nusSizes[0]["font-size"]).toBe("24px");
  expect(nusSizes[1]["font-size"]).toBe("20px");
  expect(nusSizes[2]["font-size"]).toBe("16px");
  for (const metric of nusSizes) expect(metric["font-weight"]).toBe("500");

  const partner = await computed(cards.nth(0).locator("p").nth(1), [
    "font-size",
    "font-weight",
    "color",
  ]);
  expect(partner["font-size"]).toBe("14px");
  expect(partner["font-weight"]).toBe("400");
  expect(partner.color).toBe(BODY_GRAY);

  const badge = await computed(cards.nth(0).getByText("Canada", { exact: true }), [
    "font-size",
    "font-weight",
    "background-color",
    "color",
    "border-top-width",
    "border-top-color",
    "border-radius",
  ]);
  expect(badge["font-size"]).toBe("12px");
  expect(badge["font-weight"]).toBe("400");
  expect(badge["background-color"]).toBe(SUBTLE_GRAY);
  expect(badge.color).toBe(BODY_GRAY);
  expect(badge["border-top-width"]).toBe("1px");
  expect(badge["border-top-color"]).toBe(BORDER_GRAY);
  expect(badge["border-radius"]).toBe("4px");

  const action = await computed(cards.nth(0).getByRole("link"), [
    "font-size",
    "font-weight",
    "color",
    "border-top-width",
    "border-top-color",
    "border-radius",
  ]);
  expect(action["font-size"]).toBe("14px");
  expect(action["font-weight"]).toBe("400");
  expect(action.color).toBe(ACCENT);
  expect(action["border-top-width"]).toBe("1px");
  expect(action["border-top-color"]).toBe(ACCENT);
  expect(action["border-radius"]).toBe("4px");
  await expect(cards.nth(0).getByRole("link", { name: /View Mappings/ })).toBeVisible();
});

test("picker and dropdown expose source placeholder, focus and hover states", async ({ page }) => {
  await page.goto("/");
  const picker = page.getByRole("combobox", { name: "Degree programme" });
  await expect(picker).toBeVisible();

  const idle = await computed(picker, [
    "font-size",
    "background-color",
    "border-top-width",
    "border-top-color",
    "border-radius",
  ]);
  expect(idle["font-size"]).toBe("16px");
  expect(idle["background-color"]).toBe(SURFACE);
  expect(idle["border-top-width"]).toBe("1px");
  expect(idle["border-top-color"]).toBe(BORDER_GRAY);
  expect(idle["border-radius"]).toBe("4px");

  const placeholder = await computed(picker, ["color"], "::placeholder");
  expect(placeholder.color).toBe(PLACEHOLDER_GRAY);

  await picker.focus();
  await expect
    .poll(async () => (await computed(picker, ["border-top-color"]))["border-top-color"])
    .toBe(ACCENT);
  const focused = await computed(picker, ["box-shadow"]);
  expect(focused["box-shadow"]).toContain("3.2px");
  expect(focused["box-shadow"]).toContain(RING);

  await picker.click();
  const listbox = page.getByRole("listbox");
  await expect(listbox).toBeVisible();
  const dropdown = await computed(listbox, [
    "background-color",
    "border-top-width",
    "border-top-color",
    "border-radius",
    "box-shadow",
  ]);
  expect(dropdown["background-color"]).toBe(SURFACE);
  expect(dropdown["border-top-width"]).toBe("1px");
  expect(dropdown["border-top-color"]).toBe(BORDER_GRAY);
  expect(dropdown["border-radius"]).toBe("4px");
  expect(dropdown["box-shadow"]).toMatch(/rgba\(0, 0, 0, 0\.25\) 0px 2px 6px/);

  const option = page.getByRole("option").first();
  await option.hover();
  await expect
    .poll(async () => (await computed(option, ["background-color"]))["background-color"])
    .toBe(SUBTLE_GRAY);
});

test("Compare keeps its controls and content with the same theme tokens", async ({ page }) => {
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
    `/compare?degree=${encodeURIComponent(fixtureDegree.name)}&uni=${encodeURIComponent("University of Toronto")}`,
  );

  const degree = page.getByRole("combobox", { name: "Degree programme" });
  const university = page.getByRole("combobox", { name: "Partner university" });
  await expect(degree).toHaveValue(fixtureDegree.name);
  await expect(university).toHaveValue("University of Toronto");
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await expect(page.locator(".mapping-row")).toHaveCount(1);

  const degreeStyle = await computed(degree, [
    "background-color",
    "border-top-width",
    "border-top-color",
    "border-radius",
  ]);
  expect(degreeStyle["background-color"]).toBe(SURFACE);
  expect(degreeStyle["border-top-width"]).toBe("1px");
  expect(degreeStyle["border-top-color"]).toBe(BORDER_GRAY);
  expect(degreeStyle["border-radius"]).toBe("4px");

  const summary = await computed(page.locator(".result-count"), [
    "color",
    "font-size",
    "line-height",
  ]);
  expect(summary.color).toBe(BODY_GRAY);
  expect(summary["font-size"]).toBe("16px");
  expect(summary["line-height"]).toBe("24px");
  await expect(page.locator(".result-count")).toContainText("1 mappable partner modules");
  await expect(page.locator(".result-count")).toContainText("1 distinct NUS modules");
  await expect(page.locator(".result-count")).toContainText("1 mappings");

  const row = await computed(page.locator(".mapping-row").first(), [
    "background-color",
    "border-top-width",
    "border-top-color",
    "border-radius",
  ]);
  expect(row["background-color"]).toBe(SURFACE);
  expect(row["border-top-width"]).toBe("1px");
  expect(row["border-top-color"]).toBe(BORDER_GRAY);
  expect(row["border-radius"]).toBe("5.6px");

  const course = await computed(page.locator(".course span").first(), ["color"]);
  expect(course.color).toBe(BODY_GRAY);
  const units = await computed(page.locator(".course small").first(), ["color"]);
  expect(units.color).toBe(NAV_GRAY);
  const mapsTo = await computed(page.locator(".maps-to"), ["color"]);
  expect(mapsTo.color).toBe(NAV_GRAY);
});
