import { type Page, type Locator, expect } from "@playwright/test";

export class WorkspacePage {
  readonly page: Page;

  /** Top-level containers. */
  readonly workspace: Locator;
  readonly header: Locator;
  readonly layout: Locator;

  /** Workspace header elements. */
  readonly backButton: Locator;
  readonly titleInput: Locator;
  readonly titleDisplay: Locator;
  readonly agentModeTrigger: Locator;

  /** Chat panel. */
  readonly chatPanel: Locator;
  readonly chatInput: Locator;
  readonly chatMessages: Locator;

  /** Context panel (Board / Review tabs). */
  readonly contextPanel: Locator;
  readonly boardTab: Locator;
  readonly reviewTab: Locator;
  readonly boardContent: Locator;
  readonly reviewContent: Locator;

  /** Review section (below-fold, appears after submission). */
  readonly reviewSection: Locator;

  /** Banners. */
  readonly offlineBanner: Locator;
  readonly readOnlyBanner: Locator;

  /** Loading / error states. */
  readonly loadingState: Locator;
  readonly errorState: Locator;

  constructor(page: Page) {
    this.page = page;

    this.workspace = page.locator('[data-testid="idea-workspace"]');
    this.header = page.locator('[data-testid="workspace-header"]');
    this.layout = page.locator('[data-testid="workspace-layout"]');

    // Header
    this.backButton = page.locator('[data-testid="back-button"]');
    this.titleInput = page.locator('[data-testid="title-input"]');
    this.titleDisplay = page.locator('[data-testid="title-display"]');
    this.agentModeTrigger = page.locator('[data-testid="agent-mode-trigger"]');

    // Chat
    this.chatPanel = page.locator('[data-testid="chat-panel"]');
    this.chatInput = this.chatPanel.locator("textarea, input").first();
    this.chatMessages = this.chatPanel.locator('[class*="message"], [class*="bubble"]');

    // Context panel (Board/Review)
    this.contextPanel = page.locator('[data-testid="context-panel"]');
    this.boardTab = page.locator('[data-testid="tab-board"]');
    this.reviewTab = page.locator('[data-testid="tab-review"]');
    this.boardContent = page.locator('[data-testid="board-content"]');
    this.reviewContent = page.locator('[data-testid="review-content"]');

    // Review section (below fold)
    this.reviewSection = page.locator('[data-testid="review-section-wrapper"]');

    // Banners
    this.offlineBanner = page.locator("text=offline").first();
    this.readOnlyBanner = page.locator("text=read-only").first();

    // Loading/Error
    this.loadingState = page.locator('[data-testid="workspace-loading"]');
    this.errorState = page.locator('[data-testid="workspace-error"]');
  }

  /** Navigate to a specific idea workspace. */
  async goto(ideaId: string): Promise<void> {
    await this.page.goto(`/idea/${ideaId}`);
    await expect(this.workspace.or(this.errorState)).toBeVisible({ timeout: 15_000 });
  }

  /** Assert the workspace loaded successfully. */
  async expectLoaded(): Promise<void> {
    await expect(this.workspace).toBeVisible({ timeout: 10_000 });
  }

  /** Assert the title displays the expected text. */
  async expectTitle(title: string | RegExp): Promise<void> {
    await expect(this.titleDisplay.or(this.titleInput)).toHaveText(title);
  }

  /** Send a chat message. */
  async sendMessage(message: string): Promise<void> {
    await this.chatInput.fill(message);
    await this.chatInput.press("Enter");
  }

  /** Switch to the Board tab. */
  async switchToBoard(): Promise<void> {
    await this.boardTab.click();
    await expect(this.boardContent).toBeVisible();
  }

  /** Switch to the Review tab. */
  async switchToReview(): Promise<void> {
    await this.reviewTab.click();
    await expect(this.reviewContent).toBeVisible();
  }

  /** Go back to landing via back button. */
  async goBack(): Promise<void> {
    await this.backButton.click();
    await this.page.waitForURL("/");
  }

  /** Assert the error state is shown. */
  async expectError(): Promise<void> {
    await expect(this.errorState).toBeVisible({ timeout: 10_000 });
  }

  /** Assert the review section is visible (idea was submitted). */
  async expectReviewSectionVisible(): Promise<void> {
    await expect(this.reviewSection).toBeVisible();
  }
}
