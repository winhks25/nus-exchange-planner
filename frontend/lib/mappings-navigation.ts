import type { Degree, Faculty, University } from "./types";

// Remembered selections that can be merged with URL parameters.
export type RememberedMappingsSelections = {
  degree?: Degree | string | null;
  faculty?: Faculty | string | null;
  university?: University | string | null;
};

// Result of merging URL search parameters with remembered selections.
export type MergedMappingsQuery = {
  degreeName: string | null;
  facultyName: string | null;
  universityName: string | null;
  cleared: {
    degree: boolean;
    faculty: boolean;
    uni: boolean;
  };
  otherParams: URLSearchParams;
};

// Extracts string name from an entity object or plain string.
export function extractName(item: { name: string } | string | null | undefined): string | null {
  if (!item) return null;
  if (typeof item === "string") {
    const trimmed = item.trim();
    return trimmed.length > 0 ? trimmed : null;
  }
  return item.name;
}

// Resolves a single query field, distinguishing missing from explicitly cleared values.
export function resolveQueryField(
  params: URLSearchParams,
  paramKey: string,
  rememberedValue: { name: string } | string | null | undefined
): { value: string | null; isExplicitlyCleared: boolean } {
  // Missing parameter: fall back to remembered selection.
  if (!params.has(paramKey)) {
    return {
      value: extractName(rememberedValue),
      isExplicitlyCleared: false,
    };
  }

  const rawValue = params.get(paramKey);
  // Present but empty: explicitly cleared, do not fall back.
  if (rawValue === null || rawValue.trim() === "") {
    return {
      value: null,
      isExplicitlyCleared: true,
    };
  }

  // Explicit non-empty value: overrides remembered selection.
  return {
    value: rawValue.trim(),
    isExplicitlyCleared: false,
  };
}

// Merges URL search parameters with remembered Mappings selections.
// Explicit URL query values take precedence; missing values fall back to remembered state.
export function mergeMappingsParams(
  query: URLSearchParams | string,
  remembered: RememberedMappingsSelections
): MergedMappingsQuery {
  const params =
    typeof query === "string" ? new URLSearchParams(query) : new URLSearchParams(query.toString());

  const degreeResult = resolveQueryField(params, "degree", remembered.degree);
  const facultyResult = resolveQueryField(params, "faculty", remembered.faculty);
  const uniResult = resolveQueryField(params, "uni", remembered.university);

  // Preserve any other query parameters.
  const otherParams = new URLSearchParams();
  for (const [key, value] of params.entries()) {
    if (key !== "degree" && key !== "faculty" && key !== "uni") {
      otherParams.append(key, value);
    }
  }

  return {
    degreeName: degreeResult.value,
    facultyName: facultyResult.value,
    universityName: uniResult.value,
    cleared: {
      degree: degreeResult.isExplicitlyCleared,
      faculty: facultyResult.isExplicitlyCleared,
      uni: uniResult.isExplicitlyCleared,
    },
    otherParams,
  };
}

// Builds a Mappings destination URL for a directory card click.
// Replaces only the university, carries remembered degree/faculty, and safely encodes names.
export function buildMappingsHref(
  targetUniversity: string,
  remembered?: RememberedMappingsSelections,
  existingParams?: URLSearchParams | string
): string {
  const params = new URLSearchParams(
    typeof existingParams === "string" ? existingParams : existingParams?.toString() ?? ""
  );

  // A directory card click sets the target university.
  params.set("uni", targetUniversity);

  // Retain remembered degree if not explicitly set or cleared in query.
  const degreeName = extractName(remembered?.degree);
  if (degreeName && !params.has("degree")) {
    params.set("degree", degreeName);
  }

  // Retain remembered faculty if not explicitly set or cleared in query.
  const facultyName = extractName(remembered?.faculty);
  if (facultyName && !params.has("faculty")) {
    params.set("faculty", facultyName);
  }

  const queryString = params.toString();
  return `/mappings${queryString ? `?${queryString}` : ""}`;
}
