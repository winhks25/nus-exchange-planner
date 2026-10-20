import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "NUS Exchange Planner",
  description: "Explore exchange module mappings",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <header>
            <Link className="brand" href="/">NUS Exchange Planner</Link>
            <nav>
              <Link href="/">Recommend</Link>
              <Link href="/compare">Compare</Link>
            </nav>
          </header>
          {children}
        </div>
      </body>
    </html>
  );
}
