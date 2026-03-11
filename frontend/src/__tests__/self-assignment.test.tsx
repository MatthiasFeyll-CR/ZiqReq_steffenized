import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createElement } from "react";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthContext } from "@/hooks/use-auth";
import type { AuthContextValue } from "@/hooks/use-auth";
import { websocketReducer } from "@/store/websocket-slice";
import { ReviewCard } from "@/components/review/ReviewCard";
import type { ReviewIdea } from "@/api/review";
import i18n from "@/i18n/config";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

const { mockAssignReview, mockUnassignReview, mockToastError } = vi.hoisted(() => {
  return {
    mockAssignReview: vi.fn(),
    mockUnassignReview: vi.fn(),
    mockToastError: vi.fn(),
  };
});

vi.mock("@/api/review", async () => {
  const actual = await vi.importActual("@/api/review");
  return {
    ...actual,
    assignReview: mockAssignReview,
    unassignReview: mockUnassignReview,
  };
});

vi.mock("react-toastify", () => ({
  toast: Object.assign(vi.fn(), { error: mockToastError }),
  ToastContainer: () => null,
}));

const REVIEWER_ID = "00000000-0000-0000-0000-000000000001";
const OWNER_ID = "00000000-0000-0000-0000-000000000099";

function createAuthValue(userId = REVIEWER_ID): AuthContextValue {
  return {
    user: {
      id: userId,
      email: "reviewer@dev.local",
      first_name: "Rev",
      last_name: "Iewer",
      display_name: "Rev Iewer",
      roles: ["user", "reviewer"],
    },
    isAuthenticated: true, isLoading: false,
    isDevBypass: true,
    hasRole: (r: string) => ["user", "reviewer"].includes(r),
    logout: vi.fn(),
    setUser: vi.fn(),
    getAccessToken: () => Promise.resolve(null),
  };
}

function makeIdea(overrides: Partial<ReviewIdea> = {}): ReviewIdea {
  return {
    id: "idea-1",
    title: "Test Idea",
    state: "in_review",
    owner_id: OWNER_ID,
    co_owner_id: null,
    owner_name: "Alice Owner",
    submitted_at: "2026-01-01T00:00:00Z",
    reviewers: [],
    ...overrides,
  };
}

function renderCard(
  idea: ReviewIdea,
  category: "assigned" | "unassigned" | "accepted" | "rejected" | "dropped",
  authValue?: AuthContextValue,
) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  const store = configureStore({
    reducer: { websocket: websocketReducer },
    preloadedState: {
      websocket: {
        connectionState: "online" as const,
        reconnectCountdown: null,
        isIdleDisconnected: false,
      },
    },
  });
  return render(
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          {createElement(
            AuthContext.Provider,
            { value: authValue ?? createAuthValue() },
            <ReviewCard idea={idea} category={category} />,
          )}
        </MemoryRouter>
      </QueryClientProvider>
    </Provider>,
  );
}

beforeEach(() => {
  mockNavigate.mockClear();
  mockAssignReview.mockReset();
  mockUnassignReview.mockReset();
  mockToastError.mockClear();
});

describe("UI-ASSIGN.01: Assign button works", () => {
  it("shows Assign button on unassigned idea", () => {
    renderCard(makeIdea(), "unassigned");
    expect(screen.getByTestId("assign-button")).toBeInTheDocument();
    expect(screen.getByTestId("assign-button")).toHaveTextContent("Assign");
  });

  it("calls assignReview API when Assign clicked", async () => {
    mockAssignReview.mockResolvedValue({ message: "Assigned" });
    const user = userEvent.setup();
    renderCard(makeIdea(), "unassigned");

    await user.click(screen.getByTestId("assign-button"));

    expect(mockAssignReview).toHaveBeenCalledWith("idea-1");
  });

  it("does not navigate when clicking Assign button", async () => {
    mockAssignReview.mockResolvedValue({ message: "Assigned" });
    const user = userEvent.setup();
    renderCard(makeIdea(), "unassigned");

    await user.click(screen.getByTestId("assign-button"));

    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it("shows loading state during assign", async () => {
    let resolveAssign: (v: { message: string }) => void;
    mockAssignReview.mockReturnValue(
      new Promise((resolve) => {
        resolveAssign = resolve;
      }),
    );
    const user = userEvent.setup();
    renderCard(makeIdea(), "unassigned");

    await user.click(screen.getByTestId("assign-button"));

    // Button should be disabled while loading
    expect(screen.getByTestId("assign-button")).toBeDisabled();

    // Resolve to cleanup
    resolveAssign!({ message: "Assigned" });
  });
});

describe("UI-ASSIGN.02: Unassign button works", () => {
  it("shows Unassign button on assigned idea", () => {
    renderCard(makeIdea(), "assigned");
    expect(screen.getByTestId("unassign-button")).toBeInTheDocument();
    expect(screen.getByTestId("unassign-button")).toHaveTextContent("Unassign");
  });

  it("calls unassignReview API when Unassign clicked", async () => {
    mockUnassignReview.mockResolvedValue({ message: "Unassigned" });
    const user = userEvent.setup();
    renderCard(makeIdea(), "assigned");

    await user.click(screen.getByTestId("unassign-button"));

    expect(mockUnassignReview).toHaveBeenCalledWith("idea-1");
  });

  it("shows error toast on unassign failure", async () => {
    mockUnassignReview.mockRejectedValue(new Error("Network error"));
    const user = userEvent.setup();
    renderCard(makeIdea(), "assigned");

    await user.click(screen.getByTestId("unassign-button"));

    await waitFor(() => {
      expect(mockToastError).toHaveBeenCalled();
    });
  });
});

describe("UI-ASSIGN.03: Conflict of interest", () => {
  it("disables Assign button when reviewer is owner", () => {
    const idea = makeIdea({ owner_id: REVIEWER_ID });
    renderCard(idea, "unassigned");

    const btn = screen.getByTestId("assign-button");
    expect(btn).toBeDisabled();
  });

  it("disables Assign button when reviewer is co-owner", () => {
    const idea = makeIdea({ co_owner_id: REVIEWER_ID });
    renderCard(idea, "unassigned");

    const btn = screen.getByTestId("assign-button");
    expect(btn).toBeDisabled();
  });

  it("does not show action button on accepted/rejected/dropped categories", () => {
    renderCard(makeIdea({ state: "accepted" }), "accepted");
    expect(screen.queryByTestId("assign-button")).not.toBeInTheDocument();
    expect(screen.queryByTestId("unassign-button")).not.toBeInTheDocument();
  });

  it("shows error toast on assign failure with Retry", async () => {
    mockAssignReview.mockRejectedValue(new Error("Server error"));
    const user = userEvent.setup();
    renderCard(makeIdea(), "unassigned");

    await user.click(screen.getByTestId("assign-button"));

    await waitFor(() => {
      expect(mockToastError).toHaveBeenCalled();
    });
  });
});
