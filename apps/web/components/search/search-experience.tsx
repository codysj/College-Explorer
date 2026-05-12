"use client";

import {
  AlertCircle,
  Bookmark,
  BookmarkCheck,
  ChevronLeft,
  ChevronRight,
  GitCompare,
  Search,
  SlidersHorizontal,
  X,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useState, useTransition } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { FilterPanelShell } from "@/components/ui/filter-panel-shell";
import { MetricRow } from "@/components/ui/metric-row";
import { ScorePill } from "@/components/ui/score-pill";
import { Skeleton } from "@/components/ui/skeleton";
import {
  buildSearchParams,
  defaultFilters,
  parseSearchFilters,
  searchSchools,
  sortOptions,
  type SearchFilters,
  type SortValue,
} from "@/lib/search";
import { loadPreferenceProfile, type PreferenceProfile } from "@/lib/preferences";
import { useSchoolActionState } from "@/lib/school-actions";
import { cn } from "@/lib/utils";
import type { SchoolSearchCard, SchoolSearchResponse } from "@/types/api";

const schoolTypes = ["Public", "Private"];
const settings = ["Urban", "Suburban", "Rural"];

type ActiveChip = {
  key: keyof SearchFilters;
  label: string;
};

export function SearchExperience() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();

  const urlFilters = useMemo(
    () => parseSearchFilters(new URLSearchParams(searchParams.toString())),
    [searchParams],
  );
  const [draftFilters, setDraftFilters] = useState<SearchFilters>(urlFilters);
  const [response, setResponse] = useState<SchoolSearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [retryNonce, setRetryNonce] = useState(0);
  const [preferenceProfile, setPreferenceProfile] = useState<PreferenceProfile | null>(null);
  const {
    clearCompare,
    compareIds,
    compareLimit,
    savedIds,
    toggleCompare,
    toggleSaved,
  } = useSchoolActionState();

  useEffect(() => {
    setDraftFilters(urlFilters);
  }, [retryNonce, urlFilters]);

  useEffect(() => {
    setPreferenceProfile(loadPreferenceProfile());
  }, []);

  useEffect(() => {
    const nextParams = buildSearchParams(draftFilters);
    const nextQuery = nextParams.toString();
    const currentQuery = searchParams.toString();
    if (nextQuery === currentQuery) return;

    const timeout = window.setTimeout(() => {
      startTransition(() => {
        router.replace(`${pathname}?${nextQuery}`, { scroll: false });
      });
    }, 350);

    return () => window.clearTimeout(timeout);
  }, [draftFilters, pathname, router, searchParams, startTransition]);

  useEffect(() => {
    const controller = new AbortController();
    const params = buildSearchParams(urlFilters);

    setIsLoading(true);
    setError(null);

    searchSchools(params, controller.signal)
      .then((payload) => {
        setResponse(payload);
      })
      .catch((reason: unknown) => {
        if (controller.signal.aborted) return;
        setError(reason instanceof Error ? reason.message : "Search failed.");
      })
      .finally(() => {
        if (!controller.signal.aborted) setIsLoading(false);
      });

    return () => controller.abort();
  }, [urlFilters]);

  const activeChips = useMemo(() => buildActiveChips(draftFilters), [draftFilters]);
  const results = response?.results ?? [];
  const totalResults = response?.total_results ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalResults / (response?.page_size ?? 10)));
  const selectedSchools = results.filter((school) => compareIds.has(school.school_id));

  const updateFilter = useCallback(
    <TKey extends keyof SearchFilters>(key: TKey, value: SearchFilters[TKey]) => {
      setDraftFilters((current) => ({
        ...current,
        [key]: value,
        page: key === "page" ? Number(value) : 1,
      }));
    },
    [],
  );

  const clearFilter = useCallback((key: keyof SearchFilters) => {
    setDraftFilters((current) => ({
      ...current,
      [key]: defaultFilters[key],
      page: 1,
    }));
  }, []);

  const resetFilters = useCallback(() => {
    setDraftFilters(defaultFilters);
  }, []);

  return (
    <main className="mx-auto min-h-screen w-full max-w-7xl px-5 pb-28 pt-8 sm:px-8">
      <header className="mb-8 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <Link className="text-sm font-semibold text-primary" href="/">
            College Exploration
          </Link>
          <h1 className="mt-3 text-3xl font-semibold tracking-normal text-foreground sm:text-4xl">
            Explore schools
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">
            Search the structured school dataset, keep promising options nearby,
            and stage schools for comparison. Ranking-specific fit reasons will
            appear here once V1.9 lands.
          </p>
        </div>

        <label className="flex min-w-56 flex-col gap-2 text-sm font-medium text-foreground">
          Sort
          <select
            className="h-11 rounded-md border border-border bg-white px-3 text-sm outline-none transition focus:border-primary"
            value={draftFilters.sort}
            onChange={(event) => updateFilter("sort", event.target.value as SortValue)}
          >
            {sortOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </header>

      <div className="grid gap-6 lg:grid-cols-[300px_1fr]">
        <FilterPanel
          activeChips={activeChips}
          filters={draftFilters}
          onClearFilter={clearFilter}
          onReset={resetFilters}
          onUpdate={updateFilter}
        />

        <section className="min-w-0">
          {preferenceProfile ? <PreferenceBanner profile={preferenceProfile} /> : null}

          <div className="mb-4 flex flex-col gap-3 rounded-lg border border-border bg-white p-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-semibold text-foreground">
                {isLoading && !response ? "Searching schools" : `${totalResults} schools found`}
              </p>
              <p className="mt-1 text-xs text-muted-foreground">
                Page {response?.page ?? draftFilters.page} of {totalPages}
                {isPending || isLoading ? " - updating" : ""}
              </p>
            </div>
            {sortOptions.find((option) => option.value === draftFilters.sort)?.note ? (
              <Badge variant="muted">
                {sortOptions.find((option) => option.value === draftFilters.sort)?.note}
              </Badge>
            ) : null}
          </div>

          {error ? <SearchError message={error} onRetry={() => setRetryNonce((current) => current + 1)} /> : null}

          {!error && !isLoading && results.length === 0 ? (
            <EmptyState
              title="No schools match these filters"
              description="Try removing a state, raising your max net price, or clearing selectivity filters."
              action={<button type="button" onClick={resetFilters}>Loosen filters</button>}
            />
          ) : null}

          <div
            className={cn(
              "grid gap-4 transition-opacity sm:grid-cols-2 xl:grid-cols-3",
              isLoading && response ? "opacity-60" : "opacity-100",
            )}
          >
            {isLoading && !response
              ? Array.from({ length: 6 }, (_, index) => <ResultSkeleton key={index} />)
              : results.map((school) => (
                  <SchoolCard
                    key={school.school_id}
                    compareDisabled={!compareIds.has(school.school_id) && compareIds.size >= compareLimit}
                    isCompared={compareIds.has(school.school_id)}
                    isSaved={savedIds.has(school.school_id)}
                    school={school}
                    onToggleCompare={toggleCompare}
                    onToggleSaved={toggleSaved}
                  />
                ))}
          </div>

          {!error && response && results.length > 0 ? (
            <Pagination
              currentPage={response.page}
              hasNext={response.has_next}
              totalPages={totalPages}
              onPageChange={(page) => updateFilter("page", page)}
            />
          ) : null}
        </section>
      </div>

      <CompareTray
        schools={selectedSchools}
        selectionLimit={compareLimit}
        selectedCount={compareIds.size}
        onClear={clearCompare}
      />
    </main>
  );
}

function PreferenceBanner({ profile }: { profile: PreferenceProfile }) {
  return (
    <div className="mb-4 rounded-lg border border-primary/20 bg-primary/10 p-4 text-primary">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-semibold">
            Using local preference profile: {profile.completion.percent}% complete
          </p>
          <p className="mt-1 text-xs leading-5">
            {profile.intended_major || "Undeclared"} - {profile.aid_importance || "aid not set"} - ranking integration arrives in V1.9.
          </p>
        </div>
        <Button asChild size="default" variant="secondary">
          <Link href="/onboarding">Edit profile</Link>
        </Button>
      </div>
    </div>
  );
}

type FilterPanelProps = {
  activeChips: ActiveChip[];
  filters: SearchFilters;
  onClearFilter: (key: keyof SearchFilters) => void;
  onReset: () => void;
  onUpdate: <TKey extends keyof SearchFilters>(key: TKey, value: SearchFilters[TKey]) => void;
};

function FilterPanel({ activeChips, filters, onClearFilter, onReset, onUpdate }: FilterPanelProps) {
  return (
    <FilterPanelShell
      title="Filters"
      description="Refine the search with structured fields already supported by the API."
      actions={<SlidersHorizontal className="h-5 w-5 text-muted-foreground" aria-hidden="true" />}
      className="h-fit lg:sticky lg:top-6"
    >
      <label className="block text-sm font-medium text-foreground">
        School name
        <div className="mt-2 flex h-11 items-center gap-2 rounded-md border border-border bg-white px-3">
          <Search className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
          <input
            className="min-w-0 flex-1 bg-transparent text-sm outline-none"
            placeholder="Adams, Bayview..."
            value={filters.query}
            onChange={(event) => onUpdate("query", event.target.value)}
          />
        </div>
      </label>

      <label className="block text-sm font-medium text-foreground">
        State
        <input
          className="mt-2 h-11 w-full rounded-md border border-border bg-white px-3 text-sm uppercase outline-none transition focus:border-primary"
          maxLength={2}
          placeholder="CA"
          value={filters.state}
          onChange={(event) => onUpdate("state", event.target.value.toUpperCase())}
        />
      </label>

      <label className="block text-sm font-medium text-foreground">
        School type
        <select
          className="mt-2 h-11 w-full rounded-md border border-border bg-white px-3 text-sm outline-none transition focus:border-primary"
          value={filters.type}
          onChange={(event) => onUpdate("type", event.target.value)}
        >
          <option value="">Any type</option>
          {schoolTypes.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
      </label>

      <label className="block text-sm font-medium text-foreground">
        Campus setting
        <select
          className="mt-2 h-11 w-full rounded-md border border-border bg-white px-3 text-sm outline-none transition focus:border-primary"
          value={filters.setting}
          onChange={(event) => onUpdate("setting", event.target.value)}
        >
          <option value="">Any setting</option>
          {settings.map((setting) => (
            <option key={setting} value={setting}>
              {setting}
            </option>
          ))}
        </select>
      </label>

      <label className="block text-sm font-medium text-foreground">
        Max net price
        <input
          className="mt-2 h-11 w-full rounded-md border border-border bg-white px-3 text-sm outline-none transition focus:border-primary"
          min={0}
          placeholder="30000"
          type="number"
          value={filters.maxNetPrice}
          onChange={(event) => onUpdate("maxNetPrice", event.target.value)}
        />
      </label>

      <label className="block text-sm font-medium text-foreground">
        Minimum graduation rate
        <div className="mt-2 flex items-center gap-3">
          <input
            className="h-2 flex-1 accent-primary"
            max={100}
            min={0}
            type="range"
            value={filters.minGraduationRate || "0"}
            onChange={(event) => onUpdate("minGraduationRate", event.target.value)}
          />
          <span className="w-10 text-right text-sm font-semibold">
            {filters.minGraduationRate || 0}%
          </span>
        </div>
      </label>

      {activeChips.length > 0 ? (
        <div className="space-y-3 border-t border-border pt-5">
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold text-foreground">Active filters</p>
            <button className="text-xs font-semibold text-primary" type="button" onClick={onReset}>
              Clear all
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {activeChips.map((chip) => (
              <button
                key={`${chip.key}-${chip.label}`}
                className="inline-flex items-center gap-1 rounded-md border border-border bg-muted px-2 py-1 text-xs font-semibold text-foreground"
                type="button"
                onClick={() => onClearFilter(chip.key)}
              >
                {chip.label}
                <X className="h-3 w-3" aria-hidden="true" />
              </button>
            ))}
          </div>
        </div>
      ) : null}
    </FilterPanelShell>
  );
}

type SchoolCardProps = {
  compareDisabled: boolean;
  isCompared: boolean;
  isSaved: boolean;
  school: SchoolSearchCard;
  onToggleCompare: (schoolId: number) => void;
  onToggleSaved: (schoolId: number) => void;
};

function SchoolCard({
  compareDisabled,
  isCompared,
  isSaved,
  onToggleCompare,
  onToggleSaved,
  school,
}: SchoolCardProps) {
  return (
    <Card className="flex min-h-[360px] flex-col">
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div>
            <Badge variant="outline">{school.type}</Badge>
            <CardTitle className="mt-3">
              <Link className="transition-colors hover:text-primary" href={`/schools/${school.school_id}`}>
                {school.name}
              </Link>
            </CardTitle>
            <p className="mt-1 text-sm text-muted-foreground">
              {school.city}, {school.state} - {school.setting}
            </p>
          </div>
          <ScorePill score={school.fit_score} label="Fit" />
        </div>
      </CardHeader>
      <CardContent className="flex flex-1 flex-col">
        <div className="space-y-3">
          <MetricRow label="Acceptance rate" value={formatPercent(school.acceptance_rate)} />
          <MetricRow label="Net price" value={formatCurrency(school.net_price)} />
          <MetricRow label="Enrollment" value={formatNumber(school.enrollment)} />
        </div>

        <div className="mt-5 flex-1 space-y-3 border-t border-border pt-5">
          <InsightList
            emptyText="Ranking reasons will appear after deterministic scoring is implemented."
            items={school.top_reasons.slice(0, 2)}
            title="Reasons"
          />
          <InsightList
            emptyText="No tradeoff has been computed yet."
            items={school.top_tradeoffs.slice(0, 1)}
            title="Tradeoff"
            warning
          />
        </div>

        <div className="mt-5 grid grid-cols-2 gap-2">
          <Button
            type="button"
            variant={isSaved ? "primary" : "secondary"}
            onClick={() => onToggleSaved(school.school_id)}
          >
            {isSaved ? <BookmarkCheck className="h-4 w-4" aria-hidden="true" /> : <Bookmark className="h-4 w-4" aria-hidden="true" />}
            {isSaved ? "Saved" : "Save"}
          </Button>
          <Button
            disabled={compareDisabled}
            type="button"
            variant={isCompared ? "primary" : "secondary"}
            onClick={() => onToggleCompare(school.school_id)}
          >
            <GitCompare className="h-4 w-4" aria-hidden="true" />
            {isCompared ? "Added" : "Compare"}
          </Button>
          <Button asChild className="col-span-2" variant="ghost">
            <Link href={`/schools/${school.school_id}`}>View profile</Link>
          </Button>
        </div>
      </CardContent>
    </Card>
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
      <p className="text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">{title}</p>
      {items.length > 0 ? (
        <ul className="mt-2 space-y-2 text-sm leading-6">
          {items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      ) : (
        <p
          className={cn(
            "mt-2 rounded-md p-3 text-sm leading-6",
            warning ? "bg-warning text-warning-foreground" : "bg-muted text-muted-foreground",
          )}
        >
          {emptyText}
        </p>
      )}
    </div>
  );
}

function SearchError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="mb-4 rounded-lg border border-border bg-white p-5">
      <div className="flex gap-3">
        <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-accent" aria-hidden="true" />
        <div>
          <p className="font-semibold text-foreground">Search failed</p>
          <p className="mt-1 text-sm leading-6 text-muted-foreground">{message}</p>
          <Button className="mt-4" type="button" variant="secondary" onClick={onRetry}>
            Retry
          </Button>
        </div>
      </div>
    </div>
  );
}

function Pagination({
  currentPage,
  hasNext,
  onPageChange,
  totalPages,
}: {
  currentPage: number;
  hasNext: boolean;
  onPageChange: (page: number) => void;
  totalPages: number;
}) {
  return (
    <div className="mt-6 flex items-center justify-between rounded-lg border border-border bg-white p-4">
      <Button
        disabled={currentPage <= 1}
        type="button"
        variant="secondary"
        onClick={() => onPageChange(currentPage - 1)}
      >
        <ChevronLeft className="h-4 w-4" aria-hidden="true" />
        Previous
      </Button>
      <span className="text-sm font-semibold text-foreground">
        Page {currentPage} of {totalPages}
      </span>
      <Button
        disabled={!hasNext}
        type="button"
        variant="secondary"
        onClick={() => onPageChange(currentPage + 1)}
      >
        Next
        <ChevronRight className="h-4 w-4" aria-hidden="true" />
      </Button>
    </div>
  );
}

function CompareTray({
  onClear,
  selectionLimit,
  schools,
  selectedCount,
}: {
  onClear: () => void;
  selectionLimit: number;
  schools: SchoolSearchCard[];
  selectedCount: number;
}) {
  if (selectedCount === 0) return null;

  return (
    <div className="fixed inset-x-0 bottom-0 z-20 border-t border-border bg-white/95 px-5 py-4 shadow-soft backdrop-blur">
      <div className="mx-auto flex max-w-7xl flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-semibold text-foreground">
            Compare tray: {selectedCount} selected
          </p>
          <p className="mt-1 text-xs text-muted-foreground">
            Select 2 to {selectionLimit} schools. Full comparison arrives in V1.11.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {schools.slice(0, 5).map((school) => (
            <Badge key={school.school_id} variant="outline">
              {school.name}
            </Badge>
          ))}
          <Button disabled={selectedCount < 2} asChild variant="primary">
            <Link href="/compare">Compare</Link>
          </Button>
          <Button type="button" variant="ghost" onClick={onClear}>
            Clear
          </Button>
        </div>
      </div>
    </div>
  );
}

function ResultSkeleton() {
  return (
    <Card className="min-h-[360px]">
      <CardHeader>
        <Skeleton className="h-6 w-20" />
        <Skeleton className="mt-4 h-8 w-4/5" />
        <Skeleton className="mt-2 h-4 w-2/3" />
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="space-y-3">
          <Skeleton className="h-5 w-full" />
          <Skeleton className="h-5 w-full" />
          <Skeleton className="h-5 w-full" />
        </div>
        <Skeleton className="h-20 w-full" />
        <div className="grid grid-cols-2 gap-2">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
        </div>
      </CardContent>
    </Card>
  );
}

function buildActiveChips(filters: SearchFilters): ActiveChip[] {
  const chips: ActiveChip[] = [];
  if (filters.query) chips.push({ key: "query", label: `Name: ${filters.query}` });
  if (filters.state) chips.push({ key: "state", label: `State: ${filters.state}` });
  if (filters.type) chips.push({ key: "type", label: filters.type });
  if (filters.setting) chips.push({ key: "setting", label: filters.setting });
  if (filters.maxNetPrice) chips.push({ key: "maxNetPrice", label: `Net price <= $${filters.maxNetPrice}` });
  if (filters.minGraduationRate) {
    chips.push({ key: "minGraduationRate", label: `Grad >= ${filters.minGraduationRate}%` });
  }
  return chips;
}

function formatPercent(value: number | null) {
  return value === null ? "Unknown" : `${Math.round(value * 100)}%`;
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
