import Link from "next/link";

export default function MappingsEmptyState() {
  return (
    <div className="empty-state">
      <p>No qualifying mappings for this degree and partner university.</p>
      <Link href="/">Back to Recommend</Link>
    </div>
  );
}
