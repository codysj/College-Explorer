import Link from "next/link";

import { EmptyState } from "@/components/ui/empty-state";

export default function NotFound() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-3xl items-center justify-center px-5 py-12">
      <EmptyState
        title="Page not found"
        description="This route is not part of the V1 frontend foundation."
        action={<Link href="/">Return home</Link>}
      />
    </main>
  );
}
