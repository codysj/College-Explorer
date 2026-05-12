import { expect, test } from "@playwright/test";

const profile = {
  school_id: 1,
  name: "Adams State College",
  city: "Northbridge",
  state: "MA",
  region: "Northeast",
  type: "Public",
  setting: "Suburban",
  enrollment: 6200,
  academics: {
    majors: ["Biology", "Psychology", "Business"],
    popular_majors: ["Biology", "Psychology", "Business"],
    graduation_rate: 0.69,
    retention_rate: 0.82,
    student_faculty_ratio: 15,
  },
  cost: {
    tuition_in_state: 14200,
    tuition_out_state: 31800,
    net_price: 22100,
    average_aid: 12600,
    debt_median: 21000,
  },
  outcomes: {
    median_earnings: 52000,
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
    culture_tags: ["research", "commuter-friendly", "mid-size"],
  },
  data_fields_missing: [
    "outcomes.completion_rate",
    "outcomes.outcome_percentiles",
    "campus_life.weather_band",
    "campus_life.diversity_metrics",
  ],
  data_confidence_score: 0.8571,
  fit_score: null,
  category_scores: {},
  top_reasons: [],
  top_tradeoffs: [],
  similar_schools: [],
};

test("opens a school profile and renders backend fit summary data", async ({ page }) => {
  await page.route("**:8000/schools/1", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify(profile),
    });
  });

  await page.goto("/schools/1");

  await expect(page.getByRole("heading", { name: "Adams State College" })).toBeVisible();
  await expect(page.getByText("Northbridge, MA - Northeast")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Fit Summary" })).toBeVisible();
  await expect(page.getByText("Confidence", { exact: true })).toBeVisible();
  await expect(page.getByText("Ranking version")).toBeVisible();
  await expect(page.getByText("Biology")).toBeVisible();
  await expect(page.getByText("$22,100").first()).toBeVisible();
});
