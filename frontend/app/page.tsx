"use client";

import { useEffect, useState } from "react";
import RecommendDegreeField from "@/components/recommend/RecommendDegreeField";
import RecommendHero from "@/components/recommend/RecommendHero";
import FacultyCombobox from "@/components/FacultyCombobox";
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
import type { Catalog, Degree, Faculty, PageState, Recommendation } from "@/lib/types";
import styles from "@/components/recommend/recommend.module.css";

export default function RecommendPage() {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [selection, setSelection] = useState<Selection>(EMPTY_SELECTION);
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
        <UniversityCards degree={selection.degree.name} recommendations={results} />
      )}
    </main>
  );
}
