"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { Catalog, Degree, Faculty, University } from "@/lib/types";
import { degreeBelongsToFaculty } from "@/lib/faculty-selection";

// Persistent selections for the Mappings route.
export type MappingsSelectionState = {
  faculty: Faculty | null;
  degree: Degree | null;
  university: University | null;
};

export const EMPTY_MAPPINGS_SELECTION: MappingsSelectionState = {
  faculty: null,
  degree: null,
  university: null,
};

// Reconciles remembered selections against a freshly loaded catalog.
// Drops unknown options and resolves incompatible faculty-degree pairings.
export function reconcileMappingsSelection(
  selection: MappingsSelectionState,
  catalog: Catalog
): MappingsSelectionState {
  // Match remembered items against catalog items by unique name.
  const matchedDegree = selection.degree
    ? catalog.degrees.find(d => d.name === selection.degree?.name) ?? null
    : null;

  const matchedFaculty = selection.faculty
    ? catalog.faculties.find(f => f.name === selection.faculty?.name) ?? null
    : null;

  const matchedUniversity = selection.university
    ? catalog.universities.find(u => u.name === selection.university?.name) ?? null
    : null;

  // Reconcile faculty and degree compatibility (FR-04).
  let reconciledFaculty = matchedFaculty;
  if (matchedDegree && reconciledFaculty && !degreeBelongsToFaculty(matchedDegree, reconciledFaculty)) {
    reconciledFaculty = null;
  }

  return {
    degree: matchedDegree,
    faculty: reconciledFaculty,
    university: matchedUniversity,
  };
}

export type MappingsSelectionContextValue = {
  selection: MappingsSelectionState;
  setSelection: (
    updater:
      | Partial<MappingsSelectionState>
      | ((prev: MappingsSelectionState) => MappingsSelectionState)
  ) => void;
  clearSelection: () => void;
  reconcile: (catalog: Catalog) => void;
};

const MappingsSelectionContext = createContext<MappingsSelectionContextValue | null>(null);

// Root provider to preserve Mappings selections across route unmounts.
export function MappingsSelectionProvider({ children }: { children: ReactNode }) {
  // Remember selections across route unmounts in root layout state.
  const [selection, setRawSelection] = useState<MappingsSelectionState>(EMPTY_MAPPINGS_SELECTION);

  // Update selection partially or with a state updater function.
  const setSelection = useCallback(
    (
      updater:
        | Partial<MappingsSelectionState>
        | ((prev: MappingsSelectionState) => MappingsSelectionState)
    ) => {
      setRawSelection(prev => {
        if (typeof updater === "function") {
          return updater(prev);
        }
        return { ...prev, ...updater };
      });
    },
    []
  );

  // Reset all remembered selections to empty.
  const clearSelection = useCallback(() => {
    setRawSelection(EMPTY_MAPPINGS_SELECTION);
  }, []);

  // Reconcile current selection against a loaded catalog.
  const reconcile = useCallback((catalog: Catalog) => {
    setRawSelection(current => reconcileMappingsSelection(current, catalog));
  }, []);

  const value = useMemo(
    () => ({
      selection,
      setSelection,
      clearSelection,
      reconcile,
    }),
    [selection, setSelection, clearSelection, reconcile]
  );

  return (
    <MappingsSelectionContext.Provider value={value}>
      {children}
    </MappingsSelectionContext.Provider>
  );
}

// Hook for accessing persistent Mappings selections.
export function useMappingsSelection(): MappingsSelectionContextValue {
  const context = useContext(MappingsSelectionContext);
  if (!context) {
    throw new Error("useMappingsSelection must be used within a MappingsSelectionProvider");
  }
  return context;
}
