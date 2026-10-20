"use client";

import { useId, useMemo, useRef, useState, type ReactNode } from "react";
import { Input } from "@/components/ui/input";

export type TypableDropdownProps<T> = {
  options: T[];
  value: T | null;
  onSelect: (value: T | null) => void;
  label: string;
  placeholder?: string;
  searchText: (option: T) => string;
  getOptionValue: (option: T) => string;
  renderOption: (option: T) => ReactNode;
  emptyMessage?: string;
};

export default function TypableDropdown<T>({
  options,
  value,
  onSelect,
  label,
  placeholder,
  searchText,
  getOptionValue,
  renderOption,
  emptyMessage = "No matching options.",
}: TypableDropdownProps<T>) {
  const id = useId().replace(/:/g, "");
  const inputId = `${id}-input`;
  const labelId = `${id}-label`;
  const listId = `${id}-list`;
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState<string | null>(null);
  const [filter, setFilter] = useState("");
  const [active, setActive] = useState(-1);
  const committed = useRef<T | null>(value);
  const filtered = useMemo(
    () =>
      options.filter(option =>
        searchText(option).toLowerCase().includes(filter.toLowerCase())
      ),
    [options, searchText, filter]
  );
  const displayed = input ?? (value ? getOptionValue(value) : "");

  function choose(option: T) {
    committed.current = option;
    onSelect(option);
    setInput(null);
    setFilter("");
    setActive(-1);
    setOpen(false);
  }

  function change(next: string) {
    setInput(next);
    setFilter(next);
    setActive(-1);
    setOpen(true);
    onSelect(null);
  }

  function close() {
    setOpen(false);
    setActive(-1);
  }

  function keyDown(event: React.KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Escape") {
      if (input !== null) {
        onSelect(committed.current);
      }
      setInput(null);
      setFilter("");
      close();
      return;
    }
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      setOpen(true);
      if (filtered.length) {
        setActive(current =>
          event.key === "ArrowDown"
            ? (current + 1) % filtered.length
            : current < 0
              ? filtered.length - 1
              : (current - 1 + filtered.length) % filtered.length
        );
      }
      return;
    }
    if (event.key === "Home" && open) {
      event.preventDefault();
      setActive(filtered.length ? 0 : -1);
      return;
    }
    if (event.key === "End" && open) {
      event.preventDefault();
      setActive(filtered.length - 1);
      return;
    }
    if (event.key === "Enter" && open) {
      event.preventDefault();
      if (filtered.length) {
        choose(filtered[active >= 0 ? active : 0]);
      }
    }
  }

  return (
    <div className="combo-wrap">
      <label id={labelId} htmlFor={inputId}>
        {label}
      </label>
      <Input
        id={inputId}
        role="combobox"
        aria-autocomplete="list"
        aria-expanded={open}
        aria-controls={listId}
        aria-activedescendant={open && active >= 0 ? `${id}-option-${active}` : undefined}
        aria-labelledby={labelId}
        value={displayed}
        placeholder={placeholder}
        autoComplete="off"
        onFocus={() => {
          committed.current = value;
          setInput(null);
          setFilter("");
          setActive(-1);
          setOpen(true);
        }}
        onClick={() => {
          if (input === null) setFilter("");
          setActive(-1);
          setOpen(true);
        }}
        onChange={event => change(event.target.value)}
        onKeyDown={keyDown}
        onBlur={() => {
          window.setTimeout(close, 100);
        }}
      />
      {open && (
        <div id={listId} role="listbox" aria-labelledby={labelId} className="combo-list">
          {filtered.length ? (
            filtered.map((option, index) => (
              <div
                key={`${index}-${getOptionValue(option)}`}
                id={`${id}-option-${index}`}
                role="option"
                aria-selected={index === active}
                className={index === active ? "active" : ""}
                onMouseDown={event => event.preventDefault()}
                onClick={() => choose(option)}
              >
                {renderOption(option)}
              </div>
            ))
          ) : (
            <p className="no-match">{emptyMessage}</p>
          )}
        </div>
      )}
    </div>
  );
}
