import { type Page, type Locator, expect } from "@playwright/test";

export class ReviewPage {
  readonly page: Page;

  /** Page heading. */
  readonly heading: Locator;

  /** Collapsible category sections. */
  readonly assignedToMe: Locator;
  readonly unassigned: Locator;
  readonly accepted: Locator;
  readonly rejected: Locator;
  readonly dropped: Locator;

  /** Loading indicator. */
  readonly loading: Locator;

  constructor(page: Page) {
    this.page = page;
    this.heading = page.locator("h1");

    // Each category is a <section> with a button toggle containing the title.
    // We locate by the section's heading text.
    const sections = page.locator("section");
    this.assignedToMe = sections.filter({ has: page.locator('button[aria-expanded]').first() }).first();
    this.unassigned = sections.nth(1);
    this.accepted = sections.nth(2);
    this.rejected = sections.nth(3);
    this.dropped = sections.nth(4);

    this.loading = page.locator("text=loading").first();
  }

  /** Navigate to the review page. */
  async goto(): Promise<void> {
    await this.page.goto("/reviews");
    await this.page.waitForLoadState("networkidle");
  }

  /** Assert the page loaded. */
  async expectLoaded(): Promise<void> {
    await expect(this.heading).toBeVisible();
  }

  /** Expand a collapsed category section. */
  async expandCategory(section: Locator): Promise<void> {
    const button = section.locator('button[aria-expanded="false"]');
    if (await button.isVisible()) {
      await button.click();
    }
  }

  /** Collapse an expanded category section. */
  async collapseCategory(section: Locator): Promise<void> {
    const button = section.locator('button[aria-expanded="true"]');
    if (await button.isVisible()) {
      await button.click();
    }
  }

  /** Get review cards within a specific category section. */
  getCards(section: Locator): Locator {
    return section.locator('[class*="ReviewCard"], [class*="card"]').filter({
      has: this.page.locator("a"),
    });
  }

  /** Get the count badge from a category header. */
  getCategoryCount(section: Locator): Locator {
    return section.locator("span").filter({ hasText: /^\d+$/ }).first();
  }
}
