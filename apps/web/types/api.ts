export type SchoolSearchCard = {
  school_id: number;
  name: string;
  city: string;
  state: string;
  type: string;
  setting: string;
  enrollment: number | null;
  acceptance_rate: number | null;
  net_price: number | null;
  graduation_rate: number | null;
  fit_score: number | null;
  confidence_score: number | null;
  top_reasons: string[];
  top_tradeoffs: string[];
  category_scores?: Record<string, number>;
  ranking_version?: string | null;
};

export type SchoolSearchResponse = {
  results: SchoolSearchCard[];
  page: number;
  page_size: number;
  total_results: number;
  has_next: boolean;
};

export type SchoolProfile = {
  school_id: number;
  name: string;
  city: string;
  state: string;
  region: string;
  type: string;
  setting: string;
  enrollment: number | null;
  acceptance_rate: number | null;
  academics: {
    majors: string[] | null;
    popular_majors: string[] | null;
    graduation_rate: number | null;
    retention_rate: number | null;
    student_faculty_ratio: number | null;
  };
  cost: {
    tuition_in_state: number | null;
    tuition_out_state: number | null;
    net_price: number | null;
    average_aid: number | null;
    debt_median: number | null;
  };
  outcomes: {
    median_earnings: number | null;
    completion_rate: number | null;
    repayment_rate: number | null;
    outcome_percentiles: Record<string, number> | null;
  };
  campus_life: {
    sports: string | null;
    greek_life: number | null;
    housing: boolean | null;
    weather_band: string | null;
    diversity_metrics: Record<string, number> | null;
    culture_tags: string[] | null;
  };
  data_fields_missing: string[];
  data_confidence_score: number;
  fit_score: number | null;
  category_scores: Record<string, number>;
  top_reasons: string[];
  top_tradeoffs: string[];
  similar_schools: Array<Record<string, unknown>>;
  ranking_version?: string | null;
};

export type SimilarSchoolVariant =
  | "general"
  | "cheaper"
  | "less_selective"
  | "smaller"
  | "stronger_outcomes"
  | "closer_to_home";

export type SimilarSchoolCard = {
  school_id: number;
  name: string;
  city: string;
  state: string;
  type: string;
  setting: string;
  enrollment: number | null;
  acceptance_rate: number | null;
  net_price: number | null;
  graduation_rate: number | null;
  median_earnings: number | null;
  similarity_score: number;
  fit_score: number | null;
  top_reasons: string[];
  top_tradeoffs: string[];
  variant_applied: SimilarSchoolVariant;
  ranking_version: string;
};

export type SimilarSchoolsResponse = {
  source_school_id: number;
  variant: SimilarSchoolVariant;
  variant_applied: SimilarSchoolVariant;
  ranking_version: string;
  embedding_model: string;
  embedding_type: string;
  retrieval_mode: string;
  results: SimilarSchoolCard[];
  page: number;
  page_size: number;
  total_results: number;
  has_next: boolean;
};

export type DecisionOffer = {
  id?: number;
  user_id: number;
  school_id: number;
  school_name?: string;
  city?: string;
  state?: string;
  status: "accepted" | "finalist";
  aid_offer: number | null;
  scholarships: number | null;
  estimated_yearly_cost: number | null;
  visit_notes: string | null;
  unresolved_concerns: string[];
  parent_priority_notes: string | null;
  student_priority_notes: string | null;
};

export type DecisionSchoolSummary = {
  school_id: number;
  name: string;
  status: "accepted" | "finalist";
  fit_score: number;
  confidence_score: number;
  category_scores: Record<string, number>;
  estimated_yearly_cost: number | null;
  net_price: number | null;
  median_earnings: number | null;
  unresolved_concern_count: number;
  top_reasons: string[];
  top_tradeoffs: string[];
  confidence_flags: string[];
};

export type DecisionRecommendation = {
  label: string;
  school_id: number | null;
  school_name: string | null;
  rationale: string;
};

export type DecisionReportResponse = {
  report_version: string;
  ranking_version: string;
  generated_at: string;
  disclaimer: string;
  decision_confidence: "low" | "medium" | "high";
  confidence_flags: string[];
  schools: DecisionSchoolSummary[];
  best_overall_fit: DecisionRecommendation;
  best_value: DecisionRecommendation;
  strongest_career_upside: DecisionRecommendation;
  lowest_risk: DecisionRecommendation;
  biggest_unresolved_factor: DecisionRecommendation;
  major_tradeoffs: string[];
  snapshot_id: number | null;
};

export type CostCalculatorAssumption = {
  school_id: number;
  tuition?: number | null;
  estimated_net_price?: number | null;
  scholarships?: number | null;
  grants_aid?: number | null;
  estimated_yearly_cost?: number | null;
  annual_loan_amount?: number | null;
  loan_interest_rate?: number;
  loan_term_years?: number;
};

export type CostCalculatorResult = {
  school_id: number;
  name: string;
  city: string;
  state: string;
  observed_cost_data: {
    tuition_in_state: number | null;
    tuition_out_state: number | null;
    net_price: number | null;
    average_aid: number | null;
    debt_median: number | null;
  };
  observed_outcome_data: {
    median_earnings: number | null;
    graduation_rate: number | null;
    repayment_rate: number | null;
  };
  assumptions: CostCalculatorAssumption;
  estimated_yearly_cost: number | null;
  estimated_four_year_total_cost: number | null;
  yearly_cost_difference: number | null;
  four_year_cost_difference: number | null;
  estimated_debt_exposure: number | null;
  repayment_scenarios: Array<{
    scenario: "base" | "lower_debt" | "higher_debt";
    principal: number;
    interest_rate: number;
    term_years: number;
    estimated_monthly_payment: number;
    estimated_total_repaid: number;
    assumption: string;
  }>;
  directional_outcome_adjusted_value: "stronger_value" | "reasonable_value" | "higher_cost_tradeoff" | "uncertain";
  affordability: {
    status: "within_budget" | "near_budget" | "above_budget" | "unknown";
    message: string;
  };
  confidence: "low" | "medium" | "high";
  warnings: string[];
  formulas: string[];
};

export type CostCalculatorResponse = {
  calculator_version: string;
  generated_at: string;
  disclaimer: string;
  baseline_school_id: number | null;
  results: CostCalculatorResult[];
  comparison_summary: string[];
};

export type SensitivityMovement = {
  school_id: number;
  name: string;
  city: string;
  state: string;
  base_rank: number | null;
  scenario_rank: number | null;
  rank_delta: number | null;
  fit_score: number;
  fit_delta: number;
  confidence_score: number;
  confidence_delta: number;
  category_scores: Record<string, number>;
  category_drivers: string[];
  movement: "up" | "down" | "stable" | "new" | "removed";
  stability: "stable_choice" | "volatile_choice" | "watch_choice";
  top_reasons: string[];
  top_tradeoffs: string[];
  explanation: string;
};

export type SensitivityScenarioResult = {
  scenario_id: string;
  label: string;
  applied_weights: Record<string, number>;
  emphasis_dimension: string | null;
  results: SensitivityMovement[];
  summary: string;
};

export type SensitivityChoiceSummary = {
  school_id: number;
  name: string;
  base_rank: number | null;
  average_rank: number;
  max_rank_delta: number;
  max_fit_delta: number;
  explanation: string;
};

export type SensitivityResponse = {
  ranking_version: string;
  baseline_weights: Record<string, number>;
  stable_choice_definition: string;
  volatile_choice_definition: string;
  baseline_results: SensitivityMovement[];
  scenarios: SensitivityScenarioResult[];
  stable_schools: SensitivityChoiceSummary[];
  volatile_schools: SensitivityChoiceSummary[];
  category_drivers: Array<{
    category: string;
    average_absolute_fit_delta: number;
    affected_school_count: number;
    explanation: string;
  }>;
  confidence_impacts: Array<{
    school_id: number;
    name: string;
    max_confidence_delta: number;
    explanation: string;
  }>;
  tradeoff_explanations: string[];
  summary_messages: string[];
};
