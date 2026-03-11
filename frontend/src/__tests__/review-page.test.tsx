import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createElement } from "react";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthContext } from "@/hooks/use-auth";
import type { AuthContextValue } from "@/hooks/use-auth";
import { websocketReducer } from "@/store/websocket-slice";
import ReviewPage from "@/pages/review-page";
import i18n from "@/i18n/config";
import type { ReviewListResponse } from "@/api/review";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

vi.mock("react-toastify", () => ({
  toast: Object.assign(vi.fn(), { error: vi.fn() }),
  ToastContainer: () => null,
}));

const { mockFetchReviews } = vi.hoisted(() => {
  return { mockFetchReviews: vi.fn() };
});

vi.mock("@/api/review", async () => {
  const actual = await vi.importActual("@/api/review");
  return { ...actual, fetchReviews: mockFetchReviews };
});

function createAuthValue(): AuthContextValue {
  return {
    user: {
      id: "00000000-0000-0000-0000-000000000001",
      email: "reviewer@dev.local",
      first_name: "Rev",
      last_name: "Iewer",
      display_name: "Rev Iewer",
      roles: ["user", "reviewer"],
    },
    isAuthenticated: true,
    isDevBypass: true,
    hasRole: (r: string) => ["user", "reviewer"].includes(r),
    logout: vi.fn(),
    setUser: vi.fn(),
  };
}

const emptyResponse: ReviewListResponse = {
  assigned_to_me: [],
  unassigned: [],
  accepted: [],
  rejected: [],
  dropped: [],
};

function renderReviewPage(fetchResult: ReviewListResponse = emptyResponse) {
  mockFetchReviews.mockResolvedValue(fetchResult);
  const authValue = createAuthValue();
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  const store = configureStore({
    reducer: { websocket: websocketReducer },
    preloadedState: {
      websocket: {
        connectionState: "online" as const,
        reconnectCountdown: null,
      },
    },
  });
  return render(
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/reviews"]}>
          {createElement(
            AuthContext.Provider,
            { value: authValue },
            <ReviewPage />,
          )}
        </MemoryRouter>
      </QueryClientProvider>
    </Provider>,
  );
}

beforeEach(() => {
  mockNavigate.mockClear();
  mockFetchReviews?.mockReset();
});

describe("T-10.2.02: Categories render with counts", () => {
  it("renders all 5 category headers", async () => {
    renderReviewPage();

    expect(await screen.findByText("Assigned to me")).toBeInTheDocument();
    expect(screen.getByText("Unassigned")).toBeInTheDocument();
    expect(screen.getByText("Accepted")).toBeInTheDocument();
    expect(screen.getByText("Rejected")).toBeInTheDocument();
    expect(screen.getByText("Dropped")).toBeInTheDocument();
  });

  it("renders counts for categories with data", async () => {
    const data: ReviewListResponse = {
      assigned_to_me: [
        { id: "1", title: "Idea A", state: "in_review", owner_name: "Alice", submitted_at: "2026-01-01T00:00:00Z", reviewers: [] },
        { id: "2", title: "Idea B", state: "in_review", owner_name: "Bob", submitted_at: "2026-01-02T00:00:00Z", reviewers: [] },
      ],
      unassigned: [
        { id: "3", title: "Idea C", state: "in_review", owner_name: "Charlie", submitted_at: "2026-01-03T00:00:00Z", reviewers: [] },
      ],
      accepted: [],
      rejected: [],
      dropped: [],
    };

    renderReviewPage(data);

    // Wait for data to load
    expect(await screen.findByText("Idea A")).toBeInTheDocument();

    // Check counts
    expect(screen.getByText("2")).toBeInTheDocument(); // assigned_to_me
    expect(screen.getByText("1")).toBeInTheDocument(); // unassigned
  });

  it("renders ReviewCard for each idea in a category", async () => {
    const data: ReviewListResponse = {
      ...emptyResponse,
      assigned_to_me: [
        { id: "1", title: "Review This", state: "in_review", owner_name: "Alice", submitted_at: "2026-01-01T00:00:00Z", reviewers: [{ id: "r1", display_name: "Rev" }] },
      ],
    };

    renderReviewPage(data);

    expect(await screen.findByText("Review This")).toBeInTheDocument();
    expect(screen.getByText(/by Alice/)).toBeInTheDocument();
  });
});

describe("T-10.2.03: Collapsible categories", () => {
  it("Assigned and Unassigned are expanded by default, others collapsed", async () => {
    renderReviewPage();

    // Wait for render
    expect(await screen.findByText("Assigned to me")).toBeInTheDocument();

    // Assigned and Unassigned should show empty states (expanded)
    expect(screen.getByText("No assigned to me ideas")).toBeInTheDocument();
    expect(screen.getByText("No unassigned ideas")).toBeInTheDocument();

    // Accepted, Rejected, Dropped should be collapsed — their empty states should NOT be visible
    expect(screen.queryByText("No accepted ideas")).not.toBeInTheDocument();
    expect(screen.queryByText("No rejected ideas")).not.toBeInTheDocument();
    expect(screen.queryByText("No dropped ideas")).not.toBeInTheDocument();
  });

  it("clicking a collapsed category expands it", async () => {
    const user = userEvent.setup();
    renderReviewPage();

    expect(await screen.findByText("Accepted")).toBeInTheDocument();

    // Accepted is collapsed — no empty state
    expect(screen.queryByText("No accepted ideas")).not.toBeInTheDocument();

    // Click to expand
    await user.click(screen.getByText("Accepted"));

    // Now empty state should show
    expect(screen.getByText("No accepted ideas")).toBeInTheDocument();
  });

  it("clicking an expanded category collapses it", async () => {
    const user = userEvent.setup();
    renderReviewPage();

    expect(await screen.findByText("Assigned to me")).toBeInTheDocument();

    // Assigned is expanded
    expect(screen.getByText("No assigned to me ideas")).toBeInTheDocument();

    // Click to collapse
    await user.click(screen.getByText("Assigned to me"));

    // Empty state should disappear
    expect(screen.queryByText("No assigned to me ideas")).not.toBeInTheDocument();
  });
});

describe("UI-REVIEW.01: Review page uses PageShell with Navbar", () => {
  it("renders with Navbar (ZiqReq logo visible)", async () => {
    renderReviewPage();

    expect(await screen.findByText("ZiqReq")).toBeInTheDocument();
  });

  it("renders page heading", async () => {
    renderReviewPage();

    expect(await screen.findByRole("heading", { name: "Reviews" })).toBeInTheDocument();
    expect(screen.getByText("Manage ideas submitted for your review")).toBeInTheDocument();
  });
});

describe("UI-REVIEW.02: Empty state for each category", () => {
  it("shows empty state message for expanded empty categories", async () => {
    renderReviewPage();

    expect(await screen.findByText("No assigned to me ideas")).toBeInTheDocument();
    expect(screen.getByText("No unassigned ideas")).toBeInTheDocument();
  });
});
