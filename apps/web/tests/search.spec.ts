import { expect, test } from "@playwright/test";

const allSchools = [
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
  {
    school_id: 2,
    name: "Golden Gate Metropolitan University",
    city: "San Francisco",
    state: "CA",
    type: "Private",
    setting: "Urban",
    enrollment: 7400,
    acceptance_rate: 0.32,
    net_price: 37200,
    graduation_rate: 0.85,
    fit_score: null,
    confidence_score: null,
    top_reasons: [],
    top_tradeoffs: [],
  },
];

test("loads search and updates results when a state filter is applied", async ({ page }) => {
  await page.route("**/schools/search**", async (route) => {
    const url = new URL(route.request().url());
    const state = url.searchParams.get("state");
    const results = state
      ? allSchools.filter((school) => school.state === state.toUpperCase())
      : allSchools;

    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        results,
        page: Number(url.searchParams.get("page") ?? 1),
        page_size: Number(url.searchParams.get("page_size") ?? 10),
        total_results: results.length,
        has_next: false,
      }),
    });
  });

  await page.goto("/search");

  await expect(page.getByRole("heading", { name: "Explore schools" })).toBeVisible();
  await expect(page.getByText("Adams State College")).toBeVisible();
  await expect(page.getByText("Golden Gate Metropolitan University")).toBeVisible();

  await page.getByLabel("State").fill("CA");

  await expect(page).toHaveURL(/state=CA/);
  await expect(page.getByText("Golden Gate Metropolitan University")).toBeVisible();
  await expect(page.getByText("Adams State College")).toHaveCount(0);
});
