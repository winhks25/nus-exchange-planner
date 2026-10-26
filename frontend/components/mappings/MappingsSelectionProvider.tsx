"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useSyncExternalStore,
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

const STORAGE_KEY = "mappings_selection_state";

// In-memory store persistent across route unmounts.
let inMemorySelection: MappingsSelectionState = EMPTY_MAPPINGS_SELECTION;
let isInitialized = false;
const listeners = new Set<() => void>();

function notify() {
  for (const listener of listeners) {
    listener();
  }
}

function subscribe(callback: () => void) {
  listeners.add(callback);
  return () => {
    listeners.delete(callback);
  };
}

function initFromStorage() {
  if (isInitialized || typeof window === "undefined") return;
  isInitialized = true;
  try {
    const stored = window.sessionStorage.getItem(STORAGE_KEY);
    if (stored) {
      inMemorySelection = JSON.parse(stored);
    }
  } catch {
    // Ignore storage read errors.
  }
}

function getSnapshot(): MappingsSelectionState {
  initFromStorage();
  return inMemorySelection;
}

function getServerSnapshot(): MappingsSelectionState {
  return EMPTY_MAPPINGS_SELECTION;
}

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
  // Synchronize selection using external store semantics to support concurrent mode and SSR.
  const selection = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  // Update selection partially or with a state updater function.
  const setSelection = useCallback(
    (
      updater:
        | Partial<MappingsSelectionState>
        | ((prev: MappingsSelectionState) => MappingsSelectionState)
    ) => {
      const next = typeof updater === "function" ? updater(inMemorySelection) : { ...inMemorySelection, ...updater };
      inMemorySelection = next;
      try {
        if (typeof window !== "undefined") {
          window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(next));
        }
      } catch {
        // Ignore storage write errors.
      }
      notify();
    },
    []
  );

  // Reset all remembered selections to empty.
  const clearSelection = useCallback(() => {
    inMemorySelection = EMPTY_MAPPINGS_SELECTION;
    try {
      if (typeof window !== "undefined") {
        window.sessionStorage.removeItem(STORAGE_KEY);
      }
    } catch {
      // Ignore storage write errors.
    }
    notify();
  }, []);

  // Reconcile current selection against a loaded catalog.
  const reconcile = useCallback((catalog: Catalog) => {
    const reconciled = reconcileMappingsSelection(inMemorySelection, catalog);
    inMemorySelection = reconciled;
    try {
      if (typeof window !== "undefined") {
        window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(reconciled));
      }
    } catch {
      // Ignore storage write errors.
    }
    notify();
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
