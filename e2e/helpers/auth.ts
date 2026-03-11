import { type Page } from "@playwright/test";

/**
 * Base URL for API calls — goes through the Vite proxy so cookies
 * stay on the same origin as the page (localhost:5173).
 */
const BASE_URL = process.env.BASE_URL ?? "http://localhost:5173";

/**
 * Dev users available in AUTH_BYPASS mode.
 * Must match the seed migration: services/gateway/apps/authentication/migrations/0002_seed_dev_users.py
 *
 * User1: basic user
 * User2: basic user
 * User3: user + reviewer
 * User4: user + admin
 */
export const DEV_USERS = {
  user1: {
    id: "00000000-0000-0000-0000-000000000001",
    email: "dev1@ziqreq.local",
    displayName: "Dev User 1",
    roles: ["user"],
  },
  user2: {
    id: "00000000-0000-0000-0000-000000000002",
    email: "dev2@ziqreq.local",
    displayName: "Dev User 2",
    roles: ["user"],
  },
  user3: {
    id: "00000000-0000-0000-0000-000000000003",
    email: "dev3@ziqreq.local",
    displayName: "Dev User 3",
    roles: ["user", "reviewer"],
  },
  user4: {
    id: "00000000-0000-0000-0000-000000000004",
    email: "dev4@ziqreq.local",
    displayName: "Dev User 4",
    roles: ["user", "admin"],
  },
} as const;

export type DevUserKey = keyof typeof DEV_USERS;

/**
 * Log in as a dev user by calling the dev-login endpoint through the
 * Vite proxy (/api/auth/dev-login on localhost:5173). This ensures the
 * session cookie is set on the same origin as the page, so subsequent
 * frontend fetch() calls to /api/auth/me include the cookie.
 */
export async function loginAs(page: Page, user: DevUserKey): Promise<void> {
  const devUser = DEV_USERS[user];

  // Call dev-login through the Vite proxy (same origin as the page)
  const response = await page.request.post(`${BASE_URL}/api/auth/dev-login`, {
    data: { user_id: devUser.id },
  });

  if (!response.ok()) {
    throw new Error(
      `dev-login failed for ${user}: ${response.status()} ${await response.text()}`,
    );
  }

  // Navigate to root — the frontend will call GET /api/auth/me
  // and pick up the session, rendering the authenticated layout
  await page.goto("/");
  await page.waitForLoadState("networkidle");
}

/**
 * Switch to a different dev user mid-test by calling the dev-switch
 * endpoint through the Vite proxy, then reloading the page.
 */
export async function switchUser(page: Page, user: DevUserKey): Promise<void> {
  const devUser = DEV_USERS[user];

  const response = await page.request.post(`${BASE_URL}/api/auth/dev-switch`, {
    data: { user_id: devUser.id },
  });

  if (!response.ok()) {
    throw new Error(
      `dev-switch failed for ${user}: ${response.status()} ${await response.text()}`,
    );
  }

  await page.reload();
  await page.waitForLoadState("networkidle");
}
