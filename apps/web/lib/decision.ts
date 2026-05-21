"use client";

import { apiFetch } from "@/lib/api-client";
import { loadPreferenceProfile, toApiPreferenceProfile } from "@/lib/preferences";
import type { SavedSchoolEntry } from "@/lib/school-actions";
import type { DecisionOffer, DecisionReportResponse } from "@/types/api";

export const DECISION_OFFERS_STORAGE_KEY = "college-exploration.decision-offers.v1";

export type DecisionOfferDraft = Omit<DecisionOffer, "id" | "user_id" | "school_name" | "city" | "state">;

export function getDecisionCandidates(savedSchools: SavedSchoolEntry[]) {
  return savedSchools.filter((school) => school.status === "accepted" || school.status === "finalist");
}

export function defaultOfferForSchool(school: SavedSchoolEntry): DecisionOfferDraft {
  return {
    school_id: school.school_id,
    status: school.status === "finalist" ? "finalist" : "accepted",
    aid_offer: null,
    scholarships: null,
    estimated_yearly_cost: null,
    visit_notes: "",
    unresolved_concerns: [],
    parent_priority_notes: "",
    student_priority_notes: "",
  };
}

export function readDecisionOffers() {
  if (typeof window === "undefined") return [];
  try {
    const parsed = JSON.parse(window.localStorage.getItem(DECISION_OFFERS_STORAGE_KEY) ?? "[]") as unknown;
    return Array.isArray(parsed) ? parsed.flatMap(normalizeOfferDraft) : [];
  } catch {
    return [];
  }
}

export function writeDecisionOffers(offers: DecisionOfferDraft[]) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(DECISION_OFFERS_STORAGE_KEY, JSON.stringify(offers));
}

export function mergeOffersWithCandidates(candidates: SavedSchoolEntry[], offers: DecisionOfferDraft[]) {
  const bySchool = new Map(offers.map((offer) => [offer.school_id, offer]));
  return candidates.map((school) => ({
    ...defaultOfferForSchool(school),
    ...bySchool.get(school.school_id),
    status: school.status === "finalist" ? "finalist" as const : bySchool.get(school.school_id)?.status ?? "accepted" as const,
  }));
}

export async function syncDecisionOffer(offer: DecisionOfferDraft) {
  return apiFetch<DecisionOffer>("/decision/offers", {
    method: "POST",
    body: { user_id: 1, ...offer },
  });
}

export async function requestDecisionReport(offers: DecisionOfferDraft[]) {
  const profile = loadPreferenceProfile();
  const preferences = profile ? toApiPreferenceProfile(profile) : { weights: {}, constraints: {} };
  return apiFetch<DecisionReportResponse>("/decision/report", {
    method: "POST",
    body: {
      user_id: 1,
      school_ids: offers.map((offer) => offer.school_id),
      preferences,
      save_snapshot: false,
    },
  });
}

export function buildLocalDecisionReport(
  schools: SavedSchoolEntry[],
  offers: DecisionOfferDraft[],
): DecisionReportResponse {
  const offerBySchool = new Map(offers.map((offer) => [offer.school_id, offer]));
  const summaries = schools.map((school) => {
    const offer = offerBySchool.get(school.school_id) ?? defaultOfferForSchool(school);
    const fitScore = school.fit_score ?? profileCompletenessScore(school);
    const categoryScores = {
      academic: school.graduation_rate === null ? 50 : Math.round(school.graduation_rate * 100),
      cost: costScore(offer.estimated_yearly_cost ?? school.net_price),
      career: careerScore(school.median_earnings),
      campus: school.setting === "Urban" ? 72 : 65,
    };
    const confidenceFlags = [
      offer.estimated_yearly_cost === null ? "missing_financial_offer" : null,
      school.median_earnings === null ? "missing_outcomes_metrics" : null,
      school.fit_score === null ? "backend_fit_not_loaded" : null,
    ].filter((item): item is string => Boolean(item));

    return {
      school_id: school.school_id,
      name: school.name,
      status: offer.status,
      fit_score: fitScore,
      confidence_score: Math.max(0.35, 1 - confidenceFlags.length * 0.18),
      category_scores: categoryScores,
      estimated_yearly_cost: offer.estimated_yearly_cost,
      net_price: school.net_price,
      median_earnings: school.median_earnings ?? null,
      unresolved_concern_count: offer.unresolved_concerns.length,
      top_reasons: ["local_decision_workspace"],
      top_tradeoffs: confidenceFlags,
      confidence_flags: confidenceFlags,
    };
  }).sort((left, right) => right.fit_score - left.fit_score || left.school_id - right.school_id);

  const flags = [
    summaries.length < 2 ? "fewer_than_two_finalists" : null,
    summaries.some((school) => school.estimated_yearly_cost === null) ? "missing_financial_data" : null,
    summaries.some((school) => school.median_earnings === null) ? "missing_outcomes_metrics" : null,
  ].filter((item): item is string => Boolean(item));
  const bestFit = maxBy(summaries, (school) => school.fit_score);
  const bestValue = minBy(summaries, (school) => school.estimated_yearly_cost ?? school.net_price);
  const bestCareer = maxBy(summaries, (school) => school.category_scores.career);
  const lowestRisk = minBy(summaries, (school) => (school.estimated_yearly_cost ?? school.net_price ?? 999999) + school.unresolved_concern_count * 10000);
  const mostUnresolved = maxBy(summaries, (school) => school.unresolved_concern_count);

  return {
    report_version: "local-v1",
    ranking_version: "local",
    generated_at: new Date().toISOString(),
    disclaimer: "Decision summaries are planning support based on available data and your inputs. They are not admissions or financial advice.",
    decision_confidence: flags.length >= 2 || summaries.length < 2 ? "low" : flags.length === 1 ? "medium" : "high",
    confidence_flags: flags,
    schools: summaries,
    best_overall_fit: recommendation("Best overall fit", bestFit, "Highest available fit score in this finalist set."),
    best_value: recommendation("Best value", bestValue, "Lowest known yearly cost using entered offers before profile net price."),
    strongest_career_upside: recommendation("Strongest career upside", bestCareer, "Highest known career outcome signal."),
    lowest_risk: recommendation("Lowest risk", lowestRisk, "Lowest known cost with fewer unresolved concerns."),
    biggest_unresolved_factor: mostUnresolved && mostUnresolved.unresolved_concern_count > 0
      ? recommendation("Biggest unresolved factor", mostUnresolved, "Most unresolved questions entered in the workspace.")
      : { label: "Biggest unresolved factor", school_id: null, school_name: null, rationale: "No unresolved concerns have been entered yet." },
    major_tradeoffs: buildTradeoffs(bestFit, bestValue, bestCareer, lowestRisk, summaries),
    snapshot_id: null,
  };
}

function normalizeOfferDraft(value: unknown): DecisionOfferDraft[] {
  if (!value || typeof value !== "object" || Array.isArray(value)) return [];
  const item = value as Record<string, unknown>;
  if (!Number.isInteger(item.school_id)) return [];
  return [{
    school_id: item.school_id as number,
    status: item.status === "finalist" ? "finalist" : "accepted",
    aid_offer: nullableNumber(item.aid_offer),
    scholarships: nullableNumber(item.scholarships),
    estimated_yearly_cost: nullableNumber(item.estimated_yearly_cost),
    visit_notes: typeof item.visit_notes === "string" ? item.visit_notes : "",
    unresolved_concerns: Array.isArray(item.unresolved_concerns)
      ? item.unresolved_concerns.filter((entry): entry is string => typeof entry === "string")
      : [],
    parent_priority_notes: typeof item.parent_priority_notes === "string" ? item.parent_priority_notes : "",
    student_priority_notes: typeof item.student_priority_notes === "string" ? item.student_priority_notes : "",
  }];
}

function nullableNumber(value: unknown) {
  return typeof value === "number" && Number.isFinite(value) && value >= 0 ? value : null;
}

function profileCompletenessScore(school: SavedSchoolEntry) {
  const available = [school.net_price, school.graduation_rate, school.median_earnings].filter((value) => value !== null).length;
  return Math.round(50 + available * 12);
}

function costScore(value: number | null) {
  return value === null ? 50 : Math.max(25, Math.min(100, Math.round(100 - ((value - 15000) / 45000) * 75)));
}

function careerScore(value: number | null | undefined) {
  return value === null || value === undefined ? 50 : Math.max(25, Math.min(100, Math.round(45 + ((value - 40000) / 50000) * 55)));
}

function recommendation(label: string, school: DecisionReportResponse["schools"][number] | null, rationale: string) {
  return { label, school_id: school?.school_id ?? null, school_name: school?.name ?? null, rationale };
}

function buildTradeoffs(
  bestFit: DecisionReportResponse["schools"][number] | null,
  bestValue: DecisionReportResponse["schools"][number] | null,
  bestCareer: DecisionReportResponse["schools"][number] | null,
  lowestRisk: DecisionReportResponse["schools"][number] | null,
  summaries: DecisionReportResponse["schools"],
) {
  if (summaries.length < 2) return ["Add at least two accepted or finalist schools to generate side-by-side tradeoffs."];
  const tradeoffs: string[] = [];
  if (bestFit && bestValue && bestFit.school_id !== bestValue.school_id) {
    tradeoffs.push(`${bestFit.name} is your strongest overall fit, but ${bestValue.name} has the lower known cost.`);
  }
  if (bestCareer && lowestRisk && bestCareer.school_id !== lowestRisk.school_id) {
    tradeoffs.push(`${bestCareer.name} has the strongest career upside, while ${lowestRisk.name} is the safer current-data choice.`);
  }
  if (summaries.some((school) => school.estimated_yearly_cost === null)) {
    tradeoffs.push("At least one finalist is missing offer-level cost data, so value comparisons remain uncertain.");
  }
  return tradeoffs.length ? tradeoffs : ["The finalists are close on the currently available decision signals."];
}

function maxBy<T>(items: T[], selector: (item: T) => number | null | undefined) {
  return items.reduce<T | null>((best, item) => {
    const value = selector(item);
    if (value === null || value === undefined) return best;
    if (!best) return item;
    const bestValue = selector(best);
    return bestValue === null || bestValue === undefined || value > bestValue ? item : best;
  }, null);
}

function minBy<T>(items: T[], selector: (item: T) => number | null | undefined) {
  return items.reduce<T | null>((best, item) => {
    const value = selector(item);
    if (value === null || value === undefined) return best;
    if (!best) return item;
    const bestValue = selector(best);
    return bestValue === null || bestValue === undefined || value < bestValue ? item : best;
  }, null);
}
