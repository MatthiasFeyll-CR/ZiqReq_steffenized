import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement } from "react";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { websocketReducer } from "@/store/websocket-slice";
import { AuthContext } from "@/hooks/use-auth";
import type { AuthContextValue } from "@/hooks/use-auth";
import { FilterBar } from "@/components/landing/FilterBar";
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

const mockDeleteMutate = vi.fn();
const mockRestoreMutate = vi.fn();

vi.mock("@/hooks/use-my-projects", () => ({
  useMyProjects: vi.fn(() => ({ data: null, isLoading: false })),
}));
vi.mock("@/hooks/use-collaborating-projects", () => ({
  useCollaboratingProjects: vi.fn(() => ({ data: null, isLoading: false })),
}));
vi.mock("@/hooks/use-invitations", () => ({
  useInvitations: vi.fn(() => ({ data: null, isLoading: false })),
}));
vi.mock("@/hooks/use-trash", () => ({
  useTrash: vi.fn(() => ({ data: null, isLoading: false })),
}));
vi.mock("@/hooks/use-delete-project", () => ({
  useDeleteProject: vi.fn(() => ({ mutate: mockDeleteMutate })),
}));
vi.mock("@/hooks/use-restore-project", () => ({
  useRestoreProject: vi.fn(() => ({ mutate: mockRestoreMutate })),
}));

vi.mock("react-toastify", () => ({
  toast: vi.fn(),
  ToastContainer: () => null,
}));

import { useMyProjects } from "@/hooks/use-my-projects";
import { useCollaboratingProjects } from "@/hooks/use-collaborating-projects";
import { useInvitations } from "@/hooks/use-invitations";
import { useTrash } from "@/hooks/use-trash";

function mockHook(data: unknown, isLoading = false) {
  return { data, isLoading } as never;
}

const emptyProjectsResponse = {
  results: [],
  count: 0,
  next: null,
  previous: null,
};
const emptyInvitationsResponse = { invitations: [] };

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

beforeEach(() => {
  vi.mocked(useMyProjects).mockReturnValue(mockHook(emptyProjectsResponse));
  vi.mocked(useCollaboratingProjects).mockReturnValue(
    mockHook(emptyProjectsResponse),
  );
  vi.mocked(useInvitations).mockReturnValue(
    mockHook(emptyInvitationsResponse),
  );
  vi.mocked(useTrash).mockReturnValue(mockHook(emptyProjectsResponse));
  mockNavigate.mockClear();
  mockDeleteMutate.mockClear();
  mockRestoreMutate.mockClear();
});

describe("FilterBar component (controlled)", () => {
  const defaultProps = {
    searchInput: "",
    onSearchChange: vi.fn(),
    stateFilter: "",
    onStateChange: vi.fn(),
    ownershipFilter: "",
    onOwnershipChange: vi.fn(),
    hasActiveFilters: false,
    onClear: vi.fn(),
  };

  function renderFilterBar(overrides = {}) {
    const props = { ...defaultProps, ...overrides };
    return render(
      <MemoryRouter>
        <FilterBar {...props} />
      </MemoryRouter>,
    );
  }

  it("renders search input with placeholder", () => {
    renderFilterBar();
    expect(
      screen.getByPlaceholderText("Search projects by title..."),
    ).toBeInTheDocument();
  });

  it("renders state filter dropdown with All states option", () => {
    renderFilterBar();
    expect(screen.getByText("All states")).toBeInTheDocument();
  });

  it("renders ownership filter dropdown with All projects option", () => {
    renderFilterBar();
    expect(screen.getByText("All projects")).toBeInTheDocument();
  });

  it("calls onSearchChange when typing in search input", () => {
    const onSearchChange = vi.fn();
    renderFilterBar({ onSearchChange });

    const input = screen.getByPlaceholderText("Search projects by title...");
    fireEvent.change(input, { target: { value: "test" } });

    expect(onSearchChange).toHaveBeenCalledWith("test");
  });

  it("shows clear search (X) button when searchInput has value", () => {
    renderFilterBar({ searchInput: "hello" });
    expect(screen.getByLabelText("Clear search")).toBeInTheDocument();
  });

  it("does not show clear search button when input is empty", () => {
    renderFilterBar({ searchInput: "" });
    expect(screen.queryByLabelText("Clear search")).not.toBeInTheDocument();
  });

  it("calls onSearchChange('') when clear search button is clicked", async () => {
    const onSearchChange = vi.fn();
    const user = userEvent.setup();
    renderFilterBar({ searchInput: "hello", onSearchChange });

    await user.click(screen.getByLabelText("Clear search"));
    expect(onSearchChange).toHaveBeenCalledWith("");
  });

  it("does not show 'Clear filters' button when hasActiveFilters is false", () => {
    renderFilterBar({ hasActiveFilters: false });
    expect(screen.queryByText("Clear filters")).not.toBeInTheDocument();
  });

  it("shows 'Clear filters' button when hasActiveFilters is true", () => {
    renderFilterBar({ hasActiveFilters: true });
    expect(screen.getByText("Clear filters")).toBeInTheDocument();
  });

  it("calls onClear when 'Clear filters' button is clicked", async () => {
    const onClear = vi.fn();
    const user = userEvent.setup();
    renderFilterBar({ hasActiveFilters: true, onClear });

    await user.click(screen.getByText("Clear filters"));
    expect(onClear).toHaveBeenCalled();
  });
});

describe("T-9.4.01 / T-9.4.02: FilterBar integration with LandingPage", () => {
  it("renders FilterBar on the landing page", () => {
    renderLandingPage();
    expect(
      screen.getByPlaceholderText("Search projects by title..."),
    ).toBeInTheDocument();
    expect(screen.getByText("All states")).toBeInTheDocument();
    expect(screen.getByText("All projects")).toBeInTheDocument();
  });

  it("debounces search and passes filters to useMyProjects", async () => {
    vi.useFakeTimers();

    renderLandingPage();

    const searchInput = screen.getByPlaceholderText(
      "Search projects by title...",
    );

    // Use fireEvent.change to avoid userEvent timing issues
    fireEvent.change(searchInput, { target: { value: "test" } });

    // Before debounce fires, search should not be in filters
    const callsBefore = vi.mocked(useMyProjects).mock.calls;
    const lastCallBefore = callsBefore[callsBefore.length - 1]!;
    expect(lastCallBefore[0]?.search || "").toBe("");

    // Advance past debounce (300ms)
    await act(async () => {
      vi.advanceTimersByTime(350);
    });

    // After debounce, useMyProjects should be called with search param
    const callsAfter = vi.mocked(useMyProjects).mock.calls;
    const lastCallAfter = callsAfter[callsAfter.length - 1]!;
    expect(lastCallAfter[0]?.search).toBe("test");

    vi.useRealTimers();
  });

  it("shows 'Clear filters' after debounced search", async () => {
    vi.useFakeTimers();

    renderLandingPage();

    const searchInput = screen.getByPlaceholderText(
      "Search projects by title...",
    );
    fireEvent.change(searchInput, { target: { value: "test" } });

    await act(async () => {
      vi.advanceTimersByTime(350);
    });

    expect(screen.getByText("Clear filters")).toBeInTheDocument();

    vi.useRealTimers();
  });
});
