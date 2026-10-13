/**
 * Captures the README screenshots from the real stack: no mocks, real API, real database.
 *
 * Needs the API on :8000 (rate limiting off, or the run trips it) and a production web
 * build on :3000, then:
 *   npx playwright test --config media/playwright.media.config.ts
 * Images land in docs/media/. Re-run after a UI or data change so the README stays truthful.
 */
import { expect, test, type Page } from "@playwright/test";
import path from "node:path";

const out = (name: string) => path.resolve(__dirname, "../../../docs/media", `${name}.png`);

async function shoot(page: Page, name: string) {
  // Let fonts and late fetches settle so the image matches what a student sees.
  await page.waitForLoadState("networkidle");
  await page.screenshot({ path: out(name), fullPage: false });
}

test("capture README media", async ({ page }) => {
  test.setTimeout(240_000);

  await page.goto("/");
  await shoot(page, "landing");

  // The same sample student as the landing card: Biology, from California, $25k a year.
  await page.goto("/onboarding");
  await page.getByLabel("Intended major").fill("Biology");
  await page.getByRole("button", { name: "Continue" }).click();
  await page.getByLabel("Max annual net price").fill("25000");
  await page.getByRole("button", { name: "Continue" }).click();
  // Every step needs an answer. These two have no public data behind them, so they are saved
  // but leave the scores, and so the landing card's numbers, unchanged.
  await page.getByRole("button", { name: "Graduate school" }).click();
  await page.getByRole("button", { name: "Continue" }).click();
  await page.getByLabel("Home state").fill("CA");
  await page.getByRole("button", { name: "Continue" }).click();
  await page.getByRole("button", { name: "Greek life" }).click();
  await page.getByRole("button", { name: "Continue" }).click();
  await page.getByLabel("Admissions strategy").selectOption("balanced");
  await page.getByRole("button", { name: "Continue" }).click();
  await page.getByRole("button", { name: "Save and search" }).click();

  await expect(page.getByText("Ranked by your preferences")).toBeVisible();
  await shoot(page, "search-ranked");

  // Shortlist the top four and stage three for comparison.
  for (let index = 0; index < 4; index += 1) {
    await page.getByRole("button", { name: "Save", exact: true }).first().click();
  }
  for (let index = 0; index < 3; index += 1) {
    await page.getByRole("button", { name: "Compare", exact: true }).first().click();
  }

  await page.getByLabel("Search").fill("engineering in Texas");
  await expect(page.getByText('Best matches for "engineering in Texas"')).toBeVisible();
  await shoot(page, "search-described");

  await page.goto("/search?query=San+Diego&sort_ui=best_fit");
  await page.getByRole("link", { name: "University of California-San Diego", exact: true }).first().click();
  await expect(page.getByRole("heading", { name: "Similar Schools" })).toBeVisible();
  await shoot(page, "school-profile");

  await page.goto("/compare");
  await expect(page.getByText("Sensitivity analysis")).toBeVisible();
  await page.getByRole("button", { name: "Calculate" }).click();
  await expect(page.getByText("Estimated four-year cost")).toBeVisible();
  await page.evaluate(() => window.scrollTo(0, 0));
  await shoot(page, "compare");

  await page.goto("/dashboard");
  const statuses = page.getByLabel(/Update status for/);
  await statuses.nth(0).selectOption("accepted");
  await statuses.nth(1).selectOption("accepted");
  await statuses.nth(2).selectOption("finalist");

  await page.goto("/decision");
  await page.getByRole("button", { name: "Generate summary" }).click();
  await expect(page.getByText("Decision summary")).toBeVisible();
  await page.getByRole("link", { name: "Open report" }).click();
  await expect(page.getByRole("heading", { name: "College Decision Briefing" })).toBeVisible();
  await shoot(page, "decision-report");
});
