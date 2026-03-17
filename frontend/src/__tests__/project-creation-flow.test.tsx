import { describe, it, expect, vi, beforeAll, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createElement } from "react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { websocketReducer } from "@/store/websocket-slice";
import { AuthContext } from "@/hooks/use-auth";
import type { AuthContextValue } from "@/hooks/use-auth";
import LandingPage from "@/pages/LandingPage";
import i18n from "@/i18n/config";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

// Mock list hooks so LandingPage renders without real fetches
vi.mock("@/hooks/use-my-projects", () => ({
  useMyProjects: vi.fn(() => ({
    data: { results: [], count: 0, next: null, previous: null },
    isLoading: false,
  })),
}));
vi.mock("@/hooks/use-collaborating-projects", () => ({
  useCollaboratingProjects: vi.fn(() => ({
    data: { results: [], count: 0, next: null, previous: null },
    isLoading: false,
  })),
}));
vi.mock("@/hooks/use-invitations", () => ({
  useInvitations: vi.fn(() => ({
    data: { invitations: [] },
    isLoading: false,
  })),
}));
vi.mock("@/hooks/use-trash", () => ({
  useTrash: vi.fn(() => ({
    data: { results: [], count: 0, next: null, previous: null },
    isLoading: false,
  })),
}));
vi.mock("@/hooks/use-delete-project", () => ({
  useDeleteProject: vi.fn(() => ({ mutate: vi.fn() })),
}));
vi.mock("@/hooks/use-restore-project", () => ({
  useRestoreProject: vi.fn(() => ({ mutate: vi.fn() })),
}));

vi.mock("react-toastify", () => ({
  toast: vi.fn(),
  ToastContainer: () => null,
}));

function createAuthValue(): AuthContextValue {
  return {
    user: {
      id: "00000000-0000-0000-0000-000000000001",
      email: "alice@dev.local",
      first_name: "Alice",
      last_name: "Admin",
      display_name: "Alice Admin",
      roles: ["admin", "reviewer", "user"],
    },
    isAuthenticated: true, isLoading: false,
    isDevBypass: true,
    hasRole: () => true,
    logout: vi.fn(),
    setUser: vi.fn(),
    getAccessToken: () => Promise.resolve(null),
  };
}

function renderLandingPage() {
  const authValue = createAuthValue();
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  const store = configureStore({
    reducer: { websocket: websocketReducer },
    preloadedState: {
      websocket: { connectionState: "online" as const, reconnectCountdown: null, isIdleDisconnected: false },
    },
  });
  return render(
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          {createElement(
            AuthContext.Provider,
            { value: authValue },
            <LandingPage />,
          )}
        </MemoryRouter>
      </QueryClientProvider>
    </Provider>,
  );
}

describe("Project creation flow (M19 — type selection)", () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("shows New Project button in hero section", () => {
    renderLandingPage();
    expect(screen.getByTestId("new-project-button")).toBeInTheDocument();
  });

  it("opens modal when New Project button is clicked", async () => {
    renderLandingPage();
    const user = userEvent.setup();

    await user.click(screen.getByTestId("new-project-button"));

    await waitFor(() => {
      expect(screen.getByTestId("new-project-modal")).toBeInTheDocument();
    });
  });

  it("submits with project_type and redirects to /project/:id", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          id: "new-project-uuid",
          title: "",
          project_type: "software",
          state: "open",
          visibility: "private",
          owner: null,
          created_at: "2026-03-17T00:00:00Z",
        }),
    });
    vi.stubGlobal("fetch", mockFetch);

    renderLandingPage();
    const user = userEvent.setup();

    await user.click(screen.getByTestId("new-project-button"));

    await waitFor(() => {
      expect(screen.getByTestId("new-project-modal")).toBeInTheDocument();
    });

    await user.click(screen.getByTestId("project-type-software"));
    await user.click(screen.getByTestId("create-project-button"));

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/project/new-project-uuid");
    });

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/projects/"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ project_type: "software" }),
      }),
    );

    vi.unstubAllGlobals();
  });
});
