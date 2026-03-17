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

describe("T-9.2.01: Create idea from landing page", () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("captures first message text in hero input", async () => {
    renderLandingPage();
    const user = userEvent.setup();

    const textarea = screen.getByPlaceholderText("Describe your idea...");
    await user.type(textarea, "My brilliant idea");
    expect(textarea).toHaveValue("My brilliant idea");
  });

  it("shows validation error when submitting empty input", async () => {
    renderLandingPage();
    const user = userEvent.setup();

    const submitBtn = screen.getByText("Begin");
    await user.click(submitBtn);

    expect(
      screen.getByText("Please describe your idea before submitting."),
    ).toBeInTheDocument();
  });

  it("clears validation error when user starts typing", async () => {
    renderLandingPage();
    const user = userEvent.setup();

    await user.click(screen.getByText("Begin"));
    expect(
      screen.getByText("Please describe your idea before submitting."),
    ).toBeInTheDocument();

    const textarea = screen.getByPlaceholderText("Describe your idea...");
    await user.type(textarea, "a");

    expect(
      screen.queryByText("Please describe your idea before submitting."),
    ).not.toBeInTheDocument();
  });

  it("submits and redirects to /project/:uuid on success", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          id: "new-idea-uuid",
          title: "",
          state: "open",
          visibility: "private",
          agent_mode: "interactive",
          owner: null,
          created_at: "2024-01-01T00:00:00Z",
        }),
    });
    vi.stubGlobal("fetch", mockFetch);

    renderLandingPage();
    const user = userEvent.setup();

    const textarea = screen.getByPlaceholderText("Describe your idea...");
    await user.type(textarea, "My idea");
    await user.click(screen.getByText("Begin"));

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/project/new-idea-uuid");
    });

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/projects/"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ first_message: "My idea" }),
      }),
    );
  });

  it("shows error toast with retry button on API failure", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: () => Promise.resolve({ message: "Internal server error" }),
    });
    vi.stubGlobal("fetch", mockFetch);

    renderLandingPage();
    const user = userEvent.setup();

    const textarea = screen.getByPlaceholderText("Describe your idea...");
    await user.type(textarea, "My idea");
    await user.click(screen.getByText("Begin"));

    await waitFor(() => {
      expect(
        screen.getByText("Failed to create idea. Please try again."),
      ).toBeInTheDocument();
    });

    // Retry button is present
    expect(screen.getByText("Retry")).toBeInTheDocument();
  });

  it("disables submit button during API call", async () => {
    let resolveFetch: (value: unknown) => void;
    const fetchPromise = new Promise((resolve) => {
      resolveFetch = resolve;
    });
    const mockFetch = vi.fn().mockReturnValue(fetchPromise);
    vi.stubGlobal("fetch", mockFetch);

    renderLandingPage();
    const user = userEvent.setup();

    const textarea = screen.getByPlaceholderText("Describe your idea...");
    await user.type(textarea, "My idea");
    await user.click(screen.getByText("Begin"));

    await waitFor(() => {
      const submitBtn = screen.getByText("Begin").closest("button");
      expect(submitBtn).toBeDisabled();
    });

    // Resolve the fetch to cleanup
    resolveFetch!({
      ok: true,
      json: () =>
        Promise.resolve({ id: "test-id", title: "", state: "open" }),
    });
  });
});
