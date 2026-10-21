"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import MappingsEmptyState from "@/components/MappingsEmptyState";
import DegreeCombobox from "@/components/DegreeCombobox";
import LoadingState from "@/components/loading/LoadingState";
import MappingRows from "@/components/MappingRows";
import UniversityCombobox from "@/components/UniversityCombobox";
import { getCatalog, getMappings, UNAVAILABLE_MESSAGE } from "@/lib/api";
import type { Catalog, Degree, MappingResult, PageState, University } from "@/lib/types";

function MappingsContent() {
  const router = useRouter();
  const params = useSearchParams();
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [degree, setDegree] = useState<Degree | null>(null);
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
    const universityValue = params.get("uni");
    const validDegree = catalog.degrees.find(item => item.name === degreeValue) || null;
    const validUniversity =
      catalog.universities.find(item => item.name === universityValue) || null;

    // URL navigation updates both selectors together.
    setDegree(validDegree);
    setUniversity(validUniversity);
    setResult(null);
    setState(validDegree && validUniversity ? "loading" : "idle");
    setNote(
      (degreeValue && !validDegree) || (universityValue && !validUniversity)
        ? "This link contains an unknown degree or partner university. Please choose a valid option."
        : ""
    );
  }, [catalog, params]);

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

  function update(nextDegree: Degree | null, nextUniversity: University | null) {
    setDegree(nextDegree);
    setUniversity(nextUniversity);
    setResult(null);
    setNote("");
    setState(nextDegree && nextUniversity ? "loading" : "idle");

    const next = new URLSearchParams();
    if (nextDegree) next.set("degree", nextDegree.name);
    if (nextUniversity) next.set("uni", nextUniversity.name);
    appliedUrl.current = next.toString();
    router.replace(`/mappings${next.size ? `?${next.toString()}` : ""}`, { scroll: false });
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
          <DegreeCombobox
            degrees={catalog.degrees}
            selected={degree}
            onSelect={value => update(value, university)}
          />
          <UniversityCombobox
            universities={catalog.universities}
            selected={university}
            onSelect={value => update(degree, value)}
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
