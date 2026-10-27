import type { Degree, Faculty } from "./types";

// The coupled faculty/degree selection. Both values always change together
// (FR-05 atomicity), so every transition returns a complete new state.
export type Selection = {
  degree: Degree | null;
  faculty: Faculty | null;
};

export const EMPTY_SELECTION: Selection = { degree: null, faculty: null };

// Faculties have no source order; the contract fixes name (English
// alphabetical) then stable id.
export function sortFaculties(faculties: Faculty[]): Faculty[] {
  return [...faculties].sort((a, b) => a.name.localeCompare(b.name, "en") || a.id - b.id);
}

// FR-03: the faculty derived from a directly selected degree. A degree in
// several faculties resolves to the alphabetically first faculty name, with a
// stable-id tie-break; a degree with no recorded membership derives none.
export function facultyForDegree(degree: Degree, faculties: Faculty[]): Faculty | null {
  const members = sortFaculties(faculties).filter(faculty =>
    degree.faculty_ids.includes(faculty.id)
  );
  return members[0] ?? null;
}

// FR-02: the degree options visible under a selected faculty. A null faculty
// is unrestricted (all degrees); a degree with no recorded membership is
// hidden under every faculty.
export function degreesForFaculty(degrees: Degree[], faculty: Faculty | null): Degree[] {
  if (!faculty) return degrees;
  return degrees.filter(degree => degree.faculty_ids.includes(faculty.id));
}

// Whether the degree belongs to the faculty (its membership includes it).
export function degreeBelongsToFaculty(
  degree: Degree | null,
  faculty: Faculty | null
): boolean {
  return !!degree && !!faculty && degree.faculty_ids.includes(faculty.id);
}

// FR-03 / rule 2: choosing a degree re-derives its faculty in the same
// transition. Clearing the degree also clears the faculty derived from it.
export function selectDegree(
  selection: Selection,
  degree: Degree | null,
  faculties: Faculty[]
): Selection {
  if (!degree) return selection.degree ? EMPTY_SELECTION : selection;
  return { degree, faculty: facultyForDegree(degree, faculties) };
}

// FR-04 / rules 3-4: choosing a faculty keeps the current degree only when it
// belongs to that faculty, and clears an incompatible degree. Clearing the
// faculty (null) keeps the degree and reopens every degree option.
export function selectFaculty(selection: Selection, faculty: Faculty | null): Selection {
  if (!faculty) return { degree: selection.degree, faculty: null };
  if (selection.degree && !degreeBelongsToFaculty(selection.degree, faculty)) {
    return { degree: null, faculty };
  }
  return { degree: selection.degree, faculty };
}
