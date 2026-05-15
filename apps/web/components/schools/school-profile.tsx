"use client";

import {
  AlertCircle,
  ArrowLeft,
  Bookmark,
  BookmarkCheck,
  Building2,
  CheckCircle2,
  CircleDollarSign,
  GraduationCap,
  GitCompare,
  Home,
  Info,
  Loader2,
  TrendingUp,
  Users,
  type LucideIcon,
} from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricRow } from "@/components/ui/metric-row";
import { ScorePill } from "@/components/ui/score-pill";
import { Skeleton } from "@/components/ui/skeleton";
import { ApiClientError } from "@/lib/api-client";
import { useSchoolActionState } from "@/lib/school-actions";
import { getSchoolProfile } from "@/lib/schools";
import { cn } from "@/lib/utils";
import type { SchoolProfile } from "@/types/api";

type SchoolProfilePageProps = {
  schoolId: number;
};

export function SchoolProfilePage({ schoolId }: SchoolProfilePageProps) {
  const [profile, setProfile] = useState<SchoolProfile | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [retryNonce, setRetryNonce] = useState(0);
  const { compareIds, compareLimit, savedIds, toggleCompare, toggleSaved } = useSchoolActionState();

  useEffect(() => {
    const controller = new AbortController();
    setIsLoading(true);
    setError(null);

    getSchoolProfile(schoolId, controller.signal)
      .then((payload) => setProfile(payload))
      .catch((reason: unknown) => {
        if (controller.signal.aborted) return;
        if (reason instanceof ApiClientError && reason.status === 404) {
          setError("School profile not found.");
          return;
        }
        setError(reason instanceof Error ? reason.message : "School profile failed to load.");
      })
      .finally(() => {
        if (!controller.signal.aborted) setIsLoading(false);
      });

    return () => controller.abort();
  }, [retryNonce, schoolId]);

  if (isLoading && !profile) {
    return <ProfileSkeleton />;
  }

  if (error && !profile) {
    return <ProfileError message={error} onRetry={() => setRetryNonce((current) => current + 1)} />;
  }

  if (!profile) {
    return <ProfileError message="Data unavailable." onRetry={() => setRetryNonce((current) => current + 1)} />;
  }

  const isSaved = savedIds.has(profile.school_id);
  const isCompared = compareIds.has(profile.school_id);
  const compareDisabled = !isCompared && compareIds.size >= compareLimit;

  return (
    <main className="mx-auto min-h-screen w-full max-w-7xl px-5 pb-16 pt-8 sm:px-8">
      <Link className="inline-flex items-center gap-2 text-sm font-semibold text-primary" href="/search">
        <ArrowLeft className="h-4 w-4" aria-hidden="true" />
        Back to search
      </Link>

      <ProfileHeader
        compareDisabled={compareDisabled}
        isCompared={isCompared}
        isLoading={isLoading}
        isSaved={isSaved}
        profile={profile}
        onToggleCompare={() => toggleCompare(profile)}
        onToggleSaved={() => toggleSaved(profile)}
      />

      <div className="mt-6 grid gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
        <div className="space-y-6">
          <FitSummary profile={profile} />
          <AcademicsSection profile={profile} />
          <CostSection profile={profile} />
          <OutcomesSection profile={profile} />
          <CampusLifeSection profile={profile} />
        </div>
        <aside className="space-y-6 lg:sticky lg:top-6 lg:self-start">
          <DataQualityCard profile={profile} />
          <SimilarSchoolsSection profile={profile} />
          <CompareTraySummary selectedCount={compareIds.size} selectionLimit={compareLimit} />
        </aside>
      </div>
    </main>
  );
}

function ProfileHeader({
  compareDisabled,
  isCompared,
  isLoading,
  isSaved,
  onToggleCompare,
  onToggleSaved,
  profile,
}: {
  compareDisabled: boolean;
  isCompared: boolean;
  isLoading: boolean;
  isSaved: boolean;
  onToggleCompare: () => void;
  onToggleSaved: () => void;
  profile: SchoolProfile;
}) {
  return (
    <section className="mt-6 rounded-lg border border-border bg-white p-6 shadow-soft">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline">{profile.type}</Badge>
            <Badge variant="muted">{profile.setting}</Badge>
            {isLoading ? (
              <Badge variant="muted">
                <Loader2 className="mr-1 h-3 w-3 animate-spin" aria-hidden="true" />
                Refreshing
              </Badge>
            ) : null}
          </div>
          <h1 className="mt-4 text-3xl font-semibold tracking-normal text-foreground sm:text-5xl">
            {profile.name}
          </h1>
          <p className="mt-3 text-base leading-7 text-muted-foreground">
            {profile.city}, {profile.state} - {profile.region}
          </p>
        </div>
        <div className="grid gap-2 sm:grid-cols-2 lg:w-72">
          <Button type="button" variant={isSaved ? "primary" : "secondary"} onClick={onToggleSaved}>
            {isSaved ? <BookmarkCheck className="h-4 w-4" aria-hidden="true" /> : <Bookmark className="h-4 w-4" aria-hidden="true" />}
            {isSaved ? "Saved" : "Save"}
          </Button>
          <Button disabled={compareDisabled} type="button" variant={isCompared ? "primary" : "secondary"} onClick={onToggleCompare}>
            <GitCompare className="h-4 w-4" aria-hidden="true" />
            {isCompared ? "Added" : "Compare"}
          </Button>
        </div>
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatTile icon={Building2} label="School type" value={profile.type} />
        <StatTile icon={Users} label="Enrollment" value={formatNumber(profile.enrollment)} />
        <StatTile icon={Home} label="Setting" value={profile.setting} />
        <StatTile icon={CircleDollarSign} label="Net price" value={formatCurrency(profile.cost.net_price)} />
      </div>
    </section>
  );
}

function FitSummary({ profile }: { profile: SchoolProfile }) {
  const categoryScores = Object.entries(profile.category_scores ?? {});

  return (
    <SectionCard icon={CheckCircle2} title="Fit Summary">
      <div className="grid gap-5 lg:grid-cols-[220px_1fr]">
        <div className="space-y-3">
          <ScorePill className="w-full" label="Fit" score={profile.fit_score} />
          <ScorePill className="w-full border-accent/20 bg-accent/10 text-accent" label="Confidence" score={profile.data_confidence_score * 100} />
          <p className="rounded-md bg-muted p-3 text-sm leading-6 text-muted-foreground">
            Ranking fit is unavailable until profile ranking is connected. Confidence here reflects profile data completeness.
          </p>
        </div>

        <div className="space-y-5">
          <div>
            <p className="text-sm font-semibold text-foreground">Category score breakdown</p>
            {categoryScores.length > 0 ? (
              <div className="mt-3 space-y-3">
                {categoryScores.map(([category, score]) => (
                  <ScoreBar key={category} label={formatLabel(category)} score={score} />
                ))}
              </div>
            ) : (
              <UnavailableBlock text="Data unavailable. Category scores are only returned by ranked results today." />
            )}
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <InsightList emptyText="Data unavailable. No deterministic reasons are present for this profile yet." items={profile.top_reasons} title="Top reasons" />
            <InsightList emptyText="Data unavailable. No deterministic tradeoffs are present for this profile yet." items={profile.top_tradeoffs} title="Top tradeoffs" warning />
          </div>

          <MetricRow label="Ranking version" value={profile.ranking_version ?? "Data unavailable"} />
        </div>
      </div>
    </SectionCard>
  );
}

function AcademicsSection({ profile }: { profile: SchoolProfile }) {
  return (
    <SectionCard icon={GraduationCap} title="Academics">
      <div className="grid gap-6 lg:grid-cols-[1fr_280px]">
        <TagPanel emptyText="Data unavailable for popular majors." items={profile.academics.popular_majors ?? []} title="Popular majors" />
        <MetricStack
          metrics={[
            ["Graduation rate", formatPercent(profile.academics.graduation_rate)],
            ["Retention rate", formatPercent(profile.academics.retention_rate)],
            ["Student-faculty ratio", profile.academics.student_faculty_ratio === null ? "Data unavailable" : `${profile.academics.student_faculty_ratio}:1`],
          ]}
        />
      </div>
    </SectionCard>
  );
}

function CostSection({ profile }: { profile: SchoolProfile }) {
  return (
    <SectionCard icon={CircleDollarSign} title="Cost">
      <div className="grid gap-4 md:grid-cols-2">
        <MetricStack
          metrics={[
            ["In-state tuition", formatCurrency(profile.cost.tuition_in_state)],
            ["Out-of-state tuition", formatCurrency(profile.cost.tuition_out_state)],
            ["Net price", formatCurrency(profile.cost.net_price)],
          ]}
        />
        <MetricStack
          metrics={[
            ["Average aid", formatCurrency(profile.cost.average_aid)],
            ["Median debt", formatCurrency(profile.cost.debt_median)],
          ]}
        />
      </div>
    </SectionCard>
  );
}

function OutcomesSection({ profile }: { profile: SchoolProfile }) {
  return (
    <SectionCard icon={TrendingUp} title="Outcomes">
      <div className="grid gap-4 md:grid-cols-3">
        <MetricTile label="Median earnings" value={formatCurrency(profile.outcomes.median_earnings)} />
        <MetricTile label="Completion rate" value={formatPercent(profile.outcomes.completion_rate)} />
        <MetricTile label="Repayment rate" value={formatPercent(profile.outcomes.repayment_rate)} />
      </div>
      <div className="mt-4">
        {profile.outcomes.outcome_percentiles ? (
          <TagPanel items={Object.keys(profile.outcomes.outcome_percentiles)} title="Career/outcome indicators" />
        ) : (
          <UnavailableBlock text="Data unavailable. Outcome percentile indicators are not in the V1 profile schema yet." />
        )}
      </div>
    </SectionCard>
  );
}

function CampusLifeSection({ profile }: { profile: SchoolProfile }) {
  return (
    <SectionCard icon={Home} title="Campus Life">
      <div className="grid gap-4 md:grid-cols-2">
        <MetricStack
          metrics={[
            ["Setting", profile.setting],
            ["Housing", formatBoolean(profile.campus_life.housing)],
            ["Athletics", profile.campus_life.sports ?? "Data unavailable"],
            ["Greek life", formatPercent(profile.campus_life.greek_life)],
          ]}
        />
        <TagPanel
          emptyText="Data unavailable for diversity and culture tags."
          items={profile.campus_life.culture_tags ?? []}
          title="Diversity and culture"
        />
      </div>
    </SectionCard>
  );
}

function DataQualityCard({ profile }: { profile: SchoolProfile }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <Info className="h-5 w-5 text-primary" aria-hidden="true" />
          Data Quality
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ScoreBar label="Profile completeness" score={profile.data_confidence_score * 100} />
        <p className="mt-4 text-sm leading-6 text-muted-foreground">
          Missing values stay unknown instead of being converted to zero.
        </p>
        {profile.data_fields_missing.length > 0 ? (
          <div className="mt-4">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">
              Missing fields
            </p>
            <div className="mt-2 flex max-h-40 flex-wrap gap-2 overflow-auto">
              {profile.data_fields_missing.slice(0, 12).map((field) => (
                <Badge key={field} variant="muted">
                  {field}
                </Badge>
              ))}
            </div>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}

function SimilarSchoolsSection({ profile }: { profile: SchoolProfile }) {
  const items = profile.similar_schools;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Similar Schools</CardTitle>
      </CardHeader>
      <CardContent>
        {items.length > 0 ? (
          <div className="space-y-3">
            {items.slice(0, 3).map((item, index) => (
              <div key={`${String(item.school_id ?? index)}`} className="rounded-md border border-border p-3 text-sm">
                {String(item.name ?? "Related school")}
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {["Same region", "Comparable cost", "Similar academic profile"].map((label) => (
              <div key={label} className="rounded-md border border-dashed border-border bg-muted p-3 text-sm font-medium text-muted-foreground">
                {label} placeholder
              </div>
            ))}
            <p className="text-xs leading-5 text-muted-foreground">
              Semantic similar schools are planned for V2.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function CompareTraySummary({ selectedCount, selectionLimit }: { selectedCount: number; selectionLimit: number }) {
  return (
    <Card>
      <CardContent className="pt-6">
        <p className="text-sm font-semibold text-foreground">Compare tray</p>
        <p className="mt-1 text-sm text-muted-foreground">
          {selectedCount} of {selectionLimit} selected locally.
        </p>
      </CardContent>
    </Card>
  );
}

function SectionCard({
  children,
  icon: Icon,
  title,
}: {
  children: ReactNode;
  icon: LucideIcon;
  title: string;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Icon className="h-5 w-5 text-primary" aria-hidden="true" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}

function StatTile({ icon: Icon, label, value }: { icon: LucideIcon; label: string; value: string }) {
  return (
    <div className="rounded-md border border-border bg-muted p-4">
      <Icon className="h-5 w-5 text-primary" aria-hidden="true" />
      <p className="mt-3 text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">{label}</p>
      <p className="mt-1 text-lg font-semibold text-foreground">{value}</p>
    </div>
  );
}

function MetricStack({ metrics }: { metrics: Array<[string, string]> }) {
  return (
    <div className="space-y-3 rounded-md border border-border p-4">
      {metrics.map(([label, value]) => (
        <MetricRow key={label} label={label} value={value} />
      ))}
    </div>
  );
}

function MetricTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-border p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">{label}</p>
      <p className="mt-2 text-xl font-semibold text-foreground">{value}</p>
    </div>
  );
}

function TagPanel({
  emptyText = "Data unavailable.",
  items,
  title,
}: {
  emptyText?: string;
  items: string[];
  title: string;
}) {
  return (
    <div className="rounded-md border border-border p-4">
      <p className="text-sm font-semibold text-foreground">{title}</p>
      {items.length > 0 ? (
        <div className="mt-3 flex flex-wrap gap-2">
          {items.map((item) => (
            <Badge key={item} variant="outline">
              {item}
            </Badge>
          ))}
        </div>
      ) : (
        <UnavailableBlock className="mt-3" text={emptyText} />
      )}
    </div>
  );
}

function InsightList({
  emptyText,
  items,
  title,
  warning,
}: {
  emptyText: string;
  items: string[];
  title: string;
  warning?: boolean;
}) {
  return (
    <div>
      <p className="text-sm font-semibold text-foreground">{title}</p>
      {items.length > 0 ? (
        <ul className="mt-2 space-y-2 text-sm leading-6 text-foreground">
          {items.map((item) => (
            <li key={item}>{formatLabel(item)}</li>
          ))}
        </ul>
      ) : (
        <UnavailableBlock className={cn("mt-2", warning ? "bg-warning text-warning-foreground" : undefined)} text={emptyText} />
      )}
    </div>
  );
}

function UnavailableBlock({ className, text }: { className?: string; text: string }) {
  return (
    <p className={cn("rounded-md bg-muted p-3 text-sm leading-6 text-muted-foreground", className)}>
      {text}
    </p>
  );
}

function ScoreBar({ label, score }: { label: string; score: number }) {
  const clamped = Math.max(0, Math.min(100, score));

  return (
    <div>
      <div className="mb-1 flex items-center justify-between gap-4 text-sm">
        <span className="font-medium text-foreground">{label}</span>
        <span className="font-semibold text-foreground">{Math.round(clamped)}</span>
      </div>
      <div className="h-2 rounded-full bg-muted">
        <div className="h-2 rounded-full bg-primary" style={{ width: `${clamped}%` }} />
      </div>
    </div>
  );
}

function ProfileError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-3xl items-center justify-center px-5 py-12">
      <div className="rounded-lg border border-border bg-white p-8 shadow-soft">
        <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-md bg-warning text-warning-foreground">
          <AlertCircle className="h-6 w-6" aria-hidden="true" />
        </div>
        <h1 className="text-2xl font-semibold tracking-normal text-foreground">
          School profile failed to load
        </h1>
        <p className="mt-3 text-sm leading-6 text-muted-foreground">{message}</p>
        <div className="mt-6 flex gap-3">
          <Button type="button" onClick={onRetry}>Retry</Button>
          <Button asChild variant="secondary">
            <Link href="/search">Back to search</Link>
          </Button>
        </div>
      </div>
    </main>
  );
}

function ProfileSkeleton() {
  return (
    <main className="mx-auto min-h-screen w-full max-w-7xl px-5 pb-16 pt-8 sm:px-8">
      <Skeleton className="h-5 w-32" />
      <section className="mt-6 rounded-lg border border-border bg-white p-6 shadow-soft">
        <Skeleton className="h-6 w-36" />
        <Skeleton className="mt-5 h-12 w-3/4" />
        <Skeleton className="mt-3 h-5 w-72" />
        <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }, (_, index) => (
            <Skeleton key={index} className="h-28 w-full" />
          ))}
        </div>
      </section>
      <div className="mt-6 grid gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
        <div className="space-y-6">
          {Array.from({ length: 5 }, (_, index) => (
            <Card key={index}>
              <CardHeader>
                <Skeleton className="h-7 w-48" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-40 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
        <div className="space-y-6">
          <Skeleton className="h-64 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    </main>
  );
}

function formatCurrency(value: number | null) {
  return value === null
    ? "Data unavailable"
    : new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: 0,
      }).format(value);
}

function formatNumber(value: number | null) {
  return value === null ? "Data unavailable" : new Intl.NumberFormat("en-US").format(value);
}

function formatPercent(value: number | null) {
  return value === null ? "Data unavailable" : `${Math.round(value * 100)}%`;
}

function formatBoolean(value: boolean | null) {
  if (value === null) return "Data unavailable";
  return value ? "Available" : "Not available";
}

function formatLabel(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}
