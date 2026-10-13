"use client";

import { apiFetch } from "@/lib/api-client";
import type { DecisionOfferDraft } from "@/lib/decision";
import type { SavedSchoolEntry, SchoolSnapshot } from "@/lib/school-actions";
import type { CostCalculatorAssumption, CostCalculatorResponse, SchoolProfile } from "@/types/api";

export type CostCalculatorDraft = CostCalculatorAssumption;

export function defaultCostAssumption(
  school: SavedSchoolEntry | SchoolSnapshot | SchoolProfile,
  offer?: DecisionOfferDraft,
): CostCalculatorDraft {
  const profile = school as SchoolProfile;
  const snapshot = school as SchoolSnapshot;
  return {
    school_id: school.school_id,
    tuition: profile.cost?.tuition_out_state ?? null,
    estimated_net_price: profile.cost?.net_price ?? snapshot.net_price ?? null,
    scholarships: offer?.scholarships ?? null,
    grants_aid: offer?.aid_offer ?? null,
    estimated_yearly_cost: offer?.estimated_yearly_cost ?? null,
    annual_loan_amount: null,
    loan_interest_rate: 0.055,
    loan_term_years: 10,
  };
}

export async function requestCostCalculator(
  assumptions: CostCalculatorDraft[],
  baselineSchoolId?: number,
  budget?: number | null,
) {
  return apiFetch<CostCalculatorResponse>("/cost-calculator", {
    method: "POST",
    body: {
      schools: assumptions,
      baseline_school_id: baselineSchoolId ?? assumptions[0]?.school_id,
      max_annual_family_budget: budget ?? null,
    },
  });
}
