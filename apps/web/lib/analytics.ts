"use client";

import { apiFetch } from "@/lib/api-client";
import type { AnalyticsSummaryResponse } from "@/types/api";

type AnalyticsEventName =
  | "search_performed"
  | "semantic_search_performed"
  | "school_profile_viewed"
  | "school_saved"
  | "school_compared"
  | "onboarding_completed"
  | "ranking_generated"
  | "sensitivity_adjusted"
  | "decision_report_generated";

type AnalyticsEventPayload = {
  user_id?: number | null;
  event_name: AnalyticsEventName;
  entity_type?: string | null;
  entity_id?: number | null;
  metadata?: Record<string, unknown>;
};

const sensitiveKeys = new Set([
  "aid_offer",
  "scholarships",
  "estimated_yearly_cost",
  "annual_loan_amount",
  "visit_notes",
  "unresolved_concerns",
  "parent_priority_notes",
  "student_priority_notes",
  "email",
  "query",
  "raw_query",
  "intended_major",
  "home_state",
  "max_annual_cost",
]);

export function trackAnalyticsEvent(payload: AnalyticsEventPayload) {
  if (typeof window === "undefined") return;
  const body = {
    user_id: payload.user_id ?? null,
    event_name: payload.event_name,
    entity_type: payload.entity_type ?? null,
    entity_id: payload.entity_id ?? null,
    metadata: sanitizeMetadata(payload.metadata ?? {}),
  };
  void apiFetch("/analytics/events", { method: "POST", body }).catch(() => undefined);
}

/**
 * The analytics summary is operator-facing, so the backend gates it behind
 * ANALYTICS_API_TOKEN outside development. The token is entered by the operator and kept
 * in localStorage rather than bundled as NEXT_PUBLIC_*, which would ship it to everyone.
 */
export const ANALYTICS_TOKEN_STORAGE_KEY = "college-exploration.analytics-token.v1";

export function loadAnalyticsToken() {
  if (typeof window === "undefined") return "";
  try {
    return window.localStorage.getItem(ANALYTICS_TOKEN_STORAGE_KEY) ?? "";
  } catch {
    return "";
  }
}

export function saveAnalyticsToken(token: string) {
  try {
    if (token.trim()) {
      window.localStorage.setItem(ANALYTICS_TOKEN_STORAGE_KEY, token.trim());
    } else {
      window.localStorage.removeItem(ANALYTICS_TOKEN_STORAGE_KEY);
    }
  } catch {
    // A browser with storage disabled just means the token must be re-entered.
  }
}

export function fetchAnalyticsSummary(lookbackDays = 90) {
  const token = loadAnalyticsToken();
  return apiFetch<AnalyticsSummaryResponse>(`/analytics/summary?lookback_days=${lookbackDays}` as `/${string}`, {
    headers: token ? { "X-Analytics-Token": token } : undefined,
  });
}

function sanitizeMetadata(metadata: Record<string, unknown>) {
  return Object.entries(metadata).reduce<Record<string, unknown>>((safe, [key, value]) => {
    if (sensitiveKeys.has(key)) return safe;
    if (value === undefined) return safe;
    safe[key] = value;
    return safe;
  }, {});
}
