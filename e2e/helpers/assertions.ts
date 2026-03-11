import { type Page, type Locator, expect } from "@playwright/test";

/**
 * Assert that a toast notification is visible with the given text.
 * Uses react-toastify's container structure.
 */
export async function expectToast(page: Page, text: string | RegExp): Promise<void> {
  const toast = page.locator(".Toastify__toast").filter({ hasText: text });
  await expect(toast.first()).toBeVisible({ timeout: 5_000 });
}

/** Assert that no toast with the given text is visible. */
export async function expectNoToast(page: Page, text: string | RegExp): Promise<void> {
  const toast = page.locator(".Toastify__toast").filter({ hasText: text });
  await expect(toast).toHaveCount(0, { timeout: 2_000 });
}

/** Assert the notification badge shows a specific count. */
export async function expectNotificationCount(page: Page, count: number): Promise<void> {
  const bell = page.locator('button[aria-label="Notifications"]');
  if (count === 0) {
    // No badge span should be present
    await expect(bell.locator("span")).toHaveCount(0, { timeout: 3_000 });
  } else {
    const badge = bell.locator("span");
    const expected = count > 99 ? "99+" : String(count);
    await expect(badge).toHaveText(expected, { timeout: 5_000 });
  }
}

/** Assert that a locator has a specific aria attribute value. */
export async function expectAriaAttribute(
  locator: Locator,
  attribute: string,
  value: string,
): Promise<void> {
  await expect(locator).toHaveAttribute(`aria-${attribute}`, value);
}

/** Assert page URL matches (partial). */
export async function expectUrl(page: Page, path: string | RegExp): Promise<void> {
  if (typeof path === "string") {
    await expect(page).toHaveURL(new RegExp(path.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  } else {
    await expect(page).toHaveURL(path);
  }
}

/** Wait for a loading state to disappear. */
export async function waitForLoadingToFinish(page: Page): Promise<void> {
  // Wait for common skeleton/loading patterns to disappear
  const skeletons = page.locator('[class*="skeleton"], [class*="Skeleton"]');
  await expect(skeletons).toHaveCount(0, { timeout: 10_000 }).catch(() => {
    // Some skeletons may persist — that's OK, we just wait briefly
  });
}

/** Assert element is disabled (works for buttons, inputs, etc.). */
export async function expectDisabled(locator: Locator): Promise<void> {
  await expect(locator).toBeDisabled();
}

/** Assert element is enabled. */
export async function expectEnabled(locator: Locator): Promise<void> {
  await expect(locator).toBeEnabled();
}
