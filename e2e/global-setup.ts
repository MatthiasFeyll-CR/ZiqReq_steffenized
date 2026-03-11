const GATEWAY_URL = process.env.GATEWAY_URL ?? "http://localhost:8000";
const FRONTEND_URL = process.env.FRONTEND_URL ?? "http://localhost:5173";
const POLL_INTERVAL_MS = 2_000;
const MAX_WAIT_MS = 120_000;

async function waitForUrl(url: string, label: string): Promise<void> {
  const start = Date.now();
  while (Date.now() - start < MAX_WAIT_MS) {
    try {
      const res = await fetch(url, { signal: AbortSignal.timeout(5_000) });
      if (res.ok) {
        console.log(`  [ready] ${label} (${url})`);
        return;
      }
    } catch {
      // not ready yet
    }
    await new Promise((r) => setTimeout(r, POLL_INTERVAL_MS));
  }
  throw new Error(`Timed out waiting for ${label} at ${url} after ${MAX_WAIT_MS / 1000}s`);
}

async function seedDevUsers(): Promise<void> {
  try {
    const res = await fetch(`${GATEWAY_URL}/api/auth/dev-users`);
    if (res.ok) {
      const data = (await res.json()) as { users: unknown[] };
      console.log(`  [seed] ${data.users.length} dev users available`);
    } else {
      console.warn("  [seed] dev-users endpoint returned", res.status);
    }
  } catch (err) {
    console.warn("  [seed] Could not reach dev-users endpoint:", err);
  }
}

export default async function globalSetup(): Promise<void> {
  console.log("\nE2E Global Setup");
  console.log("─".repeat(40));

  // Wait for backend gateway (serves API + WebSocket)
  await waitForUrl(`${GATEWAY_URL}/api/auth/dev-users`, "Gateway API");

  // Wait for frontend dev server
  await waitForUrl(FRONTEND_URL, "Frontend");

  // Verify dev users are seeded and accessible
  await seedDevUsers();

  console.log("─".repeat(40));
  console.log("All services ready. Running tests.\n");
}
