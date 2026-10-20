"use client";

import { useEffect, useState } from "react";
import DegreeCombobox from "@/components/DegreeCombobox";
import UniversityCards from "@/components/UniversityCards";
import { getCatalog, getRecommendations } from "@/lib/api";
import type { Catalog, Degree, Recommendation } from "@/lib/types";

type PageState = "loading-catalog" | "idle" | "loading" | "error";

export default function RecommendPage() {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [selected, setSelected] = useState<Degree | null>(null);
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

  useEffect(() => {
    if (!selected) return;
    const controller = new AbortController();

    getRecommendations(selected.name, controller.signal)
      .then(data => {
        setResults(data.recommendations);
        setState("idle");
      })
      .catch(error => {
        if (error.name !== "AbortError") setState("error");
      });

    return () => controller.abort();
  }, [selected]);

  function select(degree: Degree | null) {
    setSelected(degree);
    setTouched(true);
    setResults(null);
    setState(degree ? "loading" : "idle");
  }

  return (
    <main>
      <div className="hero">
        <p className="eyebrow">NUS SCHOOL OF COMPUTING · EXCHANGE</p>
        <h1>Find where your modules can take you.</h1>
        <p>Choose a degree to rank partner universities by available module mappings.</p>
      </div>

      {state === "loading-catalog" ? (
        <p role="status">Loading degree programmes…</p>
      ) : catalog && (
        <DegreeCombobox degrees={catalog.degrees} selected={selected} onSelect={select} />
      )}
      {state === "loading" && <p role="status">Finding partner universities…</p>}
      {state === "error" && (
        <p role="alert">The mapping service is unavailable. Please try again.</p>
      )}
      {state === "idle" && !selected && touched && <p>Choose a degree to see results.</p>}
      {state === "idle" && selected && results && (
        <UniversityCards degree={selected.name} recommendations={results} />
      )}
    </main>
  );
}
