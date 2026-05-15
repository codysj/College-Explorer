"use client";

import { GitCompare, X } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { useSchoolActionState } from "@/lib/school-actions";

export function GlobalCompareTray() {
  const {
    comparedSchools,
    compareIds,
    compareLimit,
    clearCompare,
    removeCompareSchool,
  } = useSchoolActionState();

  if (compareIds.size === 0) return null;

  return (
    <div className="fixed inset-x-0 bottom-0 z-30 border-t border-border bg-white/95 px-5 py-4 shadow-soft backdrop-blur">
      <div className="mx-auto flex max-w-7xl flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-start gap-3">
          <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground">
            <GitCompare className="h-5 w-5" aria-hidden="true" />
          </div>
          <div>
            <p className="text-sm font-semibold text-foreground">
              Compare tray: {compareIds.size} of {compareLimit} selected
            </p>
            <p className="mt-1 text-xs text-muted-foreground">
              Select 2 to {compareLimit} schools for the comparison workspace.
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {comparedSchools.map((school) => (
            <button
              key={school.school_id}
              className="inline-flex max-w-52 items-center gap-1 rounded-md border border-border bg-white px-2.5 py-1 text-xs font-semibold text-foreground transition hover:bg-muted"
              type="button"
              onClick={() => removeCompareSchool(school.school_id)}
            >
              <span className="truncate">{school.name}</span>
              <X className="h-3 w-3 shrink-0" aria-hidden="true" />
            </button>
          ))}
          {compareIds.size >= 2 ? (
            <Button asChild variant="primary">
              <Link href="/compare">Compare</Link>
            </Button>
          ) : (
            <Button disabled type="button" variant="primary">
              Compare
            </Button>
          )}
          <Button asChild variant="secondary">
            <Link href="/dashboard">Dashboard</Link>
          </Button>
          <Button type="button" variant="ghost" onClick={clearCompare}>
            Clear
          </Button>
        </div>
      </div>
    </div>
  );
}
