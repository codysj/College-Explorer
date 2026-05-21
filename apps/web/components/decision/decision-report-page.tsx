"use client";

import { AlertCircle, ArrowLeft, BadgeDollarSign, BarChart3, FileText, HelpCircle, Printer, ShieldCheck, Trophy } from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { readDecisionReport } from "@/lib/decision";
import type { DecisionReportResponse } from "@/types/api";

export function DecisionReportPage() {
  const [report, setReport] = useState<DecisionReportResponse | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setReport(readDecisionReport());
    setReady(true);
  }, []);

  if (ready && !report) {
    return (
      <main className="mx-auto min-h-screen w-full max-w-5xl px-5 py-10 sm:px-8">
        <EmptyState
          title="No decision report yet"
          description="Generate a report from the accepted-schools workspace before opening the shareable view."
          action={<Link href="/decision">Back to accepted schools</Link>}
        />
      </main>
    );
  }

  if (!report) return null;

  const recommendations = [
    report.best_overall_fit,
    report.best_value,
    report.strongest_career_upside,
    report.lowest_risk,
  ];

  return (
    <main className="decision-report mx-auto min-h-screen w-full max-w-6xl px-5 pb-16 pt-8 sm:px-8">
      <div className="no-print mb-6 flex flex-wrap items-center justify-between gap-3">
        <Button asChild variant="secondary">
          <Link href="/decision">
            <ArrowLeft className="h-4 w-4" aria-hidden="true" />
            Back to workspace
          </Link>
        </Button>
        <Button type="button" onClick={() => window.print()}>
          <Printer className="h-4 w-4" aria-hidden="true" />
          Print
        </Button>
      </div>

      <article className="overflow-hidden rounded-lg border border-border bg-white shadow-soft">
        <header className="border-b border-border bg-[hsl(185_45%_96%)] p-6 sm:p-8">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.12em] text-primary">Decision briefing</p>
              <h1 className="mt-2 text-3xl font-semibold tracking-normal text-foreground sm:text-4xl">
                {report.report_title}
              </h1>
              <p className="mt-3 max-w-3xl text-sm leading-6 text-muted-foreground">
                Generated {new Date(report.generated_at).toLocaleDateString()} using ranking {report.ranking_version} and report {report.report_version}.
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge variant={report.decision_confidence === "high" ? "default" : "muted"}>
                {report.decision_confidence} confidence
              </Badge>
              <Badge variant="muted">{report.schools.length} finalists</Badge>
            </div>
          </div>
        </header>

        <section className="grid gap-4 border-b border-border p-6 sm:grid-cols-2 lg:grid-cols-4 lg:p-8">
          {recommendations.map((item) => (
            <div key={item.label} className="rounded-md border border-border p-4">
              <div className="flex items-center gap-2 text-sm font-semibold text-muted-foreground">
                {item.label === "Best value" ? <BadgeDollarSign className="h-4 w-4 text-primary" /> : <Trophy className="h-4 w-4 text-primary" />}
                {displayRecommendationLabel(item.label)}
              </div>
              <p className="mt-3 text-lg font-semibold text-foreground">{item.school_name ?? "Not enough data"}</p>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">{item.rationale}</p>
            </div>
          ))}
        </section>

        <ReportSection icon={<BarChart3 className="h-5 w-5" />} title="Finalist Ranking">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] border-collapse text-left text-sm">
              <thead className="text-xs uppercase tracking-[0.1em] text-muted-foreground">
                <tr className="border-b border-border">
                  <th className="py-3 pr-4">Rank</th>
                  <th className="py-3 pr-4">School</th>
                  <th className="py-3 pr-4">Fit</th>
                  <th className="py-3 pr-4">Confidence</th>
                  <th className="py-3 pr-4">Yearly Cost</th>
                  <th className="py-3 pr-4">Career</th>
                  <th className="py-3 pr-4">Tradeoff</th>
                </tr>
              </thead>
              <tbody>
                {report.finalist_ranking_table.map((row) => (
                  <tr key={row.school_id} className="border-b border-border last:border-0">
                    <td className="py-3 pr-4 font-semibold">{row.rank}</td>
                    <td className="py-3 pr-4 font-semibold">{row.school_name}</td>
                    <td className="py-3 pr-4">{Math.round(row.fit_score)}</td>
                    <td className="py-3 pr-4">{Math.round(row.confidence_score * 100)}%</td>
                    <td className="py-3 pr-4">{formatCurrency(row.estimated_yearly_cost)}</td>
                    <td className="py-3 pr-4">{row.career_score === null ? "Unknown" : Math.round(row.career_score)}</td>
                    <td className="py-3 pr-4 text-muted-foreground">{humanize(row.major_tradeoff)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </ReportSection>

        <ReportSection icon={<BadgeDollarSign className="h-5 w-5" />} title="Cost And Value">
          <div className="grid gap-3 md:grid-cols-2">
            {report.cost_value_comparison.map((row) => (
              <div key={row.school_id} className="rounded-md border border-border p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-semibold text-foreground">{row.school_name}</p>
                    <p className="mt-1 text-sm text-muted-foreground">{formatCurrency(row.estimated_four_year_total_cost)} estimated four-year cost</p>
                  </div>
                  <Badge variant={row.affordability_status === "within_budget" ? "default" : "muted"}>
                    {humanize(row.affordability_status)}
                  </Badge>
                </div>
                <p className="mt-3 text-sm leading-6 text-muted-foreground">
                  Directional value: {humanize(row.directional_value)}. Confidence: {row.confidence}.
                </p>
                {row.warnings.length ? <p className="mt-2 text-xs leading-5 text-muted-foreground">{row.warnings.map(humanize).join(", ")}</p> : null}
              </div>
            ))}
          </div>
        </ReportSection>

        <ReportSection icon={<AlertCircle className="h-5 w-5" />} title="Biggest Tradeoffs">
          <div className="grid gap-3 md:grid-cols-2">
            {report.major_tradeoffs.map((tradeoff) => (
              <p key={tradeoff} className="rounded-md bg-muted p-4 text-sm leading-6 text-muted-foreground">
                {tradeoff}
              </p>
            ))}
          </div>
        </ReportSection>

        <ReportSection icon={<ShieldCheck className="h-5 w-5" />} title="Sensitivity Highlights">
          <div className="grid gap-3 md:grid-cols-3">
            {report.sensitivity_highlights.map((item) => (
              <div key={`${item.label}-${item.school_id ?? "none"}`} className="rounded-md bg-muted p-4">
                <p className="font-semibold text-foreground">{item.label}</p>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">{item.summary}</p>
              </div>
            ))}
          </div>
        </ReportSection>

        <ReportSection icon={<HelpCircle className="h-5 w-5" />} title="Questions Still Worth Investigating">
          <div className="grid gap-3 md:grid-cols-2">
            {report.unresolved_questions.map((item) => (
              <div key={item.school_id} className="rounded-md border border-border p-4">
                <p className="font-semibold text-foreground">{item.school_name}</p>
                <ul className="mt-3 space-y-2 text-sm leading-6 text-muted-foreground">
                  {(item.questions.length ? item.questions : ["No unresolved questions entered."]).map((question) => (
                    <li key={question}>{question}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </ReportSection>

        <ReportSection icon={<FileText className="h-5 w-5" />} title="Methodology And Disclaimer">
          <div className="grid gap-4 lg:grid-cols-2">
            <p className="text-sm leading-6 text-muted-foreground">{report.methodology_note}</p>
            <p className="text-sm leading-6 text-muted-foreground">{report.disclaimer}</p>
          </div>
          {report.confidence_flags.length ? (
            <p className="mt-4 rounded-md bg-muted p-3 text-sm leading-6 text-muted-foreground">
              Confidence flags: {report.confidence_flags.map(humanize).join(", ")}
            </p>
          ) : null}
        </ReportSection>
      </article>
    </main>
  );
}

function ReportSection({ children, icon, title }: { children: ReactNode; icon: ReactNode; title: string }) {
  return (
    <section className="border-b border-border p-6 last:border-0 lg:p-8">
      <h2 className="mb-5 flex items-center gap-2 text-xl font-semibold text-foreground">
        <span className="text-primary">{icon}</span>
        {title}
      </h2>
      {children}
    </section>
  );
}

function formatCurrency(value: number | null) {
  return value === null ? "Unknown" : new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);
}

function humanize(value: string) {
  return value.replaceAll("_", " ");
}

function displayRecommendationLabel(label: string) {
  if (label === "Best value") return "Best Financial Value";
  if (label === "Strongest career upside") return "Highest Career Upside";
  return label;
}
