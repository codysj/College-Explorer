"use client";

import { BarChart3, Database, Eye, FileText, RefreshCw, Save, ShieldCheck } from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { fetchAnalyticsSummary } from "@/lib/analytics";
import type { AnalyticsCountRow, AnalyticsRateRow, AnalyticsSummaryResponse } from "@/types/api";

export function AnalyticsDashboard() {
  const [summary, setSummary] = useState<AnalyticsSummaryResponse | null>(null);
  const [loadState, setLoadState] = useState<"loading" | "ready" | "error">("loading");

  function load() {
    setLoadState("loading");
    fetchAnalyticsSummary()
      .then((payload) => {
        setSummary(payload);
        setLoadState("ready");
      })
      .catch(() => {
        setLoadState("error");
      });
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <main className="mx-auto min-h-screen w-full max-w-7xl px-5 pb-16 pt-8 sm:px-8">
      <header className="mb-8 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <Link className="text-sm font-semibold text-primary" href="/">
            College Exploration
          </Link>
          <h1 className="mt-3 text-3xl font-semibold tracking-normal text-foreground sm:text-4xl">
            Analytics and ranking evaluation
          </h1>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-muted-foreground">
            Internal telemetry for product feedback loops, ranking-version usage, reason-code coverage, and decision-flow engagement.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <Badge variant="muted">Internal V2.8</Badge>
          <Button type="button" variant="secondary" onClick={load}>
            <RefreshCw className="h-4 w-4" aria-hidden="true" />
            Refresh
          </Button>
        </div>
      </header>

      {loadState === "loading" ? <DashboardSkeleton /> : null}
      {loadState === "error" ? (
        <EmptyState
          title="Analytics unavailable"
          description="Start the FastAPI backend or seed events, then refresh this internal dashboard."
        />
      ) : null}
      {loadState === "ready" && summary ? <DashboardBody summary={summary} /> : null}
    </main>
  );
}

function DashboardBody({ summary }: { summary: AnalyticsSummaryResponse }) {
  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        {summary.metric_cards.map((card) => (
          <div key={card.label} className="rounded-lg border border-border bg-white p-5 shadow-soft">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">{card.label}</p>
            <p className="mt-2 text-3xl font-semibold text-foreground">{card.value}</p>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">{card.detail}</p>
          </div>
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <Panel icon={<BarChart3 className="h-5 w-5" />} title="Ranking Evaluation">
          <BarList rows={summary.ranking_evaluation.save_rate_by_fit_bucket.map(rateToCount)} labelSuffix="save rate" />
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <MiniSection title="Compare rate by rank">
              <RateRows rows={summary.ranking_evaluation.compare_rate_by_rank_position} />
            </MiniSection>
            <MiniSection title="Confidence distribution">
              <BarList rows={summary.ranking_evaluation.confidence_distribution.map((row) => ({ key: row.bucket, count: row.count }))} />
            </MiniSection>
          </div>
        </Panel>

        <Panel icon={<Database className="h-5 w-5" />} title="Ranking Signals">
          <div className="grid gap-4 md:grid-cols-2">
            <MiniSection title="Top reason codes">
              <BarList rows={summary.ranking_evaluation.top_reason_code_frequency} />
            </MiniSection>
            <MiniSection title="Ranking versions">
              <BarList rows={summary.ranking_version_usage} />
            </MiniSection>
          </div>
          <MiniSection title="Saved schools by strongest weight">
            <BarList rows={summary.ranking_evaluation.category_weight_save_correlations} />
          </MiniSection>
        </Panel>
      </section>

      <section className="grid gap-6 xl:grid-cols-3">
        <Panel icon={<Eye className="h-5 w-5" />} title="Discovery">
          <MiniSection title="Most-used filters">
            <BarList rows={summary.most_used_filters} />
          </MiniSection>
          <MiniSection title="Most-viewed schools">
            <BarList rows={summary.most_viewed_schools.map((row) => ({ key: row.school_name, count: row.count }))} />
          </MiniSection>
        </Panel>

        <Panel icon={<Save className="h-5 w-5" />} title="Decision Actions">
          <MiniSection title="Most-saved schools">
            <BarList rows={summary.most_saved_schools.map((row) => ({ key: row.school_name, count: row.count }))} />
          </MiniSection>
          <MiniSection title="Save rate by rank">
            <RateRows rows={summary.save_rate_by_rank_position} />
          </MiniSection>
        </Panel>

        <Panel icon={<FileText className="h-5 w-5" />} title="Reports And Funnel">
          <MiniSection title="Report generation">
            <BarList rows={summary.report_generation_frequency} />
          </MiniSection>
          <MiniSection title="Onboarding completion">
            <RateRows rows={[summary.onboarding_completion_rate]} />
          </MiniSection>
        </Panel>
      </section>

      <section className="rounded-lg border border-border bg-white p-5 shadow-soft">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-foreground">
          <ShieldCheck className="h-5 w-5 text-primary" aria-hidden="true" />
          Privacy and limitations
        </h2>
        <p className="mt-3 text-sm leading-6 text-muted-foreground">{summary.privacy_note}</p>
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {summary.limitations.map((item) => (
            <p key={item} className="rounded-md bg-muted p-3 text-sm leading-6 text-muted-foreground">{item}</p>
          ))}
        </div>
      </section>
    </div>
  );
}

function Panel({ children, icon, title }: { children: ReactNode; icon: ReactNode; title: string }) {
  return (
    <section className="rounded-lg border border-border bg-white p-5 shadow-soft">
      <h2 className="mb-5 flex items-center gap-2 text-lg font-semibold text-foreground">
        <span className="text-primary">{icon}</span>
        {title}
      </h2>
      {children}
    </section>
  );
}

function MiniSection({ children, title }: { children: ReactNode; title: string }) {
  return (
    <div className="mb-5 last:mb-0">
      <h3 className="mb-3 text-sm font-semibold text-foreground">{title}</h3>
      {children}
    </div>
  );
}

function BarList({ labelSuffix, rows }: { labelSuffix?: string; rows: AnalyticsCountRow[] }) {
  const max = Math.max(...rows.map((row) => row.count), 1);
  if (!rows.length) return <p className="text-sm text-muted-foreground">No events yet.</p>;
  return (
    <div className="space-y-3">
      {rows.map((row) => (
        <div key={row.key}>
          <div className="flex items-center justify-between gap-3 text-sm">
            <span className="truncate font-medium text-foreground">{humanize(row.key)}</span>
            <span className="text-muted-foreground">{row.count}{labelSuffix ? ` ${labelSuffix}` : ""}</span>
          </div>
          <div className="mt-1 h-2 overflow-hidden rounded-full bg-muted">
            <div className="h-full bg-primary" style={{ width: `${Math.max(5, (row.count / max) * 100)}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}

function RateRows({ rows }: { rows: AnalyticsRateRow[] }) {
  return (
    <div className="space-y-3">
      {rows.map((row) => (
        <div key={row.bucket} className="rounded-md bg-muted p-3">
          <div className="flex items-center justify-between gap-3 text-sm">
            <span className="font-medium text-foreground">{humanize(row.bucket)}</span>
            <span className="text-muted-foreground">{Math.round(row.rate * 100)}%</span>
          </div>
          <p className="mt-1 text-xs text-muted-foreground">{row.numerator} of {row.denominator}</p>
        </div>
      ))}
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
      {Array.from({ length: 5 }, (_, index) => <Skeleton key={index} className="h-36 w-full" />)}
    </div>
  );
}

function rateToCount(row: AnalyticsRateRow): AnalyticsCountRow {
  return { key: row.bucket, count: Math.round(row.rate * 100) };
}

function humanize(value: string) {
  return value.replaceAll("_", " ");
}
