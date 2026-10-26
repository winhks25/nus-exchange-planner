import type { Metadata } from "next";
import AppShell from "@/components/layout/AppShell";
import { MappingsSelectionProvider } from "@/components/mappings/MappingsSelectionProvider";
import "./globals.css";

export const metadata: Metadata = {
  title: "NUS Exchange Planner",
  description: "Explore exchange module mappings",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <MappingsSelectionProvider>
          <AppShell>{children}</AppShell>
        </MappingsSelectionProvider>
      </body>
    </html>
  );
}
