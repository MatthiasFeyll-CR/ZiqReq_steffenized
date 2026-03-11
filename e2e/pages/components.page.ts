import { type Page, type Locator, expect } from "@playwright/test";

/**
 * Page object for shared UI components that appear across pages:
 * toasts, notification panel, error modals, banners.
 */
export class ComponentsPage {
  readonly page: Page;

  /** Toast container (react-toastify). */
  readonly toastContainer: Locator;

  /** Notification panel (dropdown from bell). */
  readonly notificationPanel: Locator;

  /** Error modal / boundary. */
  readonly errorModal: Locator;
  readonly errorModalClose: Locator;

  /** Offline banner. */
  readonly offlineBanner: Locator;

  /** Dev user switcher (bottom-left in bypass mode). */
  readonly devSwitcher: Locator;

  /** Skip link (accessibility). */
  readonly skipLink: Locator;

  constructor(page: Page) {
    this.page = page;

    // react-toastify renders into a container with this class
    this.toastContainer = page.locator(".Toastify");

    // NotificationPanel renders as an absolute-positioned dropdown
    this.notificationPanel = page.locator('[class*="NotificationPanel"]').or(
      page.locator('[role="dialog"]').filter({ hasText: /notification/i }),
    );

    // Error boundary / modal
    this.errorModal = page.locator('[class*="ErrorLogModal"]').or(
      page.locator('[role="dialog"]').filter({ hasText: /error/i }),
    );
    this.errorModalClose = this.errorModal.locator('button[aria-label="Close"], button').filter({ hasText: /close|schließen/i });

    // Offline banner
    this.offlineBanner = page.locator('[class*="OfflineBanner"]').or(
      page.locator("text=offline").first(),
    );

    // Dev user switcher
    this.devSwitcher = page.locator("text=Dev User Switcher").locator("..").or(
      page.locator("text=Entwickler-Benutzerwechsler").locator(".."),
    );

    // Skip link
    this.skipLink = page.locator('[class*="SkipLink"]').or(
      page.locator("a").filter({ hasText: /skip/i }),
    );
  }

  /** Get all visible toasts. */
  getToasts(): Locator {
    return this.page.locator(".Toastify__toast");
  }

  /** Get a specific toast by text content. */
  getToast(text: string | RegExp): Locator {
    return this.getToasts().filter({ hasText: text });
  }

  /** Wait for a toast with specific text to appear. */
  async waitForToast(text: string | RegExp): Promise<void> {
    await expect(this.getToast(text).first()).toBeVisible({ timeout: 5_000 });
  }

  /** Dismiss all toasts by clicking their close buttons. */
  async dismissAllToasts(): Promise<void> {
    const closeButtons = this.getToasts().locator('button[aria-label="close"]');
    const count = await closeButtons.count();
    for (let i = 0; i < count; i++) {
      await closeButtons.nth(i).click();
    }
  }

  /** Assert the notification panel is open. */
  async expectNotificationPanelOpen(): Promise<void> {
    await expect(this.notificationPanel).toBeVisible();
  }

  /** Assert the offline banner is visible. */
  async expectOffline(): Promise<void> {
    await expect(this.offlineBanner).toBeVisible();
  }

  /** Assert the offline banner is NOT visible. */
  async expectOnline(): Promise<void> {
    await expect(this.offlineBanner).toHaveCount(0);
  }

  /** Select a dev user from the switcher widget. */
  async selectDevUser(displayName: string): Promise<void> {
    const button = this.devSwitcher.locator("button").filter({ hasText: displayName });
    await button.click();
  }

  /** Assert the dev switcher is visible. */
  async expectDevSwitcherVisible(): Promise<void> {
    await expect(this.devSwitcher).toBeVisible();
  }
}
