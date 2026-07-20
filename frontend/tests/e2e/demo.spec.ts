import { expect, test } from "@playwright/test";

const API_ORIGIN = process.env.E2E_API_ORIGIN ?? "http://localhost:8000";

test("complete resolution, approval, incident, and audit workflow", async ({
  page,
  request,
}) => {
  const reset = await request.post(`${API_ORIGIN}/api/v1/demo/reset`);
  expect(reset.ok()).toBeTruthy();

  await page.goto("/chat");
  await expect(page.getByText("Connected", { exact: true })).toBeVisible();
  await expect(page.locator("select option")).toHaveCount(3);
  await expect(page.getByText("ORD-2026-1001", { exact: true })).toBeVisible();

  await page.getByRole("button", { name: "Resolve issue" }).click();
  await expect(page.getByRole("heading", { name: "Resolution trace" })).toBeVisible();
  await expect(page.locator(".badge-automatic").first()).toBeVisible();
  await expect(page.locator(".badge-completed").first()).toBeVisible();
  await expect(page.getByText("Failed Payment Spike", { exact: true })).toBeVisible();

  await page.getByRole("button", { name: /Human approval/ }).click();
  await page.getByRole("button", { name: "Resolve issue" }).click();
  await expect(page.locator(".badge-approval-required").first()).toBeVisible();
  await expect(page.locator(".badge-awaiting-approval").first()).toBeVisible();

  await page.goto("/approvals");
  await expect(page.getByText("₹1,499", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Approve and execute" }).click();
  await expect(page.getByText(/refund approved and executed/)).toBeVisible();

  await page.goto("/incidents");
  await expect(page.getByText("Failed Payment Spike", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Begin investigation" }).click();
  await expect(page.locator(".badge-investigating")).toBeVisible();

  await page.goto("/audit");
  await expect(page.getByText("Complaint classified", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("Refund completed", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("Approval requested", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("Incident detected", { exact: true }).first()).toBeVisible();

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/chat");
  const hasHorizontalPageOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth + 1
  );
  expect(hasHorizontalPageOverflow).toBeFalsy();
  await expect(page.getByRole("button", { name: "Resolve issue" })).toBeVisible();
});
