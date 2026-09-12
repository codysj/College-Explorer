import { expect, test } from "@playwright/test";

import { routeSearch, routeSensitivity, schools, toProfile } from "./fixtures";

test("saves, updates, and removes schools from the dashboard", async ({ page }) => {
  await routeSearch(page);
  await page.goto("/search");

  await expect(page.getByRole("link", { name: "Test College 1", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Save" }).first().click();
  await expect(page.getByRole("button", { name: "Saved" })).toBeVisible();
  await page.goto("/dashboard");

  await expect(page.getByRole("heading", { name: "Saved schools", exact: true })).toBeVisible();
  await expect(page.getByRole("link", { name: "Test College 1", exact: true })).toBeVisible();

  await page.getByLabel("Update status for Test College 1").selectOption("finalist");
  await expect(page.getByRole("heading", { name: "Finalist" })).toBeVisible();
  await page.getByRole("button", { name: "Remove Test College 1" }).click();

  await expect(page.getByText("No saved schools yet")).toBeVisible();
});

test("compare tray persists and prevents more than five schools", async ({ page }) => {
  await routeSearch(page);
  await page.goto("/search");

  for (let index = 0; index < 5; index += 1) {
    await page.getByRole("button", { name: "Compare" }).first().click();
  }

  await expect(page.getByText("Compare tray: 5 of 5 selected")).toBeVisible();
  const storedCount = await page.evaluate(
    () => JSON.parse(window.localStorage.getItem("college-exploration.compare-schools.v1") ?? "[]").length,
  );
  expect(storedCount).toBe(5);

  await page.goto("/dashboard");
  await expect(page.getByText("Compare tray: 5 of 5 selected")).toBeVisible();
});

test("renders the comparison workspace for selected schools", async ({ page }) => {
  await page.addInitScript((selectedSchools) => {
    window.localStorage.setItem("college-exploration.compare-schools.v1", JSON.stringify(selectedSchools));
  }, schools.slice(0, 2).map((school) => ({ ...school, added_at: new Date().toISOString() })));

  await page.route("**:8000/schools/*", async (route) => {
    const schoolId = Number(route.request().url().split("/").pop());
    const school = schools.find((item) => item.school_id === schoolId) ?? schools[0];
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify(toProfile(school)),
    });
  });
  await page.route("**/cost-calculator", async (route) => {
    await route.abort();
  });
  await routeSensitivity(page);

  await page.goto("/compare");

  await expect(page.getByRole("heading", { name: "Compare schools" })).toBeVisible();
  await expect(page.getByText("Best overall fit")).toBeVisible();
  await expect(page.getByText("Sensitivity analysis")).toBeVisible();
  await expect(page.getByLabel("Cost/value weight")).toBeVisible();
  await page.getByLabel("Cost/value weight").fill("0.55");
  await expect(page.getByText("Test College 1 remains stable")).toBeVisible();
  await expect(page.getByText("stable choice").first()).toBeVisible();
  await expect(page.getByRole("heading", { name: "Cost/value calculator", exact: true })).toBeVisible();
  await page.getByLabel("Yearly cost for school 1").fill("18000");
  await page.getByLabel("Annual loans for school 1").fill("5500");
  await page.getByRole("button", { name: "Calculate" }).click();
  await expect(page.getByText("Estimated four-year cost")).toBeVisible();
  await expect(page.getByText("$72,000")).toBeVisible();
  await expect(page.getByText("Metrics table")).toBeVisible();
  await expect(page.getByRole("cell", { name: "$20,000" })).toBeVisible();
  await expect(page.getByText("Tradeoff summary")).toBeVisible();
});

test("edits accepted-school offers and generates a decision summary", async ({ page }) => {
  await page.addInitScript((savedSchools) => {
    window.localStorage.setItem("college-exploration.saved-schools.v1", JSON.stringify(savedSchools));
  }, schools.slice(0, 2).map((school, index) => ({
    ...school,
    status: index === 0 ? "finalist" : "accepted",
    saved_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  })));

  await page.route("**/decision/offers", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ id: 1, user_id: 1, school_name: "Test College 1", city: "Northbridge", state: "MA", ...(await route.request().postDataJSON()) }),
    });
  });
  await page.route("**/decision/report", async (route) => {
    await route.abort();
  });
  await page.route("**/cost-calculator", async (route) => {
    await route.abort();
  });

  await page.goto("/decision");

  await expect(page.getByRole("heading", { name: "Accepted schools", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Cost/value calculator", exact: true })).toBeVisible();
  await expect(page.getByLabel("Estimated yearly cost").first()).toBeVisible();
  await page.getByLabel("Estimated yearly cost").first().fill("18000");
  await page.getByLabel("Annual loans").first().fill("5500");
  await page.getByRole("button", { name: "Calculate" }).click();
  await expect(page.getByLabel("Four-year total for Test College 1")).toContainText("$72,000");
  await expect(page.getByLabel("Unresolved concerns/questions").first()).toBeVisible();
  await page.getByLabel("Unresolved concerns/questions").first().fill("Confirm housing package");
  await page.getByRole("button", { name: "Save offer" }).first().click();
  await page.getByRole("button", { name: "Generate summary" }).click();

  await expect(page.getByText("Decision summary")).toBeVisible();
  await expect(page.getByText("Best overall fit")).toBeVisible();
  await expect(page.getByText("Best value")).toBeVisible();
  await expect(page.getByText("Lowest risk")).toBeVisible();
  await expect(page.getByText("Major tradeoffs")).toBeVisible();
  await page.getByRole("link", { name: "Open report" }).click();
  await expect(page.getByRole("heading", { name: "College Decision Briefing" })).toBeVisible();
  await expect(page.getByText("Finalist Ranking")).toBeVisible();
  await expect(page.getByText("Cost And Value")).toBeVisible();
  await expect(page.getByText("Sensitivity Highlights")).toBeVisible();
  await expect(page.getByText("Questions Still Worth Investigating")).toBeVisible();
  await expect(page.getByRole("button", { name: "Print" })).toBeVisible();
});
