import type { Catalog, MappingResult, Recommendations } from "./types";

export class ApiError extends Error {
  constructor(public kind: "not-found" | "unavailable", message: string) {
    super(message);
  }
}

const base = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

async function get<T>(path: string, signal?: AbortSignal): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${base}/api/v1${path}`, { signal });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") throw error;
    throw new ApiError("unavailable", "The mapping service is unavailable. Please try again.");
  }

  if (response.status === 404) {
    throw new ApiError("not-found", "The selected degree or university was not found.");
  }
  if (!response.ok) throw new ApiError("unavailable", "The mapping service is unavailable. Please try again.");
  return response.json() as Promise<T>;
}

export const getCatalog = (signal?: AbortSignal) => get<Catalog>("/catalog", signal);

export const getRecommendations = (degree: string, signal?: AbortSignal) =>
  get<Recommendations>(`/recommendations?degree=${encodeURIComponent(degree)}`, signal);

export const getMappings = (degree: string, university: string, signal?: AbortSignal) =>
  get<MappingResult>(
    `/mappings?degree=${encodeURIComponent(degree)}&uni=${encodeURIComponent(university)}`,
    signal
  );
