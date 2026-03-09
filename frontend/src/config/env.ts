export const env = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? "/api",
  wsBaseUrl: import.meta.env.VITE_WS_BASE_URL ?? "/ws",
  azureAdClientId: import.meta.env.VITE_AZURE_AD_CLIENT_ID ?? "",
  azureAdTenantId: import.meta.env.VITE_AZURE_AD_TENANT_ID ?? "",
  authBypass: import.meta.env.VITE_AUTH_BYPASS === "true",
} as const;
