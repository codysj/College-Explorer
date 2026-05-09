"use client";

import { AlertCircle } from "lucide-react";

import { Button } from "@/components/ui/button";

export default function Error({
  error,
  reset,
}: Readonly<{
  error: Error & { digest?: string };
  reset: () => void;
}>) {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-3xl items-center justify-center px-5 py-12">
      <div className="rounded-lg border border-border bg-white p-8 shadow-soft">
        <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-full bg-warning text-warning-foreground">
          <AlertCircle className="h-6 w-6" aria-hidden="true" />
        </div>
        <h1 className="text-2xl font-semibold tracking-normal text-foreground">
          Something interrupted the page.
        </h1>
        <p className="mt-3 text-sm leading-6 text-muted-foreground">
          The frontend caught an unexpected state. Try again, and keep the API
          server running if this page depends on live data.
        </p>
        {error.digest ? (
          <p className="mt-3 text-xs text-muted-foreground">Digest: {error.digest}</p>
        ) : null}
        <Button className="mt-6" onClick={reset}>
          Try again
        </Button>
      </div>
    </main>
  );
}
