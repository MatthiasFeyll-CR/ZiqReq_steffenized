export default async function globalTeardown(): Promise<void> {
  console.log("\nE2E Global Teardown");
  console.log("─".repeat(40));
  // Cleanup is handled by tearing down docker-compose.e2e.yml.
  // Test-specific data cleanup happens in individual test afterEach/afterAll hooks.
  console.log("  No teardown actions required.");
  console.log("─".repeat(40));
}
