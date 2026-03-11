import { type Page } from "@playwright/test";

const GATEWAY_URL = process.env.GATEWAY_URL ?? "http://localhost:8000";

/**
 * Dev users available in AUTH_BYPASS mode.
 * IDs match the hardcoded fallbacks in DevUserSwitcher.tsx.
 */
export const DEV_USERS = {
  alice: {
    id: "00000000-0000-0000-0000-000000000001",
    email: "alice@dev.local",
    displayName: "Alice Admin",
    roles: ["admin", "reviewer", "user"],
  },
  bob: {
    id: "00000000-0000-0000-0000-000000000002",
    email: "bob@dev.local",
    displayName: "Bob Reviewer",
    roles: ["reviewer", "user"],
  },
  carol: {
    id: "00000000-0000-0000-0000-000000000003",
    email: "carol@dev.local",
    displayName: "Carol User",
    roles: ["user"],
  },
  dave: {
    id: "00000000-0000-0000-0000-000000000004",
    email: "dave@dev.local",
    displayName: "Dave User",
    roles: ["user"],
  },
} as const;

export type DevUserKey = keyof typeof DEV_USERS;

/**
 * Log in as a dev user by calling the backend dev-login endpoint,
 * which sets a Django session cookie. Then navigate to the app so
 * the frontend picks up the session via GET /api/auth/me.
 */
export async function loginAs(page: Page, user: DevUserKey): Promise<void> {
  const devUser = DEV_USERS[user];

  // Call dev-login to establish a backend session cookie
  const response = await page.request.post(`${GATEWAY_URL}/api/auth/dev-login`, {
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
 * Switch to a different dev user mid-test by calling the backend
 * dev-switch endpoint, then reloading the page.
 */
export async function switchUser(page: Page, user: DevUserKey): Promise<void> {
  const devUser = DEV_USERS[user];

  const response = await page.request.post(`${GATEWAY_URL}/api/auth/dev-switch`, {
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
