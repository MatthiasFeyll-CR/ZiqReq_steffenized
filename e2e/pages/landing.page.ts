import { type Page, type Locator, expect } from "@playwright/test";

export class LandingPage {
  readonly page: Page;

  /** Hero section. */
  readonly heading: Locator;
  readonly ideaTextarea: Locator;
  readonly submitButton: Locator;

  /** Filter bar. */
  readonly searchInput: Locator;
  readonly stateFilter: Locator;
  readonly ownershipFilter: Locator;
  readonly clearFiltersButton: Locator;

  /** Idea list sections. */
  readonly myIdeasSection: Locator;
  readonly collaboratingSection: Locator;
  readonly invitationsSection: Locator;
  readonly trashSection: Locator;

  constructor(page: Page) {
    this.page = page;

    // Hero
    this.heading = page.locator("h1").first();
    this.ideaTextarea = page.locator("textarea").first();
    this.submitButton = page.locator('button[variant="primary"], button').filter({ hasText: /submit|erstellen/i }).first();

    // Filter bar — search input is the one with the search icon
    this.searchInput = page.locator('input[type="text"]').first();
    this.stateFilter = page.locator('[role="combobox"]').first();
    this.ownershipFilter = page.locator('[role="combobox"]').nth(1);
    this.clearFiltersButton = page.getByRole("button", { name: /clear/i });

    // Sections — identify by heading text
    const grid = page.locator(".grid");
    this.myIdeasSection = grid.locator("section").first();
    this.collaboratingSection = grid.locator("section").nth(1);
    this.invitationsSection = grid.locator("section").nth(2);
    this.trashSection = grid.locator("section").nth(3);
  }

  /** Navigate to the landing page. */
  async goto(): Promise<void> {
    await this.page.goto("/");
    await this.page.waitForLoadState("networkidle");
  }

  /** Create an idea by typing in the hero textarea and submitting. */
  async createIdea(message: string): Promise<void> {
    await this.ideaTextarea.fill(message);
    await this.submitButton.click();
    // Should navigate to workspace
    await this.page.waitForURL(/\/idea\//);
  }

  /** Search ideas using the filter bar. */
  async search(query: string): Promise<void> {
    await this.searchInput.fill(query);
  }

  /** Clear the search input. */
  async clearSearch(): Promise<void> {
    await this.searchInput.clear();
  }

  /** Get all idea cards visible on the page. */
  getIdeaCards(): Locator {
    return this.page.locator('[class*="IdeaCard"], [class*="idea-card"]').or(
      this.page.locator("a").filter({ hasText: /ago|gerade/ }),
    );
  }

  /** Assert the heading is visible (page loaded). */
  async expectLoaded(): Promise<void> {
    await expect(this.heading).toBeVisible();
  }

  /** Assert the hero section has the expected heading text. */
  async expectHeroHeading(text: string | RegExp): Promise<void> {
    await expect(this.heading).toHaveText(text);
  }

  /** Assert a specific idea title is visible in My Ideas. */
  async expectMyIdea(title: string | RegExp): Promise<void> {
    const card = this.myIdeasSection.locator("a, div").filter({ hasText: title });
    await expect(card.first()).toBeVisible({ timeout: 5_000 });
  }
}
