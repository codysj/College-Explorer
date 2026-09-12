import { expect, test } from "@playwright/test";

// Mirrors PreferenceProfile in lib/preferences.ts. Only profile_version is load-critical.
const storedProfile = {
  profile_version: "v1.local",
  intended_major: "Computer Science",
  academic_interests: ["Engineering"],
  home_state: "CA",
  preferred_regions: ["West"],
  preferred_states: ["CA"],
  preferred_settings: ["Urban"],
  preferred_school_types: ["Public"],
  max_annual_cost: 30000,
  aid_importance: "high",
  career_priorities: ["earnings"],
  campus_preferences: ["research"],
  admissions_strategy: "balanced",
  target_acceptance_rate_min: 0.2,
  weights: {
    academic: 0.3,
    cost: 0.25,
    career: 0.15,
    campus: 0.1,
    location: 0.1,
    admissions_realism: 0.1,
  },
  completion: { completed_steps: 7, total_steps: 7, percent: 100 },
  updated_at: "2026-09-12T00:00:00.000Z",
};

const rankedResults = [
  {
    school_id: 2,
    name: "Golden Gate Metropolitan University",
    city: "San Francisco",
    state: "CA",
    type: "Private",
    setting: "Urban",
    enrollment: 7400,
    acceptance_rate: 0.32,
    net_price: 27200,
    graduation_rate: 0.85,
    fit_score: 86.4,
    confidence_score: 0.95,
    category_scores: { academic: 92, cost: 78 },
    top_reasons: ["academic_major_match", "cost_within_budget"],
    top_tradeoffs: ["admissions_more_selective_than_target"],
    ranking_version: "v1.0",
  },
];

const unrankedResults = [
  {
    school_id: 1,
    name: "Adams State College",
    city: "Northbridge",
    state: "MA",
    type: "Public",
    setting: "Suburban",
    enrollment: 6200,
    acceptance_rate: 0.64,
    net_price: 22100,
    graduation_rate: 0.69,
    fit_score: null,
    confidence_score: null,
    top_reasons: [],
    top_tradeoffs: [],
  },
];

test("ranks results from the stored preference profile and explains why", async ({ page }) => {
  await page.addInitScript((profile) => {
    window.localStorage.setItem(
      "college-exploration.preference-profile.v1",
      JSON.stringify(profile),
    );
  }, storedProfile);

  const rankingRequests: Array<Record<string, unknown>> = [];
  await page.route("**/rankings", async (route) => {
    rankingRequests.push(route.request().postDataJSON());
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        ranking_version: "v1.0",
        results: rankedResults,
        page: 1,
        page_size: 10,
        total_results: 1,
        has_next: false,
      }),
    });
  });

  // Ranked mode must not fall back to structured search.
  let structuredSearchCalls = 0;
  await page.route("**/schools/search**", async (route) => {
    structuredSearchCalls += 1;
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        results: unrankedResults,
        page: 1,
        page_size: 10,
        total_results: 1,
        has_next: false,
      }),
    });
  });

  await page.goto("/search");

  await expect(page.getByText("Golden Gate Metropolitan University")).toBeVisible();
  await expect(page.getByText("Ranked by your preferences - v1.0")).toBeVisible();

  // The fit score and the reason codes the engine returned are both surfaced.
  await expect(page.getByText("86")).toBeVisible();
  await expect(page.getByText("Academic major match")).toBeVisible();
  await expect(page.getByText("Admissions more selective than target")).toBeVisible();

  expect(structuredSearchCalls).toBe(0);

  // The stored weights and the filter panel state both reach the ranking engine.
  expect(rankingRequests.length).toBeGreaterThan(0);
  const body = rankingRequests[0] as {
    preferences: { weights: Record<string, number>; max_annual_cost: number | null };
    filters: { page: number; page_size: number };
  };
  expect(body.preferences.weights.academic).toBe(0.3);
  expect(body.preferences.max_annual_cost).toBe(30000);
  expect(body.filters.page).toBe(1);
  expect(body.filters.page_size).toBe(10);
});

test("says results are unranked when no preference profile exists", async ({ page }) => {
  let rankingCalls = 0;
  await page.route("**/rankings", async (route) => {
    rankingCalls += 1;
    await route.abort();
  });
  await page.route("**/schools/search**", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        results: unrankedResults,
        page: 1,
        page_size: 10,
        total_results: 1,
        has_next: false,
      }),
    });
  });

  await page.goto("/search");

  await expect(page.getByText("These results are not ranked yet")).toBeVisible();
  await expect(page.getByRole("link", { name: "Set your preferences" })).toHaveAttribute(
    "href",
    "/onboarding",
  );
  await expect(page.getByText("Adams State College")).toBeVisible();

  // Without a profile there is nothing to rank against, so /rankings must not be called.
  expect(rankingCalls).toBe(0);
});
