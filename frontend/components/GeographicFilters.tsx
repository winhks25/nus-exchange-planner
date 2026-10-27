"use client";

import { useEffect, useId, useRef, useState } from "react";
import type { GeoOptions, GeoSelection } from "@/lib/geography";

type Option = { value: string; label: string };

type GeoMultiSelectProps = {
  label: string;
  placeholder: string;
  options: Option[];
  selected: string[];
  onChange: (values: string[]) => void;
  open: boolean;
  setOpen: (open: boolean) => void;
};

// One dependent multi-select: a toggle button, the visible selected values,
// and a checkbox panel. Changes apply immediately (FR-09).
function GeoMultiSelect({ label, placeholder, options, selected, onChange, open, setOpen }: GeoMultiSelectProps) {
  const id = useId().replace(/:/g, "");
  const labelId = `${id}-label`;
  const panelId = `${id}-panel`;
  const toggleRef = useRef<HTMLButtonElement>(null);

  function toggle(value: string) {
    onChange(
      selected.includes(value) ? selected.filter(item => item !== value) : [...selected, value]
    );
  }

  return (
    <div className="geo-filter">
      <span id={labelId} className="label-text">
        {label}
      </span>
      <button
        ref={toggleRef}
        type="button"
        className="geo-toggle"
        aria-labelledby={labelId}
        aria-expanded={open}
        aria-controls={panelId}
        onClick={() => setOpen(!open)}
      >
        {selected.length === 0 ? (
          <span className="geo-placeholder">{placeholder}</span>
        ) : (
          `${selected.length} selected`
        )}
      </button>

      {/* Visible selected values with a per-category clear action. */}
      {selected.length > 0 && (
        <div className="geo-chips" aria-label={`${label} selected values`}>
          {selected.map(value => (
            <span key={value} className="geo-chip">
              {options.find(option => option.value === value)?.label ?? value}
            </span>
          ))}
          <button type="button" className="geo-clear" onClick={() => onChange([])}>
            Clear
          </button>
        </div>
      )}

      {open && (
        <div
          id={panelId}
          className="geo-panel"
          role="group"
          aria-label={`Select ${label.toLowerCase()}s`}
          onKeyDown={event => {
            // Escape closes the panel and returns focus to the toggle.
            if (event.key === "Escape") {
              setOpen(false);
              toggleRef.current?.focus();
            }
          }}
        >
          {options.length ? (
            options.map(option => (
              <label key={option.value} className="geo-option">
                <input
                  type="checkbox"
                  checked={selected.includes(option.value)}
                  onChange={() => toggle(option.value)}
                />
                {option.label}
              </label>
            ))
          ) : (
            <p className="no-match">No options.</p>
          )}
        </div>
      )}
    </div>
  );
}

type Props = {
  options: GeoOptions;
  selection: GeoSelection;
  onContinentsChange: (values: string[]) => void;
  onCountriesChange: (values: string[]) => void;
  onCitiesChange: (values: string[]) => void;
};

// The three dependent multi-selects (FR-06/FR-07); the page owns the
// selection state and applies every change immediately.
export default function GeographicFilters({
  options,
  selection,
  onContinentsChange,
  onCountriesChange,
  onCitiesChange,
}: Props) {
  const [openCategory, setOpenCategory] = useState<string | null>(null);
  const root = useRef<HTMLDivElement>(null);
  useEffect(() => {
    function closeOutside(event: PointerEvent) {
      if (event.target instanceof Node && !root.current?.contains(event.target)) {
        setOpenCategory(null);
      }
    }
    document.addEventListener("pointerdown", closeOutside);
    return () => document.removeEventListener("pointerdown", closeOutside);
  }, []);
  return (
    <div ref={root} className="geo-filters" role="group" aria-label="Geographic filters">
      <GeoMultiSelect
        open={openCategory === "continent"}
        setOpen={open => setOpenCategory(open ? "continent" : null)}
        label="Continent"
        placeholder="Any continent"
        options={options.continents.map(value => ({ value, label: value }))}
        selected={selection.continents}
        onChange={onContinentsChange}
      />
      <GeoMultiSelect
        open={openCategory === "country"}
        setOpen={open => setOpenCategory(open ? "country" : null)}
        label="Country"
        placeholder="Any country"
        options={options.countries.map(value => ({ value, label: value }))}
        selected={selection.countries}
        onChange={onCountriesChange}
      />
      <GeoMultiSelect
        open={openCategory === "city"}
        setOpen={open => setOpenCategory(open ? "city" : null)}
        label="City"
        placeholder="Any city"
        options={options.cities.map(city => ({ value: city.key, label: city.label }))}
        selected={selection.cities}
        onChange={onCitiesChange}
      />
    </div>
  );
}
