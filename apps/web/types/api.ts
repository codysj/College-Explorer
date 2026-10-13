// API types come from the backend's OpenAPI schema. `types/openapi.json` is exported by
// `python apps/api/scripts/export_openapi.py` and `types/api.gen.ts` is generated from it by
// `npm run generate:api-types`; CI fails if either drifts from the code. Only the aliases
// below and frontend-only helpers are written by hand.
import type { components } from "./api.gen";

type Schemas = components["schemas"];

export type RankingCategoryKey =
  | "academic"
  | "cost"
  | "career"
  | "location"
  | "campus"
  | "admissions_realism";

export type RankingCategoryScores = Partial<Record<RankingCategoryKey, number>>;

export type SchoolSearchCard = Schemas["SchoolSearchResult"];
export type SchoolSearchResponse = Schemas["SearchResponse"];
export type RankingResponse = Schemas["RankingResponse"];
export type SemanticSearchResponse = Schemas["SemanticSearchResponse"];
export type SchoolProfile = Schemas["SchoolProfileResponse"];

export type SimilarSchoolCard = Schemas["SimilarSchoolResult"];
export type SimilarSchoolsResponse = Schemas["SimilarSchoolsResponse"];
export type SimilarSchoolVariant = SimilarSchoolsResponse["variant"];

export type DecisionSchoolSummary = Schemas["DecisionSchoolSummary"];
export type DecisionFinalistRankingRow = Schemas["DecisionFinalistRankingRow"];
export type DecisionCategoryScoreRow = Schemas["DecisionCategoryScoreRow"];
export type DecisionCostValueRow = Schemas["DecisionCostValueRow"];
export type DecisionConcernRow = Schemas["DecisionConcernRow"];
export type DecisionSensitivityHighlight = Schemas["DecisionSensitivityHighlight"];
export type DecisionRecommendation = Schemas["DecisionRecommendation"];
export type DecisionReportResponse = Schemas["DecisionReportResponse"];

// The request-side shape: defaulted fields such as the loan rate may be omitted when sending.
export type CostCalculatorAssumption = Schemas["CostCalculatorAssumption-Input"];
export type CostCalculatorResult = Schemas["CostCalculatorSchoolResult"];
export type CostCalculatorResponse = Schemas["CostCalculatorResponse"];

export type SensitivityMovement = Schemas["SensitivitySchoolMovement"];
export type SensitivityScenarioResult = Schemas["SensitivityScenarioResult"];
export type SensitivityChoiceSummary = Schemas["SensitivityChoiceSummary"];
export type SensitivityResponse = Schemas["SensitivityResponse"];

export type AnalyticsCountRow = Schemas["AnalyticsCountRow"];
export type AnalyticsMetricCard = Schemas["AnalyticsMetricCard"];
export type AnalyticsRateRow = Schemas["AnalyticsRateRow"];
export type AnalyticsDistributionRow = Schemas["AnalyticsDistributionRow"];
export type AnalyticsSchoolMetric = Schemas["AnalyticsSchoolMetric"];
export type RankingEvaluationSummary = Schemas["RankingEvaluationSummary"];
export type AnalyticsSummaryResponse = Schemas["AnalyticsSummaryResponse"];
