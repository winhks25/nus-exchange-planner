import LoadingState from "@/components/loading/LoadingState";

// Root route fallback renders inside AppShell so the header and sidebar stay usable.
export default function Loading() {
  return (
    <main>
      <LoadingState />
    </main>
  );
}
