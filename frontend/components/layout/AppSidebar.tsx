"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import styles from "./app-shell.module.css";

// Clean line icons; decorative so the label text stays the accessible name.
function RecommendIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      strokeLinecap="round"
      aria-hidden="true"
    >
      <circle cx="11" cy="11" r="6.5" />
      <path d="m16 16 5 5" />
    </svg>
  );
}

function MappingsIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="m16 3 4 4-4 4" />
      <path d="M20 7H4" />
      <path d="m8 21-4-4 4-4" />
      <path d="M4 17h16" />
    </svg>
  );
}

function UniversitiesIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M4 21h16" />
      <path d="M6 21V10l6-5 6 5v11" />
      <path d="M10 21v-5h4v5" />
    </svg>
  );
}

const NAV_ITEMS = [
  { href: "/", label: "Recommend", Icon: RecommendIcon },
  { href: "/mappings", label: "Mappings", Icon: MappingsIcon },
  { href: "/universities", label: "Universities", Icon: UniversitiesIcon },
];

export default function AppSidebar() {
  // The current path is the single source of the active link state.
  const pathname = usePathname();

  return (
    <nav aria-label="Primary" className={styles.sideNav}>
      {NAV_ITEMS.map(({ href, label, Icon }) => (
        <Link
          key={href}
          href={href}
          className={styles.navLink}
          aria-current={pathname === href ? "page" : undefined}
        >
          <Icon />
          <span>{label}</span>
        </Link>
      ))}
    </nav>
  );
}
