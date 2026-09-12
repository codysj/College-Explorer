import { expect, test } from "@playwright/test";

import { routeSensitivity, schools, toProfile } from "./fixtures";

/**
 * V3.2: the one test that crosses the whole student journey.
 *
 * Every other spec seeds localStorage and exercises a single page. This one seeds
 * nothing: the preference profile, the shortlist, the comparison set, and the decision
 * report each have to be produced by the previous step and picked up by the next one.
 * That is the part no per-page test can cover, and the part that was actually broken
 * before V3.1 - the ranking engine existed but nothing on the journey ever called it.
 */

const rankedSchools = schools.slice(0, 3).map((school, index) => ({
  ...school,
  fit_score: 88 - index * 6,
  confidence_score: 0.92,
  category_scores: { academic: 90 - index, cost: 80 - index },
  top_reasons: ["academic_major_match", "cost_within_budget"],
  top_tradeoffs: index === 0 ? [] : ["admissions_more_selective_than_target"],
  ranking_version: "v1.0",
}));

test("carries a student from preferences through to a decision report", async ({ page }) => {
  // Six routes, each compiled on first hit by the dev server. The default 30s budget is
  // for single-page specs; this one legitimately needs more.
  test.setTimeout(180_000);

  const rankingRequests: Array<Record<string, unknown>> = [];

  await page.route("**/rankings", async (route) => {
    rankingRequests.push(route.request().postDataJSON());
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        ranking_version: "v1.0",
        results: rankedSchools,
        page: 1,
        page_size: 10,
        total_results: rankedSchools.length,
        has_next: false,
      }),
    });
  });

  await page.route("**:8000/schools/*", async (route) => {
    const schoolId = Number(route.request().url().split("/").pop());
    const school = schools.find((item) => item.school_id === schoolId) ?? schools[0];
    await route.fulfill({ contentType: "application/json", body: JSON.stringify(toProfile(school)) });
  });

  await page.route("**/decision/offers", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        id: 1,
        user_id: 1,
        school_name: "Test College 1",
        city: "Northbridge",
        state: "MA",
        ...(await route.request().postDataJSON()),
      }),
    });
  });

  await routeSensitivity(page);
  // Cost calculator and the server-rendered report are covered by their own specs; here
  // they are aborted so the journey exercises the deterministic local fallback path.
  await page.route("**/cost-calculator", (route) => route.abort());
  await page.route("**/decision/report", (route) => route.abort());
  await page.route("**/analytics/events", (route) =>
    route.fulfill({ contentType: "application/json", body: "{}" }),
  );

  // 1. Preferences -----------------------------------------------------------------
  await page.goto("/onboarding");

  await page.getByLabel("Intended major").fill("Computer Science");
  await page.getByRole("button", { name: "Continue" }).click();
  await page.getByLabel("Max annual net price").fill("32000");
  await page.getByRole("button", { name: "Continue" }).click();
  await page.getByRole("button", { name: "Internships" }).click();
  await page.getByRole("button", { name: "Continue" }).click();
  await page.getByLabel("Home state").fill("CA");
  await page.getByRole("button", { name: "West", exact: true }).click();
  await page.getByRole("button", { name: "Continue" }).click();
  await page.getByRole("button", { name: "Urban", exact: true }).click();
  await page.getByRole("button", { name: "Public" }).click();
  await page.getByRole("button", { name: "Continue" }).click();
  await page.getByLabel("Admissions strategy").selectOption("balanced");
  await page.getByRole("button", { name: "Continue" }).click();
  await page.getByRole("button", { name: "Save and search" }).click();

  // 2. Ranked results -------------------------------------------------------------
  await expect(page).toHaveURL(/\/search/);
  await expect(page.getByText("Ranked by your preferences - v1.0")).toBeVisible();
  await expect(page.getByText("Academic major match").first()).toBeVisible();

  // The weights captured in step 1 are what the engine was asked to rank by.
  expect(rankingRequests.length).toBeGreaterThan(0);
  const ranked = rankingRequests[0] as {
    preferences: { intended_major: string | null; max_annual_cost: number | null };
  };
  expect(ranked.preferences.intended_major).toBe("Computer Science");
  expect(ranked.preferences.max_annual_cost).toBe(32000);

  // 3. Shortlist ------------------------------------------------------------------
  for (let index = 0; index < 3; index += 1) {
    await page.getByRole("button", { name: "Save", exact: true }).first().click();
  }
  await page.getByRole("button", { name: "Compare", exact: true }).first().click();
  await page.getByRole("button", { name: "Compare", exact: true }).first().click();

  await page.goto("/dashboard");
  await expect(page.getByRole("heading", { name: "Saved schools", exact: true })).toBeVisible();
  for (const school of rankedSchools) {
    await expect(page.getByRole("link", { name: school.name, exact: true })).toBeVisible();
  }

  // Mark two as accepted so the decision workspace has something to work with.
  await page.getByLabel("Update status for Test College 1").selectOption("accepted");
  await page.getByLabel("Update status for Test College 2").selectOption("accepted");

  // 4. Comparison -----------------------------------------------------------------
  await page.goto("/compare");
  await expect(page.getByRole("heading", { name: "Compare schools" })).toBeVisible();
  await expect(page.getByText("Metrics table")).toBeVisible();

  // 5. Decision -------------------------------------------------------------------
  await page.goto("/decision");
  await expect(page.getByRole("heading", { name: "Accepted schools", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Generate summary" }).click();
  await expect(page.getByText("Decision summary")).toBeVisible();

  // 6. Report ---------------------------------------------------------------------
  await page.getByRole("link", { name: "Open report" }).click();
  await expect(page.getByRole("heading", { name: "College Decision Briefing" })).toBeVisible();
  await expect(page.getByText("Finalist Ranking")).toBeVisible();
  await expect(page.getByRole("button", { name: "Print" })).toBeVisible();
});

test("every step of the journey offers a way forward", async ({ page }) => {
  test.setTimeout(120_000);

  // A dead end is a page that renders nothing actionable when the student arrives with
  // no state yet. Each of these should point at the step that fills the gap.
  await page.route("**/schools/search**", (route) =>
    route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ results: [], page: 1, page_size: 10, total_results: 0, has_next: false }),
    }),
  );

  await page.goto("/dashboard");
  await expect(page.getByText("No saved schools yet")).toBeVisible();

  await page.goto("/decision");
  await expect(
    page.getByText("Mark saved schools as accepted or finalist to start the decision workspace."),
  ).toBeVisible();

  await page.goto("/decision/report");
  await expect(page.getByText("No decision report yet")).toBeVisible();
  await expect(page.getByRole("link", { name: "Back to accepted schools" })).toBeVisible();

  // Search with no profile must still say why nothing is ranked and where to fix it.
  await page.goto("/search");
  await expect(page.getByText("These results are not ranked yet")).toBeVisible();
  await expect(page.getByRole("link", { name: "Set your preferences" })).toBeVisible();
});
