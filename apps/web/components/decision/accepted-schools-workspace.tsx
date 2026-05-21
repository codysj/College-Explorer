"use client";

import { AlertCircle, ClipboardList, FileText, Save, ShieldCheck, Sparkles, Trophy } from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import {
  buildLocalDecisionReport,
  defaultOfferForSchool,
  getDecisionCandidates,
  mergeOffersWithCandidates,
  readDecisionOffers,
  requestDecisionReport,
  syncDecisionOffer,
  writeDecisionOffers,
  type DecisionOfferDraft,
} from "@/lib/decision";
import { getVisibleSavedSchools, useSchoolActionState, type SavedSchoolEntry } from "@/lib/school-actions";
import type { DecisionReportResponse } from "@/types/api";

export function AcceptedSchoolsWorkspace() {
  const { savedSchools, updateSavedStatus } = useSchoolActionState();
  const [localStateReady, setLocalStateReady] = useState(false);
  const candidates = useMemo(() => getDecisionCandidates(getVisibleSavedSchools(savedSchools)), [savedSchools]);
  const [offers, setOffers] = useState<DecisionOfferDraft[]>([]);
  const [report, setReport] = useState<DecisionReportResponse | null>(null);
  const [saveState, setSaveState] = useState<string>("Local");

  useEffect(() => {
    setLocalStateReady(true);
  }, []);

  useEffect(() => {
    setOffers((current) => mergeOffersWithCandidates(candidates, current.length ? current : readDecisionOffers()));
  }, [candidates]);

  useEffect(() => {
    writeDecisionOffers(offers);
    const candidateById = new Map(candidates.map((school) => [school.school_id, school]));
    setReport(buildLocalDecisionReport(candidates.filter((school) => candidateById.has(school.school_id)), offers));
  }, [candidates, offers]);

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
      setSaveState("API report");
    } catch {
      setReport(buildLocalDecisionReport(candidates, offers));
      setSaveState("Local report");
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
