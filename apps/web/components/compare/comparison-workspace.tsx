"use client";

import { AlertCircle, ArrowLeft, CheckCircle2, GitCompare, Trophy, X } from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { buildComparisonSummary } from "@/lib/comparison";
import { useSchoolActionState } from "@/lib/school-actions";
import { getSchoolProfiles } from "@/lib/schools";
import type { SchoolProfile } from "@/types/api";

type LoadState = "idle" | "loading" | "ready" | "error";

export function ComparisonWorkspace() {
  const { comparedSchools, compareIds, removeCompareSchool } = useSchoolActionState();
  const [profiles, setProfiles] = useState<SchoolProfile[]>([]);
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [error, setError] = useState<string | null>(null);
  const selectedIds = useMemo(() => comparedSchools.map((school) => school.school_id), [comparedSchools]);

  useEffect(() => {
    if (selectedIds.length === 0) {
      setProfiles([]);
      setLoadState("idle");
      return;
    }

    const controller = new AbortController();
    setLoadState("loading");
    setError(null);

    getSchoolProfiles(selectedIds, controller.signal)
      .then((payload) => {
        setProfiles(payload);
        setLoadState("ready");
      })
      .catch((reason: unknown) => {
        if (controller.signal.aborted) return;
        setError(reason instanceof Error ? reason.message : "Comparison data failed to load.");
        setLoadState("error");
      });

    return () => controller.abort();
  }, [selectedIds]);

  const summary = useMemo(() => buildComparisonSummary(profiles), [profiles]);

  return (
    <main className="mx-auto min-h-screen w-full max-w-7xl px-5 pb-36 pt-8 sm:px-8">
      <Link className="inline-flex items-center gap-2 text-sm font-semibold text-primary" href="/search">
        <ArrowLeft className="h-4 w-4" aria-hidden="true" />
        Back to search
      </Link>

      <header className="mb-8 mt-6 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-normal text-foreground sm:text-4xl">
            Compare schools
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">
            Review 2 to 5 selected schools using deterministic profile metrics and explicit unknowns.
          </p>
        </div>
        <Badge variant={compareIds.size >= 2 ? "default" : "muted"}>
          {compareIds.size} selected
        </Badge>
      </header>

      {compareIds.size === 0 ? (
        <EmptyState
          title="No schools selected"
          description="Add schools from search results or profile pages to build a comparison."
          action={<Link href="/search">Explore schools</Link>}
        />
      ) : null}

      {compareIds.size === 1 ? (
        <EmptyState
          title="Add one more school"
          description="Comparison works best with at least two schools. Your current selection is saved in the tray."
          action={<Link href="/search">Find another school</Link>}
        />
      ) : null}

      {loadState === "loading" && compareIds.size >= 2 ? <ComparisonSkeleton /> : null}

      {loadState === "error" && compareIds.size >= 2 ? (
        <div className="rounded-lg border border-border bg-white p-6 shadow-soft">
          <div className="flex gap-3">
            <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-accent" aria-hidden="true" />
            <div>
              <p className="font-semibold text-foreground">Comparison failed to load</p>
              <p className="mt-1 text-sm leading-6 text-muted-foreground">{error}</p>
            </div>
          </div>
        </div>
      ) : null}

      {loadState === "ready" && compareIds.size >= 2 ? (
        <div className="space-y-6">
          <TopSummary summary={summary} />
          <MetricsTable profiles={profiles} onRemove={removeCompareSchool} />
          <CategoryWinners summary={summary} />
          <TradeoffSummary tradeoffs={summary.tradeoffs} />
        </div>
      ) : null}
    </main>
  );
}

function TopSummary({ summary }: { summary: ReturnType<typeof buildComparisonSummary> }) {
  return (
    <section className="grid gap-4 lg:grid-cols-4">
      <SummaryCard label="Best overall fit" school={summary.bestOverallFit} value={summary.bestOverallFit?.fit_score === null ? "Data-complete profile" : formatScore(summary.bestOverallFit?.fit_score)} />
      <SummaryCard label="Best value" school={summary.bestValue} value="Lowest known net price" />
      <SummaryCard label="Strongest career outcome" school={summary.strongestCareerOutcome} value="Highest known earnings" />
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <AlertCircle className="h-5 w-5 text-accent" aria-hidden="true" />
            Biggest tradeoff
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm leading-6 text-muted-foreground">{summary.biggestTradeoff}</p>
        </CardContent>
      </Card>
    </section>
  );
}

function SummaryCard({ label, school, value }: { label: string; school: SchoolProfile | null; value: string }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Trophy className="h-5 w-5 text-primary" aria-hidden="true" />
          {label}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-lg font-semibold text-foreground">{school?.name ?? "Unknown"}</p>
        <p className="mt-2 text-sm text-muted-foreground">{value}</p>
      </CardContent>
    </Card>
  );
}

function MetricsTable({ onRemove, profiles }: { onRemove: (schoolId: number) => void; profiles: SchoolProfile[] }) {
  const rows = [
    ["Net price", (school: SchoolProfile) => formatCurrency(school.cost.net_price)],
    ["Graduation rate", (school: SchoolProfile) => formatPercent(school.academics.graduation_rate)],
    ["Acceptance rate", (school: SchoolProfile) => formatPercent(school.acceptance_rate)],
    ["Enrollment", (school: SchoolProfile) => formatNumber(school.enrollment)],
    ["Median earnings", (school: SchoolProfile) => formatCurrency(school.outcomes.median_earnings)],
    ["Setting", (school: SchoolProfile) => school.setting],
    ["School type", (school: SchoolProfile) => school.type],
    ["Fit score", (school: SchoolProfile) => formatScore(school.fit_score)],
  ] as const;

  return (
    <section className="rounded-lg border border-border bg-white shadow-soft">
      <div className="flex items-center justify-between gap-4 border-b border-border p-5">
        <div>
          <h2 className="text-lg font-semibold tracking-normal text-foreground">Metrics table</h2>
          <p className="mt-1 text-xs text-muted-foreground">Unknown values remain explicit.</p>
        </div>
        <GitCompare className="h-5 w-5 text-primary" aria-hidden="true" />
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-[760px] w-full border-collapse text-left text-sm">
          <thead>
            <tr className="border-b border-border bg-muted/60">
              <th className="w-48 px-5 py-4 font-semibold text-foreground">Metric</th>
              {profiles.map((school) => (
                <th key={school.school_id} className="min-w-52 px-5 py-4 align-top font-semibold text-foreground">
                  <div className="flex items-start justify-between gap-3">
                    <Link className="transition-colors hover:text-primary" href={`/schools/${school.school_id}`}>
                      {school.name}
                    </Link>
                    <button
                      aria-label={`Remove ${school.name} from comparison`}
                      className="rounded-md p-1 text-muted-foreground transition hover:bg-white hover:text-foreground"
                      type="button"
                      onClick={() => onRemove(school.school_id)}
                    >
                      <X className="h-4 w-4" aria-hidden="true" />
                    </button>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map(([label, formatter]) => (
              <tr key={label} className="border-b border-border last:border-b-0">
                <th className="px-5 py-4 font-semibold text-foreground">{label}</th>
                {profiles.map((school) => (
                  <td key={`${school.school_id}-${label}`} className="px-5 py-4 text-muted-foreground">
                    {formatter(school)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function CategoryWinners({ summary }: { summary: ReturnType<typeof buildComparisonSummary> }) {
  return (
    <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {summary.winners.map((winner) => (
        <Card key={winner.category}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base capitalize">
              <CheckCircle2 className="h-5 w-5 text-primary" aria-hidden="true" />
              {winner.category}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="font-semibold text-foreground">{winner.school?.name ?? "Unknown"}</p>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">{winner.reason}</p>
          </CardContent>
        </Card>
      ))}
    </section>
  );
}

function TradeoffSummary({ tradeoffs }: { tradeoffs: string[] }) {
  return (
    <section className="rounded-lg border border-border bg-white p-5 shadow-soft">
      <h2 className="text-lg font-semibold tracking-normal text-foreground">Tradeoff summary</h2>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        {tradeoffs.map((tradeoff) => (
          <p key={tradeoff} className="rounded-md bg-muted p-4 text-sm leading-6 text-muted-foreground">
            {tradeoff}
          </p>
        ))}
      </div>
    </section>
  );
}

function ComparisonSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 lg:grid-cols-4">
        {Array.from({ length: 4 }, (_, index) => (
          <Skeleton key={index} className="h-40 w-full" />
        ))}
      </div>
      <Skeleton className="h-96 w-full" />
    </div>
  );
}

function formatCurrency(value: number | null) {
  return value === null
    ? "Unknown"
    : new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: 0,
      }).format(value);
}

function formatNumber(value: number | null) {
  return value === null ? "Unknown" : new Intl.NumberFormat("en-US").format(value);
}

function formatPercent(value: number | null) {
  return value === null ? "Unknown" : `${Math.round(value * 100)}%`;
}

function formatScore(value: number | null | undefined) {
  return value === null || value === undefined ? "Unavailable" : String(Math.round(value));
}
