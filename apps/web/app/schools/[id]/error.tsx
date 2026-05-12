"use client";

import Link from "next/link";

import { Button } from "@/components/ui/button";

export default function Error({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-3xl items-center justify-center px-5 py-12">
      <div className="rounded-lg border border-border bg-white p-8 shadow-soft">
        <h1 className="text-2xl font-semibold tracking-normal text-foreground">
          School profile failed to load
        </h1>
        <p className="mt-3 text-sm leading-6 text-muted-foreground">
          The profile page could not render. Keep the API server running and try again.
        </p>
        <div className="mt-6 flex gap-3">
          <Button type="button" onClick={reset}>Try again</Button>
          <Button asChild variant="secondary">
            <Link href="/search">Back to search</Link>
          </Button>
        </div>
      </div>
    </main>
  );
}
