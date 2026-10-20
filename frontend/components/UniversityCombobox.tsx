"use client";
import { useMemo } from "react";
import TypableDropdown from "@/components/ui/typable-dropdown";
import type { University } from "@/lib/types";

type Props = { universities: University[]; selected: University | null; onSelect: (university: University | null) => void; label?: string };

export default function UniversityCombobox({ universities, selected, onSelect, label = "Partner university" }: Props) {
  const options = useMemo(() => [...universities].sort((a, b) => a.name.localeCompare(b.name)), [universities]);
  return <TypableDropdown
    options={options}
    value={selected}
    onSelect={onSelect}
    label={label}
    placeholder="select a partner university"
    searchText={university => university.name}
    getOptionValue={university => university.name}
    renderOption={university => <><strong>{university.name}</strong><span>{university.country}</span></>}
    emptyMessage="Partner university not available."
  />;
}
