import { type Page, type Locator, expect } from "@playwright/test";

export class NavbarPage {
  readonly page: Page;

  /** The top nav bar element. */
  readonly navbar: Locator;

  /** Logo / brand text. */
  readonly logo: Locator;

  /** Desktop nav links. */
  readonly ideasLink: Locator;
  readonly reviewsLink: Locator;
  readonly adminLink: Locator;

  /** Utility area. */
  readonly notificationBell: Locator;
  readonly userMenuTrigger: Locator;
  readonly ideasFloatingButton: Locator;
  readonly connectionIndicator: Locator;

  /** Mobile hamburger. */
  readonly mobileMenuButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.navbar = page.locator("nav");
    this.logo = this.navbar.locator("text=ZiqReq").first();

    // Desktop nav links (visible on md+)
    this.ideasLink = this.navbar.locator('a[href="/"]').first();
    this.reviewsLink = this.navbar.locator('a[href="/reviews"]');
    this.adminLink = this.navbar.locator('a[href="/admin"]');

    // Utility area
    this.notificationBell = page.locator('button[aria-label="Notifications"]');
    this.userMenuTrigger = page.locator('button[aria-label]').filter({ has: page.locator('[class*="avatar"]') });
    this.ideasFloatingButton = this.navbar.locator("button").filter({ has: page.locator("svg.lucide-lightbulb") });
    this.connectionIndicator = page.locator('[class*="ConnectionIndicator"]');

    // Mobile
    this.mobileMenuButton = this.navbar.locator("button.md\\:hidden");
  }

  /** Navigate to the Ideas (landing) page via navbar. */
  async goToIdeas(): Promise<void> {
    await this.ideasLink.click();
    await this.page.waitForURL("/");
  }

  /** Navigate to the Reviews page via navbar. */
  async goToReviews(): Promise<void> {
    await this.reviewsLink.click();
    await this.page.waitForURL("/reviews");
  }

  /** Navigate to the Admin page via navbar. */
  async goToAdmin(): Promise<void> {
    await this.adminLink.click();
    await this.page.waitForURL("/admin");
  }

  /** Open the notification panel by clicking the bell. */
  async openNotifications(): Promise<void> {
    await this.notificationBell.click();
  }

  /** Open the user dropdown menu. */
  async openUserMenu(): Promise<void> {
    await this.userMenuTrigger.click();
  }

  /** Assert the currently displayed user name in the dropdown. */
  async expectUserName(name: string): Promise<void> {
    await this.openUserMenu();
    const label = this.page.locator('[role="menu"]').locator("text=" + name);
    await expect(label).toBeVisible();
    // Close the menu by pressing Escape
    await this.page.keyboard.press("Escape");
  }

  /** Assert a nav link is visible. */
  async expectReviewsVisible(): Promise<void> {
    await expect(this.reviewsLink).toBeVisible();
  }

  /** Assert the admin link is visible. */
  async expectAdminVisible(): Promise<void> {
    await expect(this.adminLink).toBeVisible();
  }

  /** Assert the admin link is NOT visible (non-admin user). */
  async expectAdminHidden(): Promise<void> {
    await expect(this.adminLink).toHaveCount(0);
  }
}
