import {expect, test} from "@playwright/test";

test("connects to FastAPI and creates a bill from the browser", async ({page}) => {
  await page.goto("/");

  await expect(page.getByRole("table").getByText("101", {exact: true})).toBeVisible();
  await page.getByLabel("มิเตอร์น้ำปัจจุบัน").fill("450");
  await page.getByLabel("มิเตอร์น้ำครั้งก่อน").fill("350");
  await page.getByLabel("มิเตอร์ไฟปัจจุบัน").fill("250");
  await page.getByLabel("มิเตอร์ไฟครั้งก่อน").fill("200");
  await page.getByRole("button", {name: "สร้างบิล"}).click();

  await expect(page.getByRole("status")).toContainText("สร้างบิลเรียบร้อยแล้ว");
  await expect(page.getByText("4710", {exact: true})).toBeVisible();
  await page.reload();
  await expect(page.getByText("สร้างแล้ว", {exact: true})).toBeVisible();
});

test("keeps the billing dashboard usable on a narrow viewport", async ({page}) => {
  await page.setViewportSize({width: 375, height: 812});
  await page.goto("/");

  await expect(page.locator(".billing-dashboard")).toBeVisible();
  await expect(page.locator(".dashboard-summary")).toBeVisible();
  await expect(page.locator(".billing-workspace")).toBeVisible();
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
  ).toBe(true);
});
