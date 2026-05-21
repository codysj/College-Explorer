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
