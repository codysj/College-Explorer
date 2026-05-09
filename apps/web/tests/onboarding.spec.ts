import { expect, test } from "@playwright/test";

test("completes onboarding and routes to search with local preferences", async ({ page }) => {
  await page.route("**/schools/search**", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        results: [],
        page: 1,
        page_size: 10,
        total_results: 0,
        has_next: false,
      }),
    });
  });

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

  await expect(page).toHaveURL(/\/search/);
  await expect(page).toHaveURL(/state=CA/);
  await expect(page.getByText("Using local preference profile")).toBeVisible();

  const stored = await page.evaluate(() =>
    window.localStorage.getItem("college-exploration.preference-profile.v1"),
  );
  expect(stored).toContain("Computer Science");
});
