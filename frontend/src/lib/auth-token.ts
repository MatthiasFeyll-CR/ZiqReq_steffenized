/**
 * Module-level access-token store.
 * The auth provider sets the token after MSAL acquisition.
 * API helpers and the WebSocket hook read it to attach Bearer headers.
 */

let _accessToken: string | null = null;

export function setAccessToken(token: string | null): void {
  _accessToken = token;
}

export function getAccessToken(): string | null {
  return _accessToken;
}

/**
 * Fetch wrapper that automatically attaches the Authorization header
 * when an access token is available. Always includes credentials for
 * dev-bypass session cookie compatibility.
 */
export function authFetch(
  url: string | URL | Request,
  init?: RequestInit,
): Promise<Response> {
  const token = _accessToken;
  if (token) {
    const headers = new Headers(init?.headers);
    if (!headers.has("Authorization")) {
      headers.set("Authorization", `Bearer ${token}`);
    }
    return fetch(url, { ...init, headers, credentials: "include" });
  }
  return fetch(url, { ...init, credentials: "include" });
}
