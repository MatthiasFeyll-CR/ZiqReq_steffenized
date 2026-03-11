import { describe, it, expect, vi, beforeAll } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { Provider as ReduxProvider } from "react-redux";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { configureStore } from "@reduxjs/toolkit";
import AdminPanel from "@/pages/admin-panel";
import { AuthContext, type AuthContextValue } from "@/hooks/use-auth";
import { uiReducer } from "@/store/ui-slice";
import { websocketReducer } from "@/store/websocket-slice";
import { presenceReducer } from "@/store/presence-slice";
import { selectionsReducer } from "@/store/selections-slice";
import { boardReducer } from "@/store/board-slice";
import { rateLimitReducer } from "@/store/rate-limit-slice";
import i18n from "@/i18n/config";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

function makeStore() {
  return configureStore({
    reducer: {
      board: boardReducer,
      websocket: websocketReducer,
      presence: presenceReducer,
      selections: selectionsReducer,
      ui: uiReducer,
      rateLimit: rateLimitReducer,
    },
  });
}

function makeAuth(overrides: Partial<AuthContextValue> = {}): AuthContextValue {
  return {
    user: {
      id: "user-1",
      email: "admin@test.com",
      first_name: "Admin",
      last_name: "User",
      display_name: "Admin User",
      roles: ["admin"],
    },
    isAuthenticated: true,
    isDevBypass: false,
    hasRole: (role: string) => ["admin"].includes(role),
    logout: vi.fn(),
    setUser: vi.fn(),
    ...overrides,
  };
}

function renderAdminPanel(authOverrides: Partial<AuthContextValue> = {}) {
  const auth = makeAuth(authOverrides);
  const store = makeStore();
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <ReduxProvider store={store}>
      <QueryClientProvider client={queryClient}>
        <AuthContext.Provider value={auth}>
          <MemoryRouter initialEntries={["/admin"]}>
            <AdminPanel />
          </MemoryRouter>
        </AuthContext.Provider>
      </QueryClientProvider>
    </ReduxProvider>,
  );
}

describe("AdminPanel — UI-ADMIN.01: 4 tabs render", () => {
  it("renders all 4 tabs with correct labels", () => {
    renderAdminPanel();
    expect(screen.getByRole("tab", { name: /AI Context/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /Parameters/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /Monitoring/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /Users/i })).toBeInTheDocument();
  });

  it("defaults to AI Context tab as active", () => {
    renderAdminPanel();
    const aiTab = screen.getByRole("tab", { name: /AI Context/i });
    expect(aiTab).toHaveAttribute("data-state", "active");
  });

  it("switches tabs without page reload on click", async () => {
    renderAdminPanel();
    const user = userEvent.setup();

    const parametersTab = screen.getByRole("tab", { name: /Parameters/i });
    await user.click(parametersTab);
    expect(parametersTab).toHaveAttribute("data-state", "active");

    const aiTab = screen.getByRole("tab", { name: /AI Context/i });
    expect(aiTab).toHaveAttribute("data-state", "inactive");
  });

  it("renders tab content when tab is selected", async () => {
    renderAdminPanel();
    const user = userEvent.setup();

    expect(screen.getByText("AI Context management")).toBeInTheDocument();

    await user.click(screen.getByRole("tab", { name: /Parameters/i }));
    expect(screen.getByText("Parameters management")).toBeInTheDocument();

    await user.click(screen.getByRole("tab", { name: /Monitoring/i }));
    expect(screen.getByText("Monitoring dashboard")).toBeInTheDocument();

    await user.click(screen.getByRole("tab", { name: /Users/i }));
    expect(screen.getByText("User search")).toBeInTheDocument();
  });
});

describe("AdminPanel — UI-ADMIN.04: Non-admin access denied", () => {
  it("redirects non-admin users (does not render tabs)", () => {
    renderAdminPanel({
      user: {
        id: "user-2",
        email: "user@test.com",
        first_name: "Regular",
        last_name: "User",
        display_name: "Regular User",
        roles: ["user"],
      },
      hasRole: (role: string) => ["user"].includes(role),
    });

    expect(screen.queryByRole("tab", { name: /AI Context/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("tab", { name: /Parameters/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("tab", { name: /Monitoring/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("tab", { name: /Users/i })).not.toBeInTheDocument();
  });
});
