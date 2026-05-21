"use client";

import { AlertCircle, ArrowLeft, Calculator, CheckCircle2, GitCompare, Trophy, X } from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import {
  buildLocalCostCalculator,
  defaultCostAssumption,
  requestCostCalculator,
  type CostCalculatorDraft,
} from "@/lib/cost-calculator";
import { buildComparisonSummary } from "@/lib/comparison";
import { useSchoolActionState } from "@/lib/school-actions";
import { getSchoolProfiles } from "@/lib/schools";
import type { CostCalculatorResponse, SchoolProfile } from "@/types/api";

type LoadState = "idle" | "loading" | "ready" | "error";

export function ComparisonWorkspace() {
  const { comparedSchools, compareIds, removeCompareSchool } = useSchoolActionState();
  const [profiles, setProfiles] = useState<SchoolProfile[]>([]);
  const [costAssumptions, setCostAssumptions] = useState<CostCalculatorDraft[]>([]);
  const [costReport, setCostReport] = useState<CostCalculatorResponse | null>(null);
  const [familyBudget, setFamilyBudget] = useState<number | null>(null);
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

  useEffect(() => {
    setCostAssumptions((current) => {
      const currentBySchool = new Map(current.map((item) => [item.school_id, item]));
      return profiles.map((profile) => ({ ...defaultCostAssumption(profile), ...currentBySchool.get(profile.school_id) }));
    });
  }, [profiles]);

  useEffect(() => {
    if (profiles.length < 2) {
      setCostReport(null);
      return;
    }
    setCostReport(buildLocalCostCalculator(profiles, costAssumptions, costAssumptions[0]?.school_id, familyBudget));
  }, [profiles, costAssumptions, familyBudget]);

  const calculateCosts = async () => {
    try {
      setCostReport(await requestCostCalculator(costAssumptions, costAssumptions[0]?.school_id, familyBudget));
    } catch {
      setCostReport(buildLocalCostCalculator(profiles, costAssumptions, costAssumptions[0]?.school_id, familyBudget));
    }
  };

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
          <CostComparison
            assumptions={costAssumptions}
            budget={familyBudget}
            costReport={costReport}
            onBudgetChange={setFamilyBudget}
            onCalculate={calculateCosts}
            onUpdate={(schoolId, patch) => {
              setCostAssumptions((current) =>
                current.map((item) => item.school_id === schoolId ? { ...item, ...patch } : item),
              );
            }}
          />
          <MetricsTable profiles={profiles} onRemove={removeCompareSchool} />
          <CategoryWinners summary={summary} />
          <TradeoffSummary tradeoffs={summary.tradeoffs} />
        </div>
      ) : null}
    </main>
  );
}

function CostComparison({
  assumptions,
  budget,
  costReport,
  onBudgetChange,
  onCalculate,
  onUpdate,
}: {
  assumptions: CostCalculatorDraft[];
  budget: number | null;
  costReport: CostCalculatorResponse | null;
  onBudgetChange: (value: number | null) => void;
  onCalculate: () => void;
  onUpdate: (schoolId: number, patch: Partial<CostCalculatorDraft>) => void;
}) {
  return (
    <section className="rounded-lg border border-border bg-white p-5 shadow-soft">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h2 className="flex items-center gap-2 text-lg font-semibold tracking-normal text-foreground">
            <Calculator className="h-5 w-5 text-primary" aria-hidden="true" />
            Cost/value calculator
          </h2>
          <p className="mt-1 text-sm leading-6 text-muted-foreground">
            Edit aid, scholarship, and loan assumptions to compare four-year cost and debt sensitivity.
          </p>
        </div>
        <div className="flex flex-wrap items-end gap-3">
          <MoneyInput label="Family yearly budget" value={budget} onChange={onBudgetChange} />
          <button
            className="inline-flex h-10 items-center gap-2 rounded-md bg-primary px-4 text-sm font-semibold text-primary-foreground transition hover:bg-primary/90"
            type="button"
            onClick={onCalculate}
          >
            <Calculator className="h-4 w-4" aria-hidden="true" />
            Calculate
          </button>
        </div>
      </div>
      <div className="mt-5 overflow-x-auto">
        <table className="min-w-[920px] w-full border-collapse text-left text-sm">
          <thead>
            <tr className="border-b border-border bg-muted/60">
              <th className="w-44 px-4 py-3 font-semibold text-foreground">Assumption</th>
              {assumptions.map((item) => {
                const result = costReport?.results.find((school) => school.school_id === item.school_id);
                return <th key={item.school_id} className="min-w-56 px-4 py-3 font-semibold text-foreground">{result?.name ?? `School ${item.school_id}`}</th>;
              })}
            </tr>
          </thead>
          <tbody>
            {[
              ["Scholarships", "scholarships"],
              ["Grants/aid", "grants_aid"],
              ["Yearly cost", "estimated_yearly_cost"],
              ["Annual loans", "annual_loan_amount"],
            ].map(([label, key]) => (
              <tr key={key} className="border-b border-border">
                <th className="px-4 py-3 font-semibold text-foreground">{label}</th>
                {assumptions.map((item) => (
                  <td key={`${item.school_id}-${key}`} className="px-4 py-3">
                    <MoneyInput
                      label={`${label} for school ${item.school_id}`}
                      compact
                      value={(item[key as keyof CostCalculatorDraft] as number | null | undefined) ?? null}
                      onChange={(value) => onUpdate(item.school_id, { [key]: value } as Partial<CostCalculatorDraft>)}
                    />
                  </td>
                ))}
              </tr>
            ))}
            {[
              ["Estimated four-year cost", (schoolId: number) => formatCurrency(costReport?.results.find((item) => item.school_id === schoolId)?.estimated_four_year_total_cost ?? null)],
              ["Four-year difference", (schoolId: number) => formatSignedCurrency(costReport?.results.find((item) => item.school_id === schoolId)?.four_year_cost_difference ?? null)],
              ["Debt exposure", (schoolId: number) => formatCurrency(costReport?.results.find((item) => item.school_id === schoolId)?.estimated_debt_exposure ?? null)],
              ["Value direction", (schoolId: number) => costReport?.results.find((item) => item.school_id === schoolId)?.directional_outcome_adjusted_value.replaceAll("_", " ") ?? "Unknown"],
            ].map(([label, formatter]) => (
              <tr key={label as string} className="border-b border-border last:border-b-0">
                <th className="px-4 py-3 font-semibold text-foreground">{label as string}</th>
                {assumptions.map((item) => (
                  <td key={`${item.school_id}-${label}`} className="px-4 py-3 text-muted-foreground">
                    {(formatter as (schoolId: number) => string)(item.school_id)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {costReport ? (
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {costReport.comparison_summary.map((item) => (
            <p key={item} className="rounded-md bg-muted p-3 text-sm leading-6 text-muted-foreground">{item}</p>
          ))}
          <p className="rounded-md bg-muted p-3 text-sm leading-6 text-muted-foreground">{costReport.disclaimer}</p>
        </div>
      ) : null}
    </section>
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

function formatSignedCurrency(value: number | null) {
  if (value === null) return "Unknown";
  const formatted = formatCurrency(Math.abs(value));
  if (value === 0) return "$0";
  return value > 0 ? `+${formatted}` : `-${formatted}`;
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

function MoneyInput({
  compact = false,
  label,
  onChange,
  value,
}: {
  compact?: boolean;
  label: string;
  onChange: (value: number | null) => void;
  value: number | null;
}) {
  return (
    <label className="block">
      <span className={compact ? "sr-only" : "text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground"}>{label}</span>
      <input
        aria-label={label}
        className={`${compact ? "" : "mt-1"} h-10 w-full rounded-md border border-border bg-white px-3 text-sm outline-none transition focus:border-primary`}
        inputMode="numeric"
        min={0}
        type="number"
        value={value ?? ""}
        onChange={(event) => onChange(event.target.value ? Number(event.target.value) : null)}
      />
    </label>
  );
}
