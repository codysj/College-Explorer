"use client";

import { AlertCircle, Calculator, ClipboardList, ExternalLink, FileText, Save, ShieldCheck, Sparkles, Trophy } from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { trackAnalyticsEvent } from "@/lib/analytics";
import {
  buildLocalCostCalculator,
  defaultCostAssumption,
  requestCostCalculator,
  type CostCalculatorDraft,
} from "@/lib/cost-calculator";
import {
  buildLocalDecisionReport,
  defaultOfferForSchool,
  getDecisionCandidates,
  mergeOffersWithCandidates,
  readDecisionOffers,
  requestDecisionReport,
  syncDecisionOffer,
  writeDecisionOffers,
  writeDecisionReport,
  type DecisionOfferDraft,
} from "@/lib/decision";
import { getVisibleSavedSchools, useSchoolActionState, type SavedSchoolEntry } from "@/lib/school-actions";
import type { CostCalculatorResponse, DecisionReportResponse } from "@/types/api";

export function AcceptedSchoolsWorkspace() {
  const { savedSchools, updateSavedStatus } = useSchoolActionState();
  const [localStateReady, setLocalStateReady] = useState(false);
  const candidates = useMemo(() => getDecisionCandidates(getVisibleSavedSchools(savedSchools)), [savedSchools]);
  const [offers, setOffers] = useState<DecisionOfferDraft[]>([]);
  const [report, setReport] = useState<DecisionReportResponse | null>(null);
  const [costAssumptions, setCostAssumptions] = useState<CostCalculatorDraft[]>([]);
  const [costReport, setCostReport] = useState<CostCalculatorResponse | null>(null);
  const [familyBudget, setFamilyBudget] = useState<number | null>(null);
  const [saveState, setSaveState] = useState<string>("Local");

  useEffect(() => {
    setLocalStateReady(true);
  }, []);

  useEffect(() => {
    setOffers((current) => mergeOffersWithCandidates(candidates, current.length ? current : readDecisionOffers()));
  }, [candidates]);

  useEffect(() => {
    writeDecisionOffers(offers);
    if (candidates.length === 0) {
      setReport(null);
      return;
    }
    const candidateById = new Map(candidates.map((school) => [school.school_id, school]));
    const nextReport = buildLocalDecisionReport(candidates.filter((school) => candidateById.has(school.school_id)), offers);
    setReport(nextReport);
    writeDecisionReport(nextReport);
  }, [candidates, offers]);

  useEffect(() => {
    setCostAssumptions((current) => {
      const currentBySchool = new Map(current.map((item) => [item.school_id, item]));
      const offerBySchool = new Map(offers.map((offer) => [offer.school_id, offer]));
      return candidates.map((school) => ({
        ...defaultCostAssumption(school, offerBySchool.get(school.school_id)),
        ...currentBySchool.get(school.school_id),
      }));
    });
  }, [candidates, offers]);

  useEffect(() => {
    if (candidates.length === 0) {
      setCostReport(null);
      return;
    }
    setCostReport(buildLocalCostCalculator(candidates, costAssumptions, costAssumptions[0]?.school_id, familyBudget));
  }, [candidates, costAssumptions, familyBudget]);

  const updateOffer = (school: SavedSchoolEntry, patch: Partial<DecisionOfferDraft>) => {
    setOffers((current) => {
      const next = current.some((offer) => offer.school_id === school.school_id)
        ? current.map((offer) => offer.school_id === school.school_id ? { ...offer, ...patch } : offer)
        : [...current, { ...defaultOfferForSchool(school), ...patch }];
      return next;
    });
    if (patch.status) updateSavedStatus(school.school_id, patch.status);
  };

  const saveOffer = async (offer: DecisionOfferDraft) => {
    setSaveState("Saving");
    try {
      await syncDecisionOffer(offer);
      setSaveState("Saved to API");
    } catch {
      setSaveState("Saved locally");
    }
  };

  const generateReport = async () => {
    setSaveState("Generating");
    try {
      const payload = await requestDecisionReport(offers);
      setReport(payload);
      writeDecisionReport(payload);
      setSaveState("API report");
    } catch {
      const fallback = buildLocalDecisionReport(candidates, offers);
      setReport(fallback);
      writeDecisionReport(fallback);
      trackAnalyticsEvent({
        event_name: "decision_report_generated",
        entity_type: "decision_report",
        metadata: {
          source: "local_fallback",
          ranking_version: fallback.ranking_version,
          report_version: fallback.report_version,
          school_count: fallback.schools.length,
          decision_confidence: fallback.decision_confidence,
        },
      });
      setSaveState("Local report");
    }
  };

  const calculateCosts = async () => {
    setSaveState("Calculating");
    try {
      const payload = await requestCostCalculator(costAssumptions, costAssumptions[0]?.school_id, familyBudget);
      setCostReport(payload);
      setSaveState("API calculator");
    } catch {
      setCostReport(buildLocalCostCalculator(candidates, costAssumptions, costAssumptions[0]?.school_id, familyBudget));
      setSaveState("Local calculator");
    }
  };

  return (
    <main className="mx-auto min-h-screen w-full max-w-7xl px-5 pb-36 pt-8 sm:px-8">
      <header className="mb-8 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <Link className="text-sm font-semibold text-primary" href="/dashboard">
            Back to saved schools
          </Link>
          <h1 className="mt-3 text-3xl font-semibold tracking-normal text-foreground sm:text-4xl">
            Accepted schools
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">
            Compare admitted options using fit, known costs, career signals, notes, and explicit uncertainty.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <Badge variant={report?.decision_confidence === "high" ? "default" : "muted"}>
            Confidence: {report?.decision_confidence ?? "pending"}
          </Badge>
          <Badge variant="muted">{saveState}</Badge>
          <Button type="button" onClick={generateReport}>
            <FileText className="h-4 w-4" aria-hidden="true" />
            Generate summary
          </Button>
          <Button asChild variant="secondary">
            <Link href="/decision/report">
              <ExternalLink className="h-4 w-4" aria-hidden="true" />
              Open report
            </Link>
          </Button>
        </div>
      </header>

      {localStateReady && candidates.length === 0 ? (
        <EmptyState
          title="No admitted schools yet"
          description="Mark saved schools as accepted or finalist to start the decision workspace."
          action={<Link href="/dashboard">Review saved schools</Link>}
        />
      ) : null}

      {candidates.length > 0 ? (
        <div className="grid gap-6 xl:grid-cols-[minmax(0,1.35fr)_minmax(360px,0.65fr)]">
          <section className="space-y-4">
            <CostValueCalculator
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
            {candidates.map((school) => {
              const offer = offers.find((item) => item.school_id === school.school_id) ?? defaultOfferForSchool(school);
              return (
                <OfferCard
                  key={school.school_id}
                  offer={offer}
                  school={school}
                  onSave={saveOffer}
                  onUpdate={(patch) => updateOffer(school, patch)}
                />
              );
            })}
          </section>
          <DecisionSummaryPanel report={report} />
        </div>
      ) : null}
    </main>
  );
}

function CostValueCalculator({
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
          <h2 className="flex items-center gap-2 text-lg font-semibold text-foreground">
            <Calculator className="h-5 w-5 text-primary" aria-hidden="true" />
            Cost/value calculator
          </h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
            Enter offer assumptions, debt plans, and budget to compare estimated four-year cost, debt exposure, and directional value.
          </p>
        </div>
        <div className="flex flex-wrap items-end gap-3">
          <MoneyInput label="Family yearly budget" value={budget} onChange={onBudgetChange} />
          <Button type="button" onClick={onCalculate}>
            <Calculator className="h-4 w-4" aria-hidden="true" />
            Calculate
          </Button>
        </div>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        {assumptions.map((item) => {
          const result = costReport?.results.find((school) => school.school_id === item.school_id);
          return (
            <div key={item.school_id} className="rounded-md border border-border p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-semibold text-foreground">{result?.name ?? `School ${item.school_id}`}</p>
                  <p className="mt-1 text-xs text-muted-foreground">Confidence: {result?.confidence ?? "pending"}</p>
                </div>
                <Badge variant={result?.affordability.status === "within_budget" ? "default" : "muted"}>
                  {result?.affordability.status.replace("_", " ") ?? "estimate"}
                </Badge>
              </div>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <MoneyInput label="Tuition" value={item.tuition ?? null} onChange={(value) => onUpdate(item.school_id, { tuition: value })} />
                <MoneyInput label="Net price" value={item.estimated_net_price ?? null} onChange={(value) => onUpdate(item.school_id, { estimated_net_price: value })} />
                <MoneyInput label="Scholarships" value={item.scholarships ?? null} onChange={(value) => onUpdate(item.school_id, { scholarships: value })} />
                <MoneyInput label="Grants/aid" value={item.grants_aid ?? null} onChange={(value) => onUpdate(item.school_id, { grants_aid: value })} />
                <MoneyInput label="Yearly cost" value={item.estimated_yearly_cost ?? null} onChange={(value) => onUpdate(item.school_id, { estimated_yearly_cost: value })} />
                <MoneyInput label="Annual loans" value={item.annual_loan_amount ?? null} onChange={(value) => onUpdate(item.school_id, { annual_loan_amount: value })} />
              </div>
              <div className="mt-4 grid gap-2 text-sm text-muted-foreground sm:grid-cols-3">
                <span>Yearly {formatCurrency(result?.estimated_yearly_cost ?? null)}</span>
                <span>Four-year {formatCurrency(result?.estimated_four_year_total_cost ?? null)}</span>
                <span>Debt {formatCurrency(result?.estimated_debt_exposure ?? null)}</span>
              </div>
              {result?.repayment_scenarios.length ? (
                <div className="mt-3 grid gap-2 sm:grid-cols-3">
                  {result.repayment_scenarios.map((scenario) => (
                    <p key={scenario.scenario} className="rounded-md bg-muted p-2 text-xs leading-5 text-muted-foreground">
                      {scenario.scenario.replace("_", " ")}: {formatCurrency(scenario.estimated_monthly_payment)}/mo
                    </p>
                  ))}
                </div>
              ) : null}
              {result?.warnings.length ? (
                <p className="mt-3 rounded-md bg-muted p-3 text-xs leading-5 text-muted-foreground">
                  {result.warnings.join(", ")}
                </p>
              ) : null}
            </div>
          );
        })}
      </div>

      {costReport ? (
        <div className="mt-5 grid gap-3 md:grid-cols-2">
          {costReport.comparison_summary.map((item) => (
            <p key={item} className="rounded-md bg-muted p-3 text-sm leading-6 text-muted-foreground">{item}</p>
          ))}
          <p className="rounded-md bg-muted p-3 text-sm leading-6 text-muted-foreground">{costReport.disclaimer}</p>
        </div>
      ) : null}
    </section>
  );
}

function OfferCard({
  offer,
  onSave,
  onUpdate,
  school,
}: {
  offer: DecisionOfferDraft;
  onSave: (offer: DecisionOfferDraft) => void;
  onUpdate: (patch: Partial<DecisionOfferDraft>) => void;
  school: SavedSchoolEntry;
}) {
  return (
    <Card>
      <CardHeader className="p-5 pb-3">
        <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div>
            <CardTitle className="text-lg">
              <Link className="transition-colors hover:text-primary" href={`/schools/${school.school_id}`}>
                {school.name}
              </Link>
            </CardTitle>
            <p className="mt-1 text-sm text-muted-foreground">{school.city}, {school.state} - {school.setting}</p>
          </div>
          <select
            aria-label={`Decision status for ${school.name}`}
            className="h-10 rounded-md border border-border bg-white px-3 text-sm font-medium outline-none transition focus:border-primary"
            value={offer.status}
            onChange={(event) => onUpdate({ status: event.target.value as DecisionOfferDraft["status"] })}
          >
            <option value="accepted">Accepted</option>
            <option value="finalist">Finalist</option>
          </select>
        </div>
      </CardHeader>
      <CardContent className="grid gap-4 p-5 pt-2">
        <div className="grid gap-3 md:grid-cols-3">
          <MoneyInput label="Aid offer" value={offer.aid_offer} onChange={(value) => onUpdate({ aid_offer: value })} />
          <MoneyInput label="Scholarships" value={offer.scholarships} onChange={(value) => onUpdate({ scholarships: value })} />
          <MoneyInput label="Estimated yearly cost" value={offer.estimated_yearly_cost} onChange={(value) => onUpdate({ estimated_yearly_cost: value })} />
        </div>
        <div className="grid gap-3 md:grid-cols-2">
          <TextArea label="Visit notes" value={offer.visit_notes ?? ""} onChange={(value) => onUpdate({ visit_notes: value })} />
          <TextArea
            label="Unresolved concerns/questions"
            value={offer.unresolved_concerns.join("\n")}
            onChange={(value) => onUpdate({ unresolved_concerns: value.split("\n").map((line) => line.trim()).filter(Boolean) })}
          />
          <TextArea label="Parent priority notes" value={offer.parent_priority_notes ?? ""} onChange={(value) => onUpdate({ parent_priority_notes: value })} />
          <TextArea label="Student priority notes" value={offer.student_priority_notes ?? ""} onChange={(value) => onUpdate({ student_priority_notes: value })} />
        </div>
        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border pt-4">
          <div className="grid gap-2 text-sm text-muted-foreground sm:grid-cols-3">
            <span>Profile net price: {formatCurrency(school.net_price)}</span>
            <span>Graduation: {formatPercent(school.graduation_rate)}</span>
            <span>Earnings: {formatCurrency(school.median_earnings ?? null)}</span>
          </div>
          <Button type="button" variant="secondary" onClick={() => onSave(offer)}>
            <Save className="h-4 w-4" aria-hidden="true" />
            Save offer
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function DecisionSummaryPanel({ report }: { report: DecisionReportResponse | null }) {
  if (!report) return null;
  const recommendations = [
    report.best_overall_fit,
    report.best_value,
    report.strongest_career_upside,
    report.lowest_risk,
    report.biggest_unresolved_factor,
  ];

  return (
    <aside className="space-y-4">
      <section className="rounded-lg border border-border bg-white p-5 shadow-soft">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-foreground">Decision summary</h2>
          <ClipboardList className="h-5 w-5 text-primary" aria-hidden="true" />
        </div>
        <p className="mt-3 text-sm leading-6 text-muted-foreground">{report.disclaimer}</p>
        {report.confidence_flags.length > 0 ? (
          <div className="mt-4 rounded-md bg-muted p-3 text-sm text-muted-foreground">
            {report.confidence_flags.join(", ")}
          </div>
        ) : null}
      </section>

      <section className="grid gap-3">
        {recommendations.map((item) => (
          <Card key={item.label} className="shadow-none">
            <CardHeader className="p-4 pb-2">
              <CardTitle className="flex items-center gap-2 text-base">
                {item.label === "Lowest risk" ? <ShieldCheck className="h-4 w-4 text-primary" /> : <Trophy className="h-4 w-4 text-primary" />}
                {item.label}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-4 pt-1">
              <p className="font-semibold text-foreground">{item.school_name ?? "Not enough data"}</p>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">{item.rationale}</p>
            </CardContent>
          </Card>
        ))}
      </section>

      <section className="rounded-lg border border-border bg-white p-5 shadow-soft">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-foreground">
          <AlertCircle className="h-5 w-5 text-accent" aria-hidden="true" />
          Major tradeoffs
        </h2>
        <div className="mt-4 space-y-3">
          {report.major_tradeoffs.map((tradeoff) => (
            <p key={tradeoff} className="rounded-md bg-muted p-3 text-sm leading-6 text-muted-foreground">
              {tradeoff}
            </p>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-border bg-white p-5 shadow-soft">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-foreground">
          <Sparkles className="h-5 w-5 text-primary" aria-hidden="true" />
          Finalist comparison
        </h2>
        <div className="mt-4 space-y-3">
          {report.schools.map((school) => (
            <div key={school.school_id} className="rounded-md border border-border p-3">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-foreground">{school.name}</p>
                <Badge variant={school.status === "finalist" ? "default" : "muted"}>{school.status}</Badge>
              </div>
              <div className="mt-3 grid grid-cols-3 gap-2 text-xs text-muted-foreground">
                <span>Fit {Math.round(school.fit_score)}</span>
                <span>Cost {formatCurrency(school.estimated_yearly_cost ?? school.net_price)}</span>
                <span>Career {Math.round(school.category_scores.career ?? 50)}</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </aside>
  );
}

function MoneyInput({ label, onChange, value }: { label: string; onChange: (value: number | null) => void; value: number | null }) {
  return (
    <label className="block">
      <span className="text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">{label}</span>
      <input
        className="mt-1 h-10 w-full rounded-md border border-border bg-white px-3 text-sm outline-none transition focus:border-primary"
        inputMode="numeric"
        min={0}
        type="number"
        value={value ?? ""}
        onChange={(event) => onChange(event.target.value ? Number(event.target.value) : null)}
      />
    </label>
  );
}

function TextArea({ label, onChange, value }: { label: string; onChange: (value: string) => void; value: string }) {
  return (
    <label className="block">
      <span className="text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">{label}</span>
      <textarea
        className="mt-1 min-h-24 w-full resize-y rounded-md border border-border bg-white px-3 py-2 text-sm leading-6 outline-none transition focus:border-primary"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function formatCurrency(value: number | null) {
  return value === null ? "Unknown" : new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);
}

function formatPercent(value: number | null | undefined) {
  return value === null || value === undefined ? "Unknown" : `${Math.round(value * 100)}%`;
}
