import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { createElement } from "react";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthContext } from "@/hooks/use-auth";
import type { AuthUser, AuthContextValue } from "@/hooks/use-auth";
import { DevUserSwitcher } from "@/components/auth/DevUserSwitcher";
import { Navbar } from "@/components/layout/Navbar";
import { websocketReducer } from "@/store/websocket-slice";
import { MemoryRouter } from "react-router-dom";
import "@/i18n/config";

const DEV_USERS = [
  {
    id: "00000000-0000-0000-0000-000000000001",
    email: "alice@dev.local",
    first_name: "Alice",
    last_name: "Admin",
    display_name: "Alice Admin",
    roles: ["admin", "reviewer", "user"],
  },
  {
    id: "00000000-0000-0000-0000-000000000002",
    email: "bob@dev.local",
    first_name: "Bob",
    last_name: "Reviewer",
    display_name: "Bob Reviewer",
    roles: ["reviewer", "user"],
  },
];

// Mock fetch to return dev users from API
vi.stubGlobal(
  "fetch",
  vi.fn(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve(DEV_USERS),
    }),
  ),
);

function createAuthValue(overrides: Partial<AuthContextValue> = {}): AuthContextValue {
  return {
    user: null,
    isAuthenticated: false,
    isDevBypass: true,
    hasRole: (role: string) => overrides.user?.roles.includes(role) ?? false,
    logout: vi.fn(),
    setUser: vi.fn(),
    getAccessToken: () => Promise.resolve(null),
    ...overrides,
  };
}

function renderWithAuth(ui: React.ReactNode, authValue: AuthContextValue) {
  const store = configureStore({
    reducer: { websocket: websocketReducer },
    preloadedState: { websocket: { connectionState: "online" as const, reconnectCountdown: null, isIdleDisconnected: false } },
  });
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <Provider store={store}>
        <MemoryRouter>
          {createElement(AuthContext.Provider, { value: authValue }, ui)}
        </MemoryRouter>
      </Provider>
    </QueryClientProvider>,
  );
}

describe("T-7.1.04: Dev login flow end-to-end", () => {
  let authValue: AuthContextValue;
  let currentUser: AuthUser | null;

  beforeEach(() => {
    currentUser = null;
    vi.clearAllMocks();

    // Re-stub fetch for each test
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(DEV_USERS),
        }),
      ),
    );

    authValue = createAuthValue({
      get user() {
        return currentUser;
      },
      get isAuthenticated() {
        return currentUser !== null;
      },
      hasRole: (role: string) => currentUser?.roles.includes(role) ?? false,
      setUser: vi.fn((u: AuthUser | null) => {
        currentUser = u;
      }),
    });
  });

  it("renders dev user switcher with available dev users", async () => {
    renderWithAuth(<DevUserSwitcher />, authValue);

    // Wait for dev users to load (from mocked fetch or fallback)
    const aliceButton = await screen.findByText("Alice Admin");
    expect(aliceButton).toBeInTheDocument();

    const bobButton = await screen.findByText("Bob Reviewer");
    expect(bobButton).toBeInTheDocument();
  });

  it("selects a dev user and calls setUser with user data", async () => {
    renderWithAuth(<DevUserSwitcher />, authValue);

    const aliceButton = await screen.findByText("Alice Admin");
    fireEvent.click(aliceButton);

    expect(authValue.setUser).toHaveBeenCalledWith(
      expect.objectContaining({
        id: "00000000-0000-0000-0000-000000000001",
        display_name: "Alice Admin",
        roles: ["admin", "reviewer", "user"],
      }),
    );
  });

  it("user identity visible in navbar after selecting dev user", async () => {
    // Simulate user already selected
    currentUser = DEV_USERS[0] as AuthUser;
    const selectedAuth = createAuthValue({
      user: currentUser,
      isAuthenticated: true,
      hasRole: (role: string) => currentUser?.roles.includes(role) ?? false,
    });

    renderWithAuth(
      <>
        <Navbar />
        <DevUserSwitcher />
      </>,
      selectedAuth,
    );

    // The user's initials (AA for Alice Admin) should be visible in the navbar avatar
    expect(screen.getByText("AA")).toBeInTheDocument();

    // The display name should be visible in the dev user switcher (highlighted as selected)
    const aliceButton = await screen.findByText("Alice Admin");
    expect(aliceButton).toBeInTheDocument();
  });

  it("does not render dev user switcher when dev bypass is disabled", () => {
    const nonDevAuth = createAuthValue({ isDevBypass: false });
    renderWithAuth(<DevUserSwitcher />, nonDevAuth);

    // The switcher label should not be present
    expect(screen.queryByText("Alice Admin")).not.toBeInTheDocument();
  });
});
