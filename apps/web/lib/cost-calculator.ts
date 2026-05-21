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

export function buildLocalCostCalculator(
  schools: Array<SavedSchoolEntry | SchoolProfile>,
  assumptions: CostCalculatorDraft[],
  baselineSchoolId?: number,
  budget?: number | null,
): CostCalculatorResponse {
  const assumptionBySchool = new Map(assumptions.map((item) => [item.school_id, item]));
  const baseline = baselineSchoolId ?? schools[0]?.school_id ?? null;
  const baselineCost = baseline ? yearlyCost(assumptionBySchool.get(baseline), findSchool(schools, baseline)) : null;
  const results = schools.map((school) => {
    const assumption = assumptionBySchool.get(school.school_id) ?? defaultCostAssumption(school);
    const cost = yearlyCost(assumption, school);
    const difference = cost !== null && baselineCost !== null ? cost - baselineCost : null;
    const debtExposure = assumption.annual_loan_amount !== null && assumption.annual_loan_amount !== undefined
      ? assumption.annual_loan_amount * 4
      : profileDebt(school);
    const warnings = [
      cost === null ? "missing_aid_or_net_price" : null,
      medianEarnings(school) === null || graduationRate(school) === null ? "missing_outcomes_data" : null,
      assumption.annual_loan_amount === null || assumption.annual_loan_amount === undefined ? "missing_or_observed_debt_assumption" : null,
    ].filter((item): item is string => Boolean(item));

    return {
      school_id: school.school_id,
      name: school.name,
      city: school.city,
      state: school.state,
      observed_cost_data: {
        tuition_in_state: profileCost(school, "tuition_in_state"),
        tuition_out_state: profileCost(school, "tuition_out_state"),
        net_price: profileCost(school, "net_price") ?? snapshotNetPrice(school),
        average_aid: profileCost(school, "average_aid"),
        debt_median: profileDebt(school),
      },
      observed_outcome_data: {
        median_earnings: medianEarnings(school),
        graduation_rate: graduationRate(school),
        repayment_rate: (school as SchoolProfile).outcomes?.repayment_rate ?? null,
      },
      assumptions: assumption,
      estimated_yearly_cost: cost,
      estimated_four_year_total_cost: cost === null ? null : cost * 4,
      yearly_cost_difference: difference,
      four_year_cost_difference: difference === null ? null : difference * 4,
      estimated_debt_exposure: debtExposure,
      repayment_scenarios: debtExposure === null ? [] : repaymentScenarios(debtExposure, assumption.loan_interest_rate ?? 0.055, assumption.loan_term_years ?? 10),
      directional_outcome_adjusted_value: directionalValue(cost === null ? null : cost * 4, school),
      affordability: affordability(cost, budget),
      confidence: cost === null || warnings.length >= 2 ? "low" as const : warnings.length ? "medium" as const : "high" as const,
      warnings,
      formulas: [
        "estimated_yearly_cost = entered yearly cost, or known price minus scholarships and grants/aid",
        "estimated_four_year_total_cost = estimated_yearly_cost * 4",
        "estimated_debt_exposure = annual loan amount * 4 when entered; otherwise observed median debt if available",
      ],
    };
  });

  return {
    calculator_version: "local-v1",
    generated_at: new Date().toISOString(),
    disclaimer: "Cost/value calculator outputs are estimates for planning only, not financial advice. Actual aid, costs, borrowing terms, repayment, and outcomes may vary.",
    baseline_school_id: baseline,
    results,
    comparison_summary: comparisonSummary(results, baseline),
  };
}

function yearlyCost(assumption: CostCalculatorDraft | undefined, school?: SavedSchoolEntry | SchoolProfile) {
  if (!assumption) return null;
  if (assumption.estimated_yearly_cost !== null && assumption.estimated_yearly_cost !== undefined) return assumption.estimated_yearly_cost;
  const base = assumption.estimated_net_price ?? assumption.tuition ?? (school ? profileCost(school, "net_price") ?? snapshotNetPrice(school) : null);
  return base === null ? null : Math.max(0, base - (assumption.scholarships ?? 0) - (assumption.grants_aid ?? 0));
}

function repaymentScenarios(principal: number, rate: number, years: number) {
  return [
    { scenario: "lower_debt" as const, principal: Math.max(0, principal - 10000), interest_rate: rate, term_years: years, assumption: "Total borrowed is $10,000 lower." },
    { scenario: "base" as const, principal, interest_rate: rate, term_years: years, assumption: "Total borrowed matches the current assumption." },
    { scenario: "higher_debt" as const, principal: principal + 10000, interest_rate: rate, term_years: years, assumption: "Total borrowed is $10,000 higher." },
  ].map((item) => {
    const payment = monthlyPayment(item.principal, rate, years);
    return { ...item, estimated_monthly_payment: payment, estimated_total_repaid: payment * years * 12 };
  });
}

function monthlyPayment(principal: number, annualRate: number, years: number) {
  if (principal <= 0) return 0;
  const months = years * 12;
  const monthlyRate = annualRate / 12;
  if (monthlyRate === 0) return Math.round(principal / months);
  return Math.round(principal * (monthlyRate * (1 + monthlyRate) ** months) / ((1 + monthlyRate) ** months - 1));
}

function affordability(cost: number | null, budget?: number | null) {
  if (cost === null || budget === null || budget === undefined) return { status: "unknown" as const, message: "Add a family budget to evaluate affordability." };
  if (cost <= budget) return { status: "within_budget" as const, message: "Estimated yearly cost is within budget." };
  if (cost <= budget * 1.15) return { status: "near_budget" as const, message: "Estimated yearly cost is near budget." };
  return { status: "above_budget" as const, message: "Estimated yearly cost is above budget." };
}

function directionalValue(fourYearCost: number | null, school: SavedSchoolEntry | SchoolProfile) {
  const earnings = medianEarnings(school);
  const graduation = graduationRate(school);
  if (fourYearCost === null || earnings === null || graduation === null) return "uncertain" as const;
  const ratio = fourYearCost / Math.max(earnings, 1);
  if (ratio <= 1.7 && graduation >= 0.75) return "stronger_value" as const;
  if (ratio <= 2.6 && graduation >= 0.6) return "reasonable_value" as const;
  return "higher_cost_tradeoff" as const;
}

function comparisonSummary(results: CostCalculatorResponse["results"], baselineId: number | null) {
  if (results.length < 2) return ["Add at least two schools to compare cost differences."];
  const baseline = results.find((item) => item.school_id === baselineId);
  if (!baseline) return ["Choose a baseline school to summarize cost differences."];
  return results
    .filter((item) => item.school_id !== baseline.school_id && item.four_year_cost_difference !== null)
    .map((item) => `${item.name} may cost about ${formatCurrency(Math.abs(item.four_year_cost_difference ?? 0))} ${item.four_year_cost_difference && item.four_year_cost_difference > 0 ? "more" : "less"} over four years than ${baseline.name} under current assumptions.`);
}

function findSchool(schools: Array<SavedSchoolEntry | SchoolProfile>, schoolId: number) {
  return schools.find((school) => school.school_id === schoolId);
}

function profileCost(school: SavedSchoolEntry | SchoolProfile, key: keyof SchoolProfile["cost"]) {
  return (school as SchoolProfile).cost?.[key] ?? null;
}

function snapshotNetPrice(school: SavedSchoolEntry | SchoolProfile) {
  return "net_price" in school ? school.net_price : null;
}

function profileDebt(school: SavedSchoolEntry | SchoolProfile) {
  return (school as SchoolProfile).cost?.debt_median ?? null;
}

function medianEarnings(school: SavedSchoolEntry | SchoolProfile) {
  return (school as SchoolProfile).outcomes?.median_earnings ?? ("median_earnings" in school ? school.median_earnings ?? null : null);
}

function graduationRate(school: SavedSchoolEntry | SchoolProfile) {
  return (school as SchoolProfile).academics?.graduation_rate ?? ("graduation_rate" in school ? school.graduation_rate : null);
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);
}
