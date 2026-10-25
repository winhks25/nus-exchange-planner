"use client";

import { useEffect, useMemo, useState } from "react";
import RecommendDegreeField from "@/components/recommend/RecommendDegreeField";
import RecommendHero from "@/components/recommend/RecommendHero";
import FacultyCombobox from "@/components/FacultyCombobox";
import GeographicFilters from "@/components/GeographicFilters";
import LoadingState from "@/components/loading/LoadingState";
import UniversityCards from "@/components/UniversityCards";
import { getCatalog, getRecommendations, UNAVAILABLE_MESSAGE } from "@/lib/api";
import {
  EMPTY_SELECTION,
  degreesForFaculty,
  selectDegree,
  selectFaculty,
  type Selection,
} from "@/lib/faculty-selection";
import {
  EMPTY_GEO_SELECTION,
  deriveGeoOptions,
  geoIdentityMatches,
  isGeoSelectionEmpty,
  reconcileGeography,
  type GeoIdentity,
  type GeoSelection,
} from "@/lib/geography";
import type { Catalog, Degree, Faculty, PageState, Recommendation } from "@/lib/types";
import styles from "@/components/recommend/recommend.module.css";

export default function RecommendPage() {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [selection, setSelection] = useState<Selection>(EMPTY_SELECTION);
  const [geo, setGeo] = useState<GeoSelection>(EMPTY_GEO_SELECTION);
  const [touched, setTouched] = useState(false);
  const [results, setResults] = useState<Recommendation[] | null>(null);
  const [state, setState] = useState<PageState>("loading-catalog");

  useEffect(() => {
    const controller = new AbortController();

    getCatalog(controller.signal)
      .then(data => {
        setCatalog(data);
        setState("idle");
      })
      .catch(error => {
        if (error.name !== "AbortError") setState("error");
      });

    return () => controller.abort();
  }, []);

  // Recommendations track the effective degree. A compatible faculty change
  // keeps the same degree object, so the request and results are untouched.
  useEffect(() => {
    if (!selection.degree) return;
    const controller = new AbortController();

    getRecommendations(selection.degree.name, controller.signal)
      .then(data => {
        // Ignore responses superseded by a newer selection.
        if (controller.signal.aborted) return;
        setResults(data.recommendations);
        setState("idle");
      })
      .catch(error => {
        if (error.name !== "AbortError") setState("error");
      });

    return () => controller.abort();
  }, [selection.degree]);

  // Catalog metadata supplies each recommendation university's geography.
  const universityGeo = useMemo(() => {
    const byName = new Map<string, GeoIdentity>();
    for (const university of catalog?.universities ?? []) {
      byName.set(university.name, {
        country: university.country,
        city: university.city,
        continent: university.continent,
      });
    }
    return byName;
  }, [catalog]);

  // The filter row only appears when the catalog records any geography.
  const geoAvailable =
    catalog !== null &&
    catalog.universities.some(university => university.city !== null || university.continent !== null);

  // Immediate client-side filter (FR-09/FR-10): the API rank order and the
  // per-university counts are untouched; only non-matching cards are hidden.
  const visibleResults = useMemo(() => {
    if (!results || isGeoSelectionEmpty(geo)) return results;
    return results.filter(recommendation => {
      const identity =
        universityGeo.get(recommendation.university) ?? {
          country: recommendation.country,
          city: null,
          continent: null,
        };
      return geoIdentityMatches(identity, geo);
    });
  }, [results, geo, universityGeo]);

  // True when loaded results exist but the active geography matches none.
  const geoFilteredEmpty = (results?.length ?? 0) > 0 && (visibleResults?.length ?? 0) === 0;

  // Atomic transition (FR-05); only a changed degree invalidates the results.
  function applyTransition(next: Selection) {
    const degreeChanged = next.degree !== selection.degree;
    setSelection(next);
    setTouched(true);
    if (degreeChanged) {
      setResults(null);
      setState(next.degree ? "loading" : "idle");
    }
  }

  // Direct degree selection re-derives its faculty (FR-03).
  function changeDegree(degree: Degree | null) {
    applyTransition(selectDegree(selection, degree, catalog?.faculties ?? []));
  }

  // A faculty change keeps a compatible degree and clears an incompatible one.
  function changeFaculty(faculty: Faculty | null) {
    applyTransition(selectFaculty(selection, faculty));
  }

  // Parent changes reconcile dependent selections in one transition (FR-07).
  function changeContinents(values: string[]) {
    if (!catalog) return;
    setGeo(current => reconcileGeography(catalog.universities, current, { continents: values }));
  }

  function changeCountries(values: string[]) {
    if (!catalog) return;
    setGeo(current => reconcileGeography(catalog.universities, current, { countries: values }));
  }

  function changeCities(values: string[]) {
    setGeo(current => ({ ...current, cities: values }));
  }

  return (
    <main>
      <RecommendHero />

      {/* Catalog loading replaces page content but keeps the hero visible. */}
      {state === "loading-catalog" ? (
        <LoadingState label="Loading degree programmes…" />
      ) : catalog && (
        <>
          {/* Without recorded faculties there is nothing to filter by. */}
          {catalog.faculties.length > 0 && (
            <div className={styles.facultyField}>
              <FacultyCombobox
                faculties={catalog.faculties}
                selected={selection.faculty}
                onSelect={changeFaculty}
              />
            </div>
          )}
          {/* The page owns selection state; the field only presents it. */}
          <RecommendDegreeField
            degrees={degreesForFaculty(catalog.degrees, selection.faculty)}
            selected={selection.degree}
            onSelect={changeDegree}
          />
          {/* Geographic filters apply to the loaded results immediately. */}
          {geoAvailable && (
            <GeographicFilters
              options={deriveGeoOptions(catalog.universities, geo)}
              selection={geo}
              onContinentsChange={changeContinents}
              onCountriesChange={changeCountries}
              onCitiesChange={changeCities}
            />
          )}
        </>
      )}
      {/* Result loading keeps the hero and degree selector available. */}
      {state === "loading" && (
        <LoadingState variant="results" label="Finding partner universities…" />
      )}
      {state === "error" && <p role="alert">{UNAVAILABLE_MESSAGE}</p>}
      {state === "idle" && !selection.degree && touched && (
        <p>Choose a degree to see results.</p>
      )}
      {state === "idle" && selection.degree && results && (
        geoFilteredEmpty ? (
          // Distinguish geography-matched-nothing from a degree with no results.
          <p role="status">No universities match the selected geography.</p>
        ) : (
          <UniversityCards
            degree={selection.degree.name}
            recommendations={visibleResults ?? results}
          />
        )
      )}
    </main>
  );
}
