import { type Page, type Locator, expect } from "@playwright/test";

export class AdminPage {
  readonly page: Page;

  /** Tab triggers. */
  readonly aiContextTab: Locator;
  readonly parametersTab: Locator;
  readonly monitoringTab: Locator;
  readonly usersTab: Locator;

  /** AI Context tab content. */
  readonly facilitatorTextarea: Locator;
  readonly sectionsTextarea: Locator;
  readonly freetextTextarea: Locator;

  /** Parameters tab content. */
  readonly parametersTable: Locator;

  /** Monitoring tab content. */
  readonly alertToggle: Locator;
  readonly alertToggleSwitch: Locator;

  /** Users tab content. */
  readonly userSearchInput: Locator;
  readonly userCardGrid: Locator;

  constructor(page: Page) {
    this.page = page;

    // Tab triggers use Radix TabsTrigger with value attributes
    this.aiContextTab = page.locator('[role="tab"]').filter({ hasText: /ai context|ki-kontext/i });
    this.parametersTab = page.locator('[role="tab"]').filter({ hasText: /parameters|parameter/i });
    this.monitoringTab = page.locator('[role="tab"]').filter({ hasText: /monitoring|überwachung/i });
    this.usersTab = page.locator('[role="tab"]').filter({ hasText: /users|benutzer/i });

    // AI Context
    this.facilitatorTextarea = page.locator('[data-testid="facilitator-textarea"]');
    this.sectionsTextarea = page.locator('[data-testid="sections-textarea"]');
    this.freetextTextarea = page.locator('[data-testid="freetext-textarea"]');

    // Parameters
    this.parametersTable = page.locator('[data-testid="parameters-table"]');

    // Monitoring
    this.alertToggle = page.locator('[data-testid="alert-toggle"]');
    this.alertToggleSwitch = page.locator('[data-testid="alert-toggle-switch"]');

    // Users
    this.userSearchInput = page.locator('[data-testid="user-search-input"]');
    this.userCardGrid = page.locator('[data-testid="user-card-grid"]');
  }

  /** Navigate to the admin page. */
  async goto(): Promise<void> {
    await this.page.goto("/admin");
    await this.page.waitForLoadState("networkidle");
  }

  /** Switch to the AI Context tab. */
  async switchToAIContext(): Promise<void> {
    await this.aiContextTab.click();
    await expect(this.facilitatorTextarea).toBeVisible();
  }

  /** Switch to the Parameters tab. */
  async switchToParameters(): Promise<void> {
    await this.parametersTab.click();
    await expect(this.parametersTable).toBeVisible();
  }

  /** Switch to the Monitoring tab. */
  async switchToMonitoring(): Promise<void> {
    await this.monitoringTab.click();
    await expect(this.alertToggle).toBeVisible();
  }

  /** Switch to the Users tab. */
  async switchToUsers(): Promise<void> {
    await this.usersTab.click();
    await expect(this.userSearchInput).toBeVisible();
  }

  /** Search for a user in the Users tab. */
  async searchUser(query: string): Promise<void> {
    await this.userSearchInput.fill(query);
  }

  /** Assert the page loaded (default tab visible). */
  async expectLoaded(): Promise<void> {
    await expect(this.aiContextTab).toBeVisible();
  }

  /** Assert the admin page redirected (non-admin user). */
  async expectRedirected(): Promise<void> {
    await expect(this.page).not.toHaveURL("/admin");
  }

  /** Get a parameter row by key. */
  getParameterRow(key: string): Locator {
    return this.parametersTable.locator("tr").filter({ hasText: key });
  }

  /** Get the edit input for a parameter by key. */
  getParameterInput(key: string): Locator {
    return this.page.locator(`[data-testid="edit-input-${key}"]`);
  }

  /** Get the displayed value for a parameter by key. */
  getParameterValue(key: string): Locator {
    return this.page.locator(`[data-testid="value-${key}"]`);
  }
}
