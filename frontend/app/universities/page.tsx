"use client";

import { useEffect, useMemo, useState } from "react";
import FacultyCombobox from "@/components/FacultyCombobox";
import GeographicFilters from "@/components/GeographicFilters";
import LoadingState from "@/components/loading/LoadingState";
import UniversityDirectoryCard from "@/components/universities/UniversityDirectoryCard";
import { getCatalog, UNAVAILABLE_MESSAGE } from "@/lib/api";
import {
  EMPTY_GEO_SELECTION,
  deriveGeoOptions,
  isGeoSelectionEmpty,
  reconcileGeography,
  type GeoSelection,
} from "@/lib/geography";
import { filterUniversities } from "@/lib/university-filters";
import type { Catalog, Faculty, PageState } from "@/lib/types";
import styles from "@/components/universities/universities.module.css";

export default function UniversitiesPage() {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [faculty, setFaculty] = useState<Faculty | null>(null);
  const [geo, setGeo] = useState<GeoSelection>(EMPTY_GEO_SELECTION);
  const [state, setState] = useState<PageState>("loading-catalog");
  const [reloadKey, setReloadKey] = useState(0);

  // Catalog fetch with cancellation; retry re-runs it by bumping the key.
  useEffect(() => {
    const controller = new AbortController();

    getCatalog(controller.signal)
      .then(data => {
        // Ignore responses superseded by a newer load.
        if (controller.signal.aborted) return;
        setCatalog(data);
        setState("idle");
      })
      .catch(error => {
        if (error.name !== "AbortError") setState("error");
      });

    return () => controller.abort();
  }, [reloadKey]);

  function retry() {
    // The reset happens in the handler, not the effect, so the retry is a
    // plain state transition followed by one re-fetch.
    setCatalog(null);
    setState("loading-catalog");
    setReloadKey(key => key + 1);
  }

  // The directory is a client-side view of the complete catalog; no filters
  // return every partner, including partners without availability links.
  const visibleUniversities = useMemo(
    () => (catalog ? filterUniversities(catalog.universities, faculty, geo) : []),
    [catalog, faculty, geo]
  );

  // The geographic row only appears when the catalog records any geography.
  const geoAvailable =
    catalog !== null &&
    catalog.universities.some(university => university.city !== null || university.continent !== null);

  const filtersActive = faculty !== null || !isGeoSelectionEmpty(geo);
  const filteredEmpty = filtersActive && visibleUniversities.length === 0;

  // Clearing the faculty restores partners with no recorded availability.
  function changeFaculty(value: Faculty | null) {
    setFaculty(value);
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

  function resetFilters() {
    setFaculty(null);
    setGeo(EMPTY_GEO_SELECTION);
  }

  return (
    <main>
      <div className="hero">
        <h1>Partner universities.</h1>
        <p>Browse every exchange partner, optionally restricted by faculty and location.</p>
      </div>

      {state === "loading-catalog" && (
        <LoadingState label="Loading partner universities…" />
      )}

      {state === "error" && (
        <div className={styles.errorState} role="alert">
          <p>{UNAVAILABLE_MESSAGE}</p>
          <button type="button" className={styles.retry} onClick={retry}>
            Retry
          </button>
        </div>
      )}

      {state === "idle" && catalog && (
        <>
          <div className={styles.controls}>
            {/* Without recorded faculties there is nothing to filter by. */}
            {catalog.faculties.length > 0 && (
              <FacultyCombobox
                faculties={catalog.faculties}
                selected={faculty}
                onSelect={changeFaculty}
              />
            )}
            {geoAvailable && (
              <GeographicFilters
                options={deriveGeoOptions(catalog.universities, geo)}
                selection={geo}
                onContinentsChange={changeContinents}
                onCountriesChange={changeCountries}
                onCitiesChange={changeCities}
              />
            )}
          </div>

          {catalog.universities.length === 0 ? (
            <p className={styles.empty}>No partner universities are recorded yet.</p>
          ) : filteredEmpty ? (
            <div className={styles.emptyState}>
              <p role="status">No universities match the selected filters.</p>
              <button type="button" className={styles.retry} onClick={resetFilters}>
                Reset filters
              </button>
            </div>
          ) : (
            <section aria-label="Partner universities" className={styles.grid}>
              {visibleUniversities.map(university => (
                <UniversityDirectoryCard
                  key={university.name}
                  university={university}
                />
              ))}
            </section>
          )}
        </>
      )}
    </main>
  );
}
