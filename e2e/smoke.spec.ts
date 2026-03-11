import { test, expect } from "@playwright/test";
import { loginAs, DEV_USERS } from "./helpers/auth";
import { NavbarPage } from "./pages/navbar.page";
import { LandingPage } from "./pages/landing.page";

test.describe("Smoke tests", () => {
  test("landing page loads and user is authenticated", async ({ page }) => {
    // Log in as user1 (basic user)
    await loginAs(page, "user1");

    const landing = new LandingPage(page);
    const navbar = new NavbarPage(page);

    // Verify landing page rendered
    await landing.expectLoaded();

    // Verify the ZiqReq logo is visible
    await expect(navbar.logo).toBeVisible();

    // Verify the user is authenticated — name shows in user menu
    await navbar.expectUserName(DEV_USERS.user1.displayName);
  });

  test("admin user sees all nav links", async ({ page }) => {
    // user4 has admin + user roles
    await loginAs(page, "user4");

    const navbar = new NavbarPage(page);

    await navbar.expectAdminVisible();
  });

  test("reviewer user sees reviews link", async ({ page }) => {
    // user3 has reviewer + user roles
    await loginAs(page, "user3");

    const navbar = new NavbarPage(page);

    await navbar.expectReviewsVisible();
  });

  test("regular user does not see admin link", async ({ page }) => {
    // user1 has only user role
    await loginAs(page, "user1");

    const navbar = new NavbarPage(page);

    await navbar.expectAdminHidden();
  });

  test("navigation between pages works", async ({ page }) => {
    // user4 has admin role, can access all pages
    await loginAs(page, "user4");

    // Start on landing
    await expect(page).toHaveURL("/");

    // Navigate to admin
    const navbar = new NavbarPage(page);
    await navbar.goToAdmin();
    await expect(page).toHaveURL("/admin");

    // Navigate back to landing
    await navbar.goToIdeas();
    await expect(page).toHaveURL("/");
  });
});
