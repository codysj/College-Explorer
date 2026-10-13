"use client";

import { apiFetch } from "@/lib/api-client";
import { loadPreferenceProfile, toApiPreferenceProfile } from "@/lib/preferences";
import type { SavedSchoolEntry } from "@/lib/school-actions";
import type { DecisionReportResponse } from "@/types/api";

export const DECISION_OFFERS_STORAGE_KEY = "college-exploration.decision-offers.v1";
export const DECISION_REPORT_STORAGE_KEY = "college-exploration.decision-report.v1";

export type DecisionOfferDraft = {
  school_id: number;
  status: "accepted" | "finalist";
  aid_offer: number | null;
  scholarships: number | null;
  estimated_yearly_cost: number | null;
  visit_notes: string | null;
  unresolved_concerns: string[];
  parent_priority_notes: string | null;
  student_priority_notes: string | null;
};

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
  writeStorage(DECISION_OFFERS_STORAGE_KEY, offers);
}

export function readDecisionReport() {
  if (typeof window === "undefined") return null;
  try {
    const parsed = JSON.parse(window.localStorage.getItem(DECISION_REPORT_STORAGE_KEY) ?? "null") as DecisionReportResponse | null;
    return parsed
      && Array.isArray(parsed.schools)
      && Array.isArray(parsed.finalist_ranking_table)
      && Array.isArray(parsed.cost_value_comparison)
      && Array.isArray(parsed.sensitivity_highlights)
      && Array.isArray(parsed.unresolved_questions)
      ? parsed
      : null;
  } catch {
    return null;
  }
}

export function writeDecisionReport(report: DecisionReportResponse | null) {
  if (report) writeStorage(DECISION_REPORT_STORAGE_KEY, report);
}

// Storage can throw (Safari private mode, quota). Losing a write is better than crashing the page.
function writeStorage(key: string, value: unknown) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // ignore
  }
}

export function mergeOffersWithCandidates(candidates: SavedSchoolEntry[], offers: DecisionOfferDraft[]) {
  const bySchool = new Map(offers.map((offer) => [offer.school_id, offer]));
  return candidates.map((school) => ({
    ...defaultOfferForSchool(school),
    ...bySchool.get(school.school_id),
    status: school.status === "finalist" ? "finalist" as const : bySchool.get(school.school_id)?.status ?? "accepted" as const,
  }));
}

export async function requestDecisionReport(offers: DecisionOfferDraft[]) {
  const profile = loadPreferenceProfile();
  const preferences = profile ? toApiPreferenceProfile(profile) : { weights: {}, constraints: {} };
  return apiFetch<DecisionReportResponse>("/decision/report", {
    method: "POST",
    // Offers, including any notes, stay in this browser; only the numbers the report needs are sent.
    body: {
      offers: offers.map(({ school_id, status, aid_offer, scholarships, estimated_yearly_cost, unresolved_concerns }) => ({
        school_id, status, aid_offer, scholarships, estimated_yearly_cost, unresolved_concerns,
      })),
      preferences,
      max_annual_family_budget: profile?.max_annual_cost ?? null,
    },
  });
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
