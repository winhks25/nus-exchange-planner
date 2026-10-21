import DegreeCombobox from "@/components/DegreeCombobox";
import type { Degree } from "@/lib/types";
import styles from "./recommend.module.css";

type Props = {
  degrees: Degree[];
  selected: Degree | null;
  onSelect: (degree: Degree | null) => void;
};

// Presentation frame; the page keeps selection and request state.
export default function RecommendDegreeField({ degrees, selected, onSelect }: Props) {
  return (
    <div className={styles.degreeField}>
      <DegreeCombobox
        degrees={degrees}
        selected={selected}
        onSelect={onSelect}
        label="Degree Programme"
        placeholder="Choose your degree programme"
      />
      <span>Find out which university offers the best module mapping options for you.</span>
    </div>
  );
}
