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
  acceptance_rate: 0.64,
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
  await page.route("**:8000/schools/1/similar**", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        source_school_id: 1,
        variant: "general",
        variant_applied: "general",
        ranking_version: "v1.0",
        embedding_model: "local-hash-embedding-v1",
        embedding_type: "school_search_document",
        retrieval_mode: "deterministic_fallback",
        results: [
          {
            school_id: 2,
            name: "Bayview Technical University",
            city: "New Haven",
            state: "CT",
            type: "Public",
            setting: "Urban",
            enrollment: 11800,
            acceptance_rate: 0.52,
            net_price: 24400,
            graduation_rate: 0.78,
            median_earnings: 68000,
            similarity_score: 0.82,
            fit_score: 86.4,
            top_reasons: ["overlapping_majors", "same_school_type"],
            top_tradeoffs: [],
            variant_applied: "general",
            ranking_version: "v1.0",
          },
        ],
        page: 1,
        page_size: 3,
        total_results: 1,
        has_next: false,
      }),
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
  await expect(page.getByRole("heading", { name: "Similar Schools" })).toBeVisible();
  await expect(page.getByText("Bayview Technical University")).toBeVisible();
  await expect(page.getByText("Overlapping Majors")).toBeVisible();
});

test("renders similar-school empty and variant states", async ({ page }) => {
  await page.route("**:8000/schools/1", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify(profile) });
  });
  await page.route("**:8000/schools/1/similar**", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        source_school_id: 1,
        variant: "cheaper",
        variant_applied: "cheaper",
        ranking_version: "v1.0",
        embedding_model: "local-hash-embedding-v1",
        embedding_type: "school_search_document",
        retrieval_mode: "deterministic_fallback",
        results: [],
        page: 1,
        page_size: 3,
        total_results: 0,
        has_next: false,
      }),
    });
  });

  await page.goto("/schools/1");
  await page.getByRole("button", { name: "Cheaper" }).click();

  await expect(page.getByText("No close alternatives found")).toBeVisible();
});

test("renders similar-school error state", async ({ page }) => {
  await page.route("**:8000/schools/1", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify(profile) });
  });
  await page.route("**:8000/schools/1/similar**", async (route) => {
    await route.fulfill({
      status: 500,
      contentType: "application/json",
      body: JSON.stringify({ error: { code: "server_error", message: "Similar schools failed." } }),
    });
  });

  await page.goto("/schools/1");

  await expect(page.getByText("Similar schools failed.")).toBeVisible();
});
