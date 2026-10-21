"use client";

import TypableDropdown from "@/components/ui/typable-dropdown";
import type { Degree } from "@/lib/types";

type Props = {
  degrees: Degree[];
  selected: Degree | null;
  onSelect: (degree: Degree | null) => void;
  label?: string;
  placeholder?: string;
};

// Shared defaults keep the Mappings page copy unchanged.
export default function DegreeCombobox({
  degrees,
  selected,
  onSelect,
  label = "Degree programme",
  placeholder = "Search degree programmes",
}: Props) {
  return (
    <TypableDropdown
      options={degrees}
      value={selected}
      onSelect={onSelect}
      label={label}
      placeholder={placeholder}
      searchText={degree => `${degree.name} ${degree.degree}`}
      getOptionValue={degree => degree.name}
      renderOption={degree => (
        <>
          <strong>{degree.name}</strong>
          <span>{degree.degree}</span>
        </>
      )}
      emptyMessage="Program not available. Check the degree list."
    />
  );
}
