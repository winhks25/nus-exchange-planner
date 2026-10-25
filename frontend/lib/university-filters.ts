import { geoIdentityMatches, type GeoSelection } from "./geography";
import type { Faculty, University } from "./types";

// A university passes the directory when both active restrictions hold:
// the selected faculty (explicit availability link only — never inferred)
// and the shared geographic predicate. An absent restriction passes every
// university, so no filters return the complete catalog, including partners
// with no mappings or recorded availability (FR-12).
export function universityMatchesDirectory(
  university: University,
  faculty: Faculty | null,
  geo: GeoSelection
): boolean {
  if (faculty !== null && !university.faculty_ids.includes(faculty.id)) return false;
  return geoIdentityMatches(
    {
      country: university.country,
      city: university.city,
      continent: university.continent,
    },
    geo
  );
}

export function filterUniversities(
  universities: University[],
  faculty: Faculty | null,
  geo: GeoSelection
): University[] {
  return universities.filter(university => universityMatchesDirectory(university, faculty, geo));
}
