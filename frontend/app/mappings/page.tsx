"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import MappingsEmptyState from "@/components/MappingsEmptyState";
import DegreeCombobox from "@/components/DegreeCombobox";
import FacultyCombobox from "@/components/FacultyCombobox";
import LoadingState from "@/components/loading/LoadingState";
import MappingRows from "@/components/MappingRows";
import UniversityCombobox from "@/components/UniversityCombobox";
import { getCatalog, getMappings, UNAVAILABLE_MESSAGE } from "@/lib/api";
import {
  degreeBelongsToFaculty,
  degreesForFaculty,
  selectDegree,
  selectFaculty,
} from "@/lib/faculty-selection";
import type {
  Catalog,
  Degree,
  Faculty,
  MappingResult,
  PageState,
  University,
} from "@/lib/types";

function MappingsContent() {
  const router = useRouter();
  const params = useSearchParams();
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [degree, setDegree] = useState<Degree | null>(null);
  const [faculty, setFaculty] = useState<Faculty | null>(null);
  const [university, setUniversity] = useState<University | null>(null);
  const [note, setNote] = useState("");
  const [result, setResult] = useState<MappingResult | null>(null);
  const [state, setState] = useState<PageState>("loading-catalog");
  const appliedUrl = useRef<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    getCatalog(controller.signal)
      .then(data => {
        // URL synchronization decides whether to stay loading for mappings.
        setCatalog(data);
      })
      .catch(error => {
        if (error.name !== "AbortError") setState("error");
      });

    return () => controller.abort();
  }, []);

  useEffect(() => {
    if (!catalog) return;
    const query = params.toString();
    if (appliedUrl.current === query) return;
    appliedUrl.current = query;

    const degreeValue = params.get("degree");
    const facultyValue = params.get("faculty");
    const universityValue = params.get("uni");
    const validDegree = catalog.degrees.find(item => item.name === degreeValue) || null;
    const validFaculty = catalog.faculties.find(item => item.name === facultyValue) || null;
    const validUniversity =
      catalog.universities.find(item => item.name === universityValue) || null;

    // Inconsistent deep links keep the degree and drop the faculty so the
    // mappings for the linked degree can still load.
    let nextFaculty = validFaculty;
    if (validDegree && nextFaculty && !degreeBelongsToFaculty(validDegree, nextFaculty)) {
      nextFaculty = null;
    }

    // URL navigation updates all selectors together.
    setDegree(validDegree);
    setFaculty(nextFaculty);
    setUniversity(validUniversity);
    setResult(null);
    setState(validDegree && validUniversity ? "loading" : "idle");
    setNote(
      (degreeValue && !validDegree) ||
      (facultyValue && !validFaculty) ||
      (universityValue && !validUniversity)
        ? "This link contains an unknown degree, faculty or partner university. Please choose a valid option."
        : ""
    );
  }, [catalog, params]);

  // Mappings track the effective degree/university pair; a compatible faculty
  // change leaves both references untouched, so nothing refetches.
  useEffect(() => {
    if (!degree || !university) return;
    const controller = new AbortController();

    getMappings(degree.name, university.name, controller.signal)
      .then(data => {
        // Ignore responses superseded by a newer selection pair.
        if (controller.signal.aborted) return;
        setResult(data);
        setState("idle");
      })
      .catch(error => {
        if (error.name !== "AbortError") setState("error");
      });

    return () => controller.abort();
  }, [degree, university]);

  // All selector writes go through one update so the URL, state and the
  // request-invalidating pair stay consistent.
  function update(
    nextDegree: Degree | null,
    nextFaculty: Faculty | null,
    nextUniversity: University | null
  ) {
    const requestChanged = nextDegree !== degree || nextUniversity !== university;

    setDegree(nextDegree);
    setFaculty(nextFaculty);
    setUniversity(nextUniversity);
    setNote("");
    // Only the effective pair invalidates the loaded mappings.
    if (requestChanged) {
      setResult(null);
      setState(nextDegree && nextUniversity ? "loading" : "idle");
    }

    const next = new URLSearchParams();
    if (nextFaculty) next.set("faculty", nextFaculty.name);
    if (nextDegree) next.set("degree", nextDegree.name);
    if (nextUniversity) next.set("uni", nextUniversity.name);
    appliedUrl.current = next.toString();
    router.replace(`/mappings${next.size ? `?${next.toString()}` : ""}`, { scroll: false });
  }

  // A faculty change reconciles the degree (FR-04) and keeps the university.
  function changeFaculty(faculty: Faculty | null) {
    const next = selectFaculty({ degree, faculty }, faculty);
    update(next.degree, next.faculty, university);
  }

  // A direct degree selection re-derives the faculty (FR-03) and keeps the university.
  function changeDegree(degreeValue: Degree | null) {
    const next = selectDegree({ degree, faculty }, degreeValue, catalog?.faculties ?? []);
    update(next.degree, next.faculty, university);
  }

  return (
    <main>
      <div className="hero">
        <h1>Module mappings.</h1>
        <p>Explore qualifying NUS and partner course mappings for your degree and your preferred university.</p>
      </div>

      {/* Catalog loading replaces page content until the selectors are ready. */}
      {state === "loading-catalog" ? (
        <LoadingState label="Loading choices…" />
      ) : catalog && (
        <div className="selectors">
          {/* Without recorded faculties there is nothing to filter by. */}
          {catalog.faculties.length > 0 && (
            <FacultyCombobox
              faculties={catalog.faculties}
              selected={faculty}
              onSelect={changeFaculty}
            />
          )}
          <DegreeCombobox
            degrees={degreesForFaculty(catalog.degrees, faculty)}
            selected={degree}
            onSelect={changeDegree}
          />
          <UniversityCombobox
            universities={catalog.universities}
            selected={university}
            onSelect={value => update(degree, faculty, value)}
          />
        </div>
      )}
      {note && <p role="status" className="note">{note}</p>}
      {/* Result loading keeps the hero and selectors available. */}
      {state === "loading" && (
        <LoadingState variant="results" label="Loading mappings…" />
      )}
      {state === "error" && <p role="alert">{UNAVAILABLE_MESSAGE}</p>}
      {state === "idle" && result && (
        <section>
          <div className="result-summary" role="group" aria-label="Mapping counts">
            <p className="result-count">
              <strong>{result.partner_module_count}</strong> mappable partner modules ·{" "}
              <strong>{result.distinct_nus_module_count}</strong> distinct NUS modules ·{" "}
              <strong>{result.mappings.length}</strong> mappings
            </p>
            <p className="result-note">
              One NUS module can have several partner mappings, and one partner module may appear
              in more than one mapping row.
            </p>
          </div>
          {result.mappings.length ? (
            <MappingRows mappings={result.mappings} />
          ) : (
            <MappingsEmptyState />
          )}
        </section>
      )}
    </main>
  );
}

export default function MappingsPage() {
  // The Suspense fallback owns a single main landmark while the page suspends.
  return (
    <Suspense
      fallback={
        <main>
          <LoadingState label="Loading choices…" />
        </main>
      }
    >
      <MappingsContent />
    </Suspense>
  );
}
