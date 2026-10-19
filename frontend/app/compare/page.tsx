"use client";
import { Suspense, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import DegreeCombobox from "@/components/DegreeCombobox";
import MappingRows from "@/components/MappingRows";
import CompareEmptyState from "@/components/CompareEmptyState";
import { getCatalog, getMappings } from "@/lib/api";
import type { Catalog, Degree, MappingResult, University } from "@/lib/types";

function CompareContent() {
  const router = useRouter(); const params = useSearchParams();
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [degree, setDegree] = useState<Degree | null>(null);
  const [university, setUniversity] = useState<University | null>(null);
  const [note, setNote] = useState("");
  const [result, setResult] = useState<MappingResult | null>(null);
  const [state, setState] = useState<"loading-catalog" | "idle" | "loading" | "error">("loading-catalog");
  const appliedUrl = useRef<string | null>(null);
  useEffect(() => { const controller = new AbortController(); getCatalog(controller.signal).then(data => { setCatalog(data); setState("idle"); }).catch(error => { if (error.name !== "AbortError") setState("error"); }); return () => controller.abort(); }, []);
  useEffect(() => {
    if (!catalog) return;
    const query = params.toString();
    if (appliedUrl.current === query) return;
    appliedUrl.current = query;
    const degreeValue = params.get("degree"), uniValue = params.get("uni");
    const validDegree = catalog.degrees.find(item => item.name === degreeValue) || null;
    const validUniversity = catalog.universities.find(item => item.name === uniValue) || null;
    // URL navigation is an external state change that updates both selectors together.
    setDegree(validDegree); setUniversity(validUniversity); setResult(null); setState(validDegree && validUniversity ? "loading" : "idle");
    setNote((degreeValue && !validDegree) || (uniValue && !validUniversity) ? "This link contains an unknown degree or partner university. Please choose a valid option." : "");
  }, [catalog, params]);
  useEffect(() => {
    if (!degree || !university) return;
    const controller = new AbortController();
    getMappings(degree.name, university.name, controller.signal).then(data => { setResult(data); setState("idle"); }).catch(error => { if (error.name !== "AbortError") setState("error"); });
    return () => controller.abort();
  }, [degree, university]);
  function update(nextDegree: Degree | null, nextUniversity: University | null) {
    setDegree(nextDegree); setUniversity(nextUniversity); setResult(null); setNote(""); setState(nextDegree && nextUniversity ? "loading" : "idle");
    const next = new URLSearchParams(); if (nextDegree) next.set("degree", nextDegree.name); if (nextUniversity) next.set("uni", nextUniversity.name);
    appliedUrl.current = next.toString();
    router.replace(`/compare${next.size ? `?${next.toString()}` : ""}`, { scroll: false });
  }
  return <main><div className="hero"><p className="eyebrow">SIDE BY SIDE</p><h1>Compare module mappings.</h1><p>Explore qualifying NUS and partner courses for one degree and university.</p></div>
    {state === "loading-catalog" ? <p role="status">Loading choices…</p> : catalog && <div className="selectors"><DegreeCombobox degrees={catalog.degrees} selected={degree} onSelect={value => update(value, university)}/><div><label htmlFor="university">Partner university</label><select id="university" value={university?.name || ""} onChange={event => update(degree, catalog.universities.find(item => item.name === event.target.value) || null)}><option value="">select a partner university</option>{[...catalog.universities].sort((a,b) => a.name.localeCompare(b.name)).map(item => <option key={item.name} value={item.name}>{item.name}</option>)}</select></div></div>}
    {note && <p role="status" className="note">{note}</p>}
    {state === "loading" && <p role="status">Loading mappings…</p>}
    {state === "error" && <p role="alert">The mapping service is unavailable. Please try again.</p>}
    {state === "idle" && result && <section><p className="result-count">{result.distinct_nus_module_count} distinct NUS modules · {result.mappings.length} mapping rows</p>{result.mappings.length ? <MappingRows mappings={result.mappings}/> : <CompareEmptyState/>}</section>}
  </main>;
}
export default function ComparePage() { return <Suspense fallback={<p>Loading choices…</p>}><CompareContent/></Suspense>; }
