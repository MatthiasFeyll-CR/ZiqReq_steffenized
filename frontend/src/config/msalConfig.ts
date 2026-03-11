import { PublicClientApplication, LogLevel } from "@azure/msal-browser";
import type { Configuration } from "@azure/msal-browser";
import { env } from "./env";

const msalConfig: Configuration = {
  auth: {
    clientId: env.azureAdClientId,
    authority: `https://login.microsoftonline.com/${env.azureAdTenantId}`,
    redirectUri: window.location.origin,
    postLogoutRedirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: "localStorage",
  },
  system: {
    loggerOptions: {
      logLevel: LogLevel.Warning,
      loggerCallback: (_level, message) => {
        console.debug(`[MSAL] ${message}`);
      },
    },
  },
};

export const msalInstance = new PublicClientApplication(msalConfig);

export const loginRequest = {
  scopes: [`api://${env.azureAdClientId}/access_as_user`],
};
