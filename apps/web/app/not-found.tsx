import Link from "next/link";

import { EmptyState } from "@/components/ui/empty-state";

export default function NotFound() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-3xl items-center justify-center px-5 py-12">
      <EmptyState
        title="Page not found"
        description="That page does not exist. Start from school search instead."
        action={<Link href="/search">Explore schools</Link>}
        headingLevel="h1"
      />
    </main>
  );
}
