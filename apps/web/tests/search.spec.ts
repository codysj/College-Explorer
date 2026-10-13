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

test("a described search is matched by the semantic endpoint, with filters kept separate", async ({ page }) => {
  const requests: Array<Record<string, unknown>> = [];
  await page.route("**/schools/search**", (route) =>
    route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ results: allSchools, page: 1, page_size: 10, total_results: 2, has_next: false }),
    }),
  );
  await page.route("**/semantic-search", async (route) => {
    requests.push(await route.request().postDataJSON());
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        results: [{ ...allSchools[1], semantic_score: 0.6, match_reasons: ["semantic_query_match"] }],
        page: 1,
        page_size: 10,
        total_results: 1,
        has_next: false,
        ranking_version: "test",
        embedding_model: "postgres-fts-english",
        embedding_type: "school_search_document",
        retrieval_mode: "fulltext",
      }),
    });
  });

  await page.goto("/search?state=CA");
  await page.getByLabel("Search").fill("engineering near the bay");

  await expect(page.getByText('Best matches for "engineering near the bay"')).toBeVisible();
  await expect(page.getByText("Adams State College")).toHaveCount(0);
  const body = requests.at(-1) as { query: string; filters: Record<string, unknown> };
  expect(body.query).toBe("engineering near the bay");
  // The description is the query, not a name filter that would match no school.
  expect(body.filters).not.toHaveProperty("query");
  expect(body.filters.state).toBe("CA");
});
