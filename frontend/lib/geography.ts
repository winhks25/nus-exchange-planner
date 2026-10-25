import type { University } from "./types";

// Multi-select geographic filter state (FR-06/FR-11). An empty category
// selection means that category is unrestricted.
export type GeoSelection = {
  continents: string[];
  countries: string[];
  cities: string[]; // city keys, see cityKey
};

export const EMPTY_GEO_SELECTION: GeoSelection = {
  continents: [],
  countries: [],
  cities: [],
};

export type CityOption = {
  key: string;
  city: string;
  country: string;
  // "City" while the name is unique in the visible set; "City, Country"
  // once a duplicate name appears.
  label: string;
};

export type GeoOptions = {
  continents: string[];
  countries: string[];
  cities: CityOption[];
};

// City identity is the (city, country) pair so duplicate city names in
// different countries stay distinct (spec default).
export function cityKey(city: string, country: string): string {
  return `${city}|${country}`;
}

// English alphabetical order keeps every option list deterministic.
function byName(a: string, b: string): number {
  return a.localeCompare(b, "en");
}

// Universities passing the active continent constraint; empty selection
// restricts nothing.
function withinContinents(universities: University[], continents: string[]): University[] {
  if (continents.length === 0) return universities;
  return universities.filter(u => u.continent !== null && continents.includes(u.continent));
}

// Universities passing both parent constraints (continents, then countries).
function withinParents(
  universities: University[],
  continents: string[],
  countries: string[]
): University[] {
  const pool = withinContinents(universities, continents);
  if (countries.length === 0) return pool;
  return pool.filter(u => countries.includes(u.country));
}

// FR-07: option lists come from the full university catalog, constrained by
// the active parent selections (country by continents, city by both).
export function deriveGeoOptions(universities: University[], selection: GeoSelection): GeoOptions {
  const continents = [...new Set(universities.map(u => u.continent).filter((c): c is string => c !== null))];
  continents.sort(byName);

  const countries = [...new Set(withinContinents(universities, selection.continents).map(u => u.country))];
  countries.sort(byName);

  const cityPool = withinParents(universities, selection.continents, selection.countries).filter(
    (u): u is University & { city: string } => u.city !== null
  );

  // One option per (city, country) pair, in first-seen order.
  const byKey = new Map<string, CityOption>();
  for (const u of cityPool) {
    const key = cityKey(u.city, u.country);
    if (!byKey.has(key)) byKey.set(key, { key, city: u.city, country: u.country, label: u.city });
  }

  // Disambiguate duplicate city names within the visible set.
  const nameCounts = new Map<string, number>();
  for (const option of byKey.values()) {
    nameCounts.set(option.city, (nameCounts.get(option.city) ?? 0) + 1);
  }
  const cities = [...byKey.values()];
  for (const option of cities) {
    if ((nameCounts.get(option.city) ?? 0) > 1) option.label = `${option.city}, ${option.country}`;
  }
  cities.sort((a, b) => byName(a.city, b.city) || byName(a.country, b.country));

  return { continents, countries, cities };
}

// Geography known for one recommendation university. Catalog metadata supplies
// city and continent; the recommendation itself always carries the country.
export type GeoIdentity = {
  country: string;
  city: string | null;
  continent: string | null;
};

// FR-08/FR-11: AND across categories, OR within a category. A missing value
// matches only while its category is unrestricted.
export function geoIdentityMatches(identity: GeoIdentity, selection: GeoSelection): boolean {
  if (selection.continents.length > 0) {
    if (identity.continent === null || !selection.continents.includes(identity.continent)) return false;
  }
  if (selection.countries.length > 0) {
    if (!selection.countries.includes(identity.country)) return false;
  }
  if (selection.cities.length > 0) {
    if (identity.city === null || !selection.cities.includes(cityKey(identity.city, identity.country))) return false;
  }
  return true;
}

export function isGeoSelectionEmpty(selection: GeoSelection): boolean {
  return (
    selection.continents.length === 0 &&
    selection.countries.length === 0 &&
    selection.cities.length === 0
  );
}
