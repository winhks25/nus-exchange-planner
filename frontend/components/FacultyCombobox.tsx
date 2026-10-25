"use client";

import { useMemo } from "react";
import TypableDropdown from "@/components/ui/typable-dropdown";
import { sortFaculties } from "@/lib/faculty-selection";
import type { Faculty } from "@/lib/types";

type Props = {
  faculties: Faculty[];
  selected: Faculty | null;
  onSelect: (faculty: Faculty | null) => void;
  label?: string;
  placeholder?: string;
};

// Shared faculty picker; the page owns the selection state.
export default function FacultyCombobox({
  faculties,
  selected,
  onSelect,
  label = "Faculty",
  placeholder = "Search faculty",
}: Props) {
  // Reuse the contract order: English alphabetical name, then stable id.
  const options = useMemo(() => sortFaculties(faculties), [faculties]);

  return (
    <div className="faculty-field">
      <TypableDropdown
        options={options}
        value={selected}
        onSelect={onSelect}
        label={label}
        placeholder={placeholder}
        searchText={faculty => faculty.name}
        getOptionValue={faculty => faculty.name}
        renderOption={faculty => <strong>{faculty.name}</strong>}
        emptyMessage="No matching faculty."
      />
      {/* Clear keeps the degree and reopens every degree option (rule 4). */}
      {selected && (
        <button type="button" className="faculty-clear" onClick={() => onSelect(null)}>
          Clear
        </button>
      )}
    </div>
  );
}
