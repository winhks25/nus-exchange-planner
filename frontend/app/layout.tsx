import type { Metadata } from "next";
import Link from "next/link";
import AppShell from "@/components/layout/AppShell";
import "./globals.css";

export const metadata: Metadata = {
  title: "NUS Exchange Planner",
  description: "Explore exchange module mappings",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  const navigation = (
    <>
      <Link href="/">Recommend</Link>
      <Link href="/compare">Compare</Link>
    </>
  );

  return (
    <html lang="en">
      <body>
        <AppShell navigation={navigation}>{children}</AppShell>
      </body>
    </html>
  );
}
