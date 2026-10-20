"use client";
import TypeableCombobox from "@/components/TypeableCombobox";
import type { Degree } from "@/lib/types";

type Props = { degrees: Degree[]; selected: Degree | null; onSelect: (degree: Degree | null) => void; label?: string };

export default function DegreeCombobox({ degrees, selected, onSelect, label = "Degree programme" }: Props) {
  return <TypeableCombobox
    options={degrees}
    value={selected}
    onSelect={onSelect}
    label={label}
    placeholder="Search degree programmes"
    searchText={degree => `${degree.name} ${degree.degree}`}
    getOptionValue={degree => degree.name}
    renderOption={degree => <><strong>{degree.name}</strong><span>{degree.degree}</span></>}
    emptyMessage="Program not available. Check the degree list."
  />;
}
