"use client";
import { useId, useMemo, useRef, useState } from "react";
import type { Degree } from "@/lib/types";

type Props = { degrees: Degree[]; selected: Degree | null; onSelect: (degree: Degree | null) => void; label?: string };
export default function DegreeCombobox({ degrees, selected, onSelect, label = "Degree programme" }: Props) {
  const id = useId().replace(/:/g, "");
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState<string | null>(null);
  const [filter, setFilter] = useState("");
  const [active, setActive] = useState(-1);
  const committed = useRef<Degree | null>(selected);
  const options = useMemo(() => degrees.filter(d => `${d.name} ${d.degree}`.toLowerCase().includes(filter.toLowerCase())), [degrees, filter]);
  const value = input ?? selected?.name ?? "";
  function choose(degree: Degree) { committed.current = degree; onSelect(degree); setInput(null); setFilter(""); setActive(-1); setOpen(false); }
  function change(value: string) { setInput(value); setFilter(value); setActive(-1); setOpen(true); onSelect(null); }
  function keyDown(event: React.KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Escape") { if (input !== null) onSelect(committed.current); setOpen(false); setInput(null); setFilter(""); setActive(-1); return; }
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault(); setOpen(true);
      if (options.length) setActive(current => event.key === "ArrowDown" ? (current + 1) % options.length : (current < 0 ? options.length - 1 : (current - 1 + options.length) % options.length));
    }
    if (event.key === "Home" && open) { event.preventDefault(); setActive(options.length ? 0 : -1); }
    if (event.key === "End" && open) { event.preventDefault(); setActive(options.length - 1); }
    if (event.key === "Enter" && open) { event.preventDefault(); if (options.length) choose(options[active >= 0 ? active : 0]); }
  }
  return <div className="combo-wrap"><label htmlFor={`${id}-input`}>{label}</label>
    <input id={`${id}-input`} role="combobox" aria-autocomplete="list" aria-expanded={open} aria-controls={`${id}-list`} aria-activedescendant={open && active >= 0 ? `${id}-option-${active}` : undefined}
      value={value} placeholder="Search degree programmes" autoComplete="off" onFocus={() => { committed.current = selected; setOpen(true); setFilter(""); setActive(-1); }} onClick={() => { setOpen(true); setFilter(""); setActive(-1); }} onChange={event => change(event.target.value)} onKeyDown={keyDown} onBlur={() => { window.setTimeout(() => setOpen(false), 100); }} />
    {open && <div id={`${id}-list`} role="listbox" className="combo-list">{options.length ? options.map((degree, index) => <div key={degree.name} id={`${id}-option-${index}`} role="option" aria-selected={index === active} className={index === active ? "active" : ""} onMouseDown={event => event.preventDefault()} onClick={() => choose(degree)}><strong>{degree.name}</strong><span>{degree.degree}</span></div>) : <p className="no-match">Program not available. Check the degree list.</p>}</div>}
  </div>;
}
