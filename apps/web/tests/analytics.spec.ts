import { expect, test } from "@playwright/test";

test("renders analytics dashboard with ranking evaluation states", async ({ page }) => {
  await page.route("**/analytics/summary**", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        generated_at: new Date().toISOString(),
        lookback_days: 90,
        event_counts: [{ key: "school_saved", count: 4 }],
        metric_cards: [
          { label: "Searches", value: 12, detail: "Structured and semantic search events." },
          { label: "Saves", value: 4, detail: "Privacy-safe school save events." },
          { label: "Compares", value: 3, detail: "Schools added to comparison." },
          { label: "Reports", value: 2, detail: "Decision reports generated." },
          { label: "Onboarding completion", value: "67%", detail: "Completed profiles divided by observed starts/completions." },
        ],
        most_used_filters: [{ key: "state", count: 5 }],
        most_viewed_schools: [{ school_id: 1, school_name: "Test College 1", count: 3 }],
        most_saved_schools: [{ school_id: 2, school_name: "Test College 2", count: 4 }],
        compare_frequency: [{ key: "2026-05-21", count: 3 }],
        onboarding_completion_rate: { bucket: "onboarding", numerator: 2, denominator: 3, rate: 0.6667 },
        save_rate_by_rank_position: [{ bucket: "1", numerator: 2, denominator: 5, rate: 0.4 }],
        report_generation_frequency: [{ key: "2026-05-21", count: 2 }],
        ranking_version_usage: [{ key: "v1.0", count: 8 }],
        ranking_evaluation: {
          save_rate_by_fit_bucket: [{ bucket: "90-100", numerator: 2, denominator: 5, rate: 0.4 }],
          compare_rate_by_rank_position: [{ bucket: "1", numerator: 1, denominator: 4, rate: 0.25 }],
          top_reason_code_frequency: [{ key: "academic_major_match", count: 3 }],
          confidence_distribution: [{ bucket: "high", count: 6 }],
          ranking_version_distribution: [{ key: "v1.0", count: 8 }],
          category_weight_save_correlations: [{ key: "academic", count: 2 }],
          interpretation_notes: ["Correlation metrics are descriptive."],
        },
        privacy_note: "Analytics events avoid sensitive notes and financial details.",
        limitations: ["Correlation metrics are descriptive and not causal."],
      }),
    });
  });

  await page.goto("/analytics");

  await expect(page.getByRole("heading", { name: "Analytics and ranking evaluation" })).toBeVisible();
  await expect(page.getByText("Ranking Evaluation")).toBeVisible();
  await expect(page.getByText("Top reason codes")).toBeVisible();
  await expect(page.getByText("academic major match")).toBeVisible();
  await expect(page.getByText("Privacy and limitations")).toBeVisible();
});
