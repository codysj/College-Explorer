// Shared Playwright fixtures. Extracted from saved-compare.spec.ts so the journey
// spec reuses these mocks instead of carrying a second copy of them.
import { type Page } from "@playwright/test";

export const schools = Array.from({ length: 6 }, (_, index) => ({
  school_id: index + 1,
  name: `Test College ${index + 1}`,
  city: index === 0 ? "Northbridge" : "San Francisco",
  state: index === 0 ? "MA" : "CA",
  type: index % 2 === 0 ? "Public" : "Private",
  setting: index % 2 === 0 ? "Suburban" : "Urban",
  enrollment: 5000 + index * 1000,
  acceptance_rate: 0.5 - index * 0.03,
  net_price: 20000 + index * 2000,
  graduation_rate: 0.65 + index * 0.03,
  fit_score: null,
  confidence_score: null,
  category_scores: {},
  top_reasons: [],
  top_tradeoffs: [],
}));

export async function routeSearch(page: Page) {
  await page.route("**/schools/search**", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        results: schools,
        page: 1,
        page_size: 10,
        total_results: schools.length,
        has_next: false,
      }),
    });
  });
}

export async function routeSensitivity(page: Page) {
  await page.route("**/sensitivity", async (route) => {
    const body = await route.request().postDataJSON();
    const ids = body.candidate_school_ids as number[];
    const results = ids.map((schoolId, index) => {
      const school = schools.find((item) => item.school_id === schoolId) ?? schools[index];
      const costWeight = body.scenarios[0].weight_adjustments.cost_value as number;
      const baseRank = index + 1;
      const scenarioRank = costWeight >= 0.5 && schoolId === 2 ? 1 : baseRank;
      const rankDelta = baseRank - scenarioRank;
      return {
        school_id: school.school_id,
        name: school.name,
        city: school.city,
        state: school.state,
        base_rank: baseRank,
        scenario_rank: scenarioRank,
        rank_delta: rankDelta,
        fit_score: 82 - index,
        fit_delta: rankDelta * 2,
        confidence_score: 0.84,
        confidence_delta: 0,
        category_scores: { academic: 80, cost: 75, career: 70 },
        category_drivers: ["cost"],
        movement: rankDelta > 0 ? "up" : rankDelta < 0 ? "down" : "stable",
        stability: index === 0 ? "stable_choice" : "watch_choice",
        top_reasons: ["cost_within_budget"],
        top_tradeoffs: [],
        explanation: `${school.name} movement is driven by cost.`,
      };
    });
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        ranking_version: "v1.0",
        baseline_weights: { academic: 0.2, cost: 0.2, career: 0.18, campus: 0.14, location: 0.14, admissions_realism: 0.14 },
        stable_choice_definition: "A stable choice remains highly ranked across many weighting scenarios.",
        volatile_choice_definition: "A volatile choice changes rank dramatically when one preference changes.",
        baseline_results: results,
        scenarios: [
          {
            scenario_id: "current_slider",
            label: "Current slider priorities",
            applied_weights: { cost: body.scenarios[0].weight_adjustments.cost_value },
            emphasis_dimension: "cost_value",
            results,
            summary: "Current slider priorities keeps the current top choices stable.",
          },
        ],
        stable_schools: [{ school_id: 1, name: "Test College 1", base_rank: 1, average_rank: 1, max_rank_delta: 0, max_fit_delta: 0, explanation: "Stable." }],
        volatile_schools: [],
        category_drivers: [{ category: "cost", average_absolute_fit_delta: 3, affected_school_count: 1, explanation: "Cost drives movement." }],
        confidence_impacts: [],
        tradeoff_explanations: ["Cost drives movement."],
        summary_messages: ["Test College 1 remains stable across the tested weighting scenarios."],
      }),
    });
  });
}

export function toProfile(school: (typeof schools)[number]) {
  return {
    school_id: school.school_id,
    name: school.name,
    city: school.city,
    state: school.state,
    region: school.state === "CA" ? "West" : "Northeast",
    type: school.type,
    setting: school.setting,
    enrollment: school.enrollment,
    acceptance_rate: school.acceptance_rate,
    academics: {
      majors: ["Biology", "Business"],
      popular_majors: ["Biology", "Business"],
      graduation_rate: school.graduation_rate,
      retention_rate: 0.8,
      student_faculty_ratio: 15,
    },
    cost: {
      tuition_in_state: 14000,
      tuition_out_state: 31000,
      net_price: school.net_price,
      average_aid: 12000,
      debt_median: 21000,
    },
    outcomes: {
      median_earnings: 50000 + school.school_id * 3000,
      completion_rate: null,
      repayment_rate: 0.76,
      outcome_percentiles: null,
    },
    campus_life: {
      sports: "DIII",
      greek_life: 0.08,
      housing: true,
      weather_band: null,
      diversity_metrics: null,
      culture_tags: ["research", "mid-size"],
    },
    data_fields_missing: ["outcomes.completion_rate"],
    data_confidence_score: 0.85,
    fit_score: null,
    category_scores: {},
    top_reasons: [],
    top_tradeoffs: [],
    similar_schools: [],
  };
}
