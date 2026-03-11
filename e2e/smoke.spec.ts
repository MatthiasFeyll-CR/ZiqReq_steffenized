import { test, expect } from "@playwright/test";
import { loginAs, DEV_USERS } from "./helpers/auth";
import { NavbarPage } from "./pages/navbar.page";
import { LandingPage } from "./pages/landing.page";

test.describe("Smoke tests", () => {
  test("landing page loads and user is authenticated", async ({ page }) => {
    // Log in as Carol (basic user)
    await loginAs(page, "carol");

    const landing = new LandingPage(page);
    const navbar = new NavbarPage(page);

    // Verify landing page rendered
    await landing.expectLoaded();

    // Verify the ZiqReq logo is visible
    await expect(navbar.logo).toBeVisible();

    // Verify the user is authenticated — name shows in user menu
    await navbar.expectUserName(DEV_USERS.carol.displayName);
  });

  test("admin user sees all nav links", async ({ page }) => {
    await loginAs(page, "alice");

    const navbar = new NavbarPage(page);

    await navbar.expectReviewsVisible();
    await navbar.expectAdminVisible();
  });

  test("regular user does not see admin link", async ({ page }) => {
    await loginAs(page, "carol");

    const navbar = new NavbarPage(page);

    await navbar.expectAdminHidden();
  });

  test("navigation between pages works", async ({ page }) => {
    await loginAs(page, "alice");

    // Start on landing
    await expect(page).toHaveURL("/");

    // Navigate to reviews
    const navbar = new NavbarPage(page);
    await navbar.goToReviews();
    await expect(page).toHaveURL("/reviews");

    // Navigate to admin
    await navbar.goToAdmin();
    await expect(page).toHaveURL("/admin");

    // Navigate back to landing
    await navbar.goToIdeas();
    await expect(page).toHaveURL("/");
  });
});
