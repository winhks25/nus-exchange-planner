"use client";

import { Suspense, useEffect, useEffectEvent, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import MappingsEmptyState from "@/components/MappingsEmptyState";
import DegreeCombobox from "@/components/DegreeCombobox";
import FacultyCombobox from "@/components/FacultyCombobox";
import LoadingState from "@/components/loading/LoadingState";
import MappingRows from "@/components/MappingRows";
import UniversityCombobox from "@/components/UniversityCombobox";
import { useMappingsSelection } from "@/components/mappings/MappingsSelectionProvider";
import { getCatalog, getMappings, UNAVAILABLE_MESSAGE } from "@/lib/api";
import {
  degreeBelongsToFaculty,
  degreesForFaculty,
  facultyForDegree,
  selectDegree,
  selectFaculty,
} from "@/lib/faculty-selection";
import { mergeMappingsParams } from "@/lib/mappings-navigation";
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
  const { selection: savedSelection, setSelection: setSavedSelection } = useMappingsSelection();
  const readSavedSelection = useEffectEvent(() => savedSelection);

  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [degree, setDegree] = useState<Degree | null>(null);
  const [faculty, setFaculty] = useState<Faculty | null>(null);
  const [university, setUniversity] = useState<University | null>(null);
  const [note, setNote] = useState("");
  const [result, setResult] = useState<MappingResult | null>(null);
  const [state, setState] = useState<PageState>("loading-catalog");
  const appliedUrl = useRef<string | null>(null);

  // Fetch the full catalog on initial mount with cancellation.
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

  // Hydrate selections by merging URL search parameters with remembered selections.
  useEffect(() => {
    if (!catalog) return;
    const query = params.toString();
    if (appliedUrl.current === query) return;
    appliedUrl.current = query;

    // Merge URL query with remembered Mappings selections (US5).
    // Remembered state is a fallback when a URL changes, not a trigger to
    // rehydrate the old URL while a selector's router update is pending.
    const merged = mergeMappingsParams(params, readSavedSelection());

    // Lookup matching objects in the loaded catalog.
    const validDegree = merged.degreeName
      ? catalog.degrees.find(item => item.name === merged.degreeName) || null
      : null;
    const validFaculty = merged.facultyName
      ? catalog.faculties.find(item => item.name === merged.facultyName) || null
      : null;
    const validUniversity = merged.universityName
      ? catalog.universities.find(item => item.name === merged.universityName) || null
      : null;

    // Preserve an explicitly selected compatible faculty (FR-04).
    // Derive a faculty only when degree has memberships and faculty was not explicitly set or cleared.
    let nextFaculty = validFaculty;
    if (validDegree && nextFaculty && !degreeBelongsToFaculty(validDegree, nextFaculty)) {
      nextFaculty = null;
    } else if (validDegree && !nextFaculty && !merged.cleared.faculty && !merged.facultyName) {
      nextFaculty = facultyForDegree(validDegree, catalog.faculties);
    }

    // Apply selections together to avoid partial renders.
    setDegree(validDegree);
    setFaculty(nextFaculty);
    setUniversity(validUniversity);
    setSavedSelection({
      degree: validDegree,
      faculty: nextFaculty,
      university: validUniversity,
    });
    setResult(null);
    setState(validDegree && validUniversity ? "loading" : "idle");

    // Report stale or unknown selections without silently choosing another degree.
    const unknownSelection =
      (Boolean(merged.degreeName) && !validDegree) ||
      (Boolean(merged.universityName) && !validUniversity);
    setNote(
      unknownSelection
        ? "This link contains an unknown degree or partner university. Please choose a valid option."
        : Boolean(merged.facultyName) && !validFaculty
          ? "This link contains an unknown faculty. Please choose a valid option."
          : ""
    );

    // Sync URL if merged parameters expanded beyond the initial query string.
    const hasUnknownParams =
      unknownSelection || (Boolean(merged.facultyName) && !validFaculty);
    if (!hasUnknownParams) {
      const next = new URLSearchParams();
      if (nextFaculty) next.set("faculty", nextFaculty.name);
      else if (merged.cleared.faculty) next.set("faculty", "");
      if (validDegree) next.set("degree", validDegree.name);
      else if (merged.cleared.degree) next.set("degree", "");
      if (validUniversity) next.set("uni", validUniversity.name);
      else if (merged.cleared.uni) next.set("uni", "");
      for (const [key, value] of merged.otherParams.entries()) {
        next.append(key, value);
      }
      const nextQuery = next.toString();
      if (nextQuery !== query && (merged.degreeName || merged.facultyName || merged.universityName)) {
        appliedUrl.current = nextQuery;
        router.replace(`/mappings${nextQuery ? `?${nextQuery}` : ""}`, { scroll: false });
      }
    }
  }, [
    catalog,
    params,
    router,
    setSavedSelection,
  ]);

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
    setSavedSelection({
      degree: nextDegree,
      faculty: nextFaculty,
      university: nextUniversity,
    });
    setNote("");

    // Only the effective pair invalidates the loaded mappings.
    if (requestChanged) {
      setResult(null);
      setState(nextDegree && nextUniversity ? "loading" : "idle");
    }

    const next = new URLSearchParams(params.toString());
    next.set("faculty", nextFaculty?.name ?? "");
    next.set("degree", nextDegree?.name ?? "");
    next.set("uni", nextUniversity?.name ?? "");
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

  // Documented prompt when a partner university is chosen without a degree (FR-20).
  const noDegreePrompt =
    !note && university && !degree
      ? "Please select a degree programme to view course mappings for this partner university."
      : "";
  const displayNote = note || noDegreePrompt;

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
      {displayNote && <p role="status" className="note">{displayNote}</p>}
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
