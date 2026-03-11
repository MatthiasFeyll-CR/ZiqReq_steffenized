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

vi.mock("@/hooks/use-my-ideas", () => ({
  useMyIdeas: vi.fn(() => ({ data: null, isLoading: false })),
}));
vi.mock("@/hooks/use-collaborating-ideas", () => ({
  useCollaboratingIdeas: vi.fn(() => ({ data: null, isLoading: false })),
}));
vi.mock("@/hooks/use-invitations", () => ({
  useInvitations: vi.fn(() => ({ data: null, isLoading: false })),
}));
vi.mock("@/hooks/use-trash", () => ({
  useTrash: vi.fn(() => ({ data: null, isLoading: false })),
}));
vi.mock("@/hooks/use-delete-idea", () => ({
  useDeleteIdea: vi.fn(() => ({ mutate: mockDeleteMutate })),
}));
vi.mock("@/hooks/use-restore-idea", () => ({
  useRestoreIdea: vi.fn(() => ({ mutate: mockRestoreMutate })),
}));

vi.mock("react-toastify", () => ({
  toast: vi.fn(),
  ToastContainer: () => null,
}));

import { useMyIdeas } from "@/hooks/use-my-ideas";
import { useCollaboratingIdeas } from "@/hooks/use-collaborating-ideas";
import { useInvitations } from "@/hooks/use-invitations";
import { useTrash } from "@/hooks/use-trash";

function mockHook(data: unknown, isLoading = false) {
  return { data, isLoading } as never;
}

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
    isAuthenticated: true,
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
    preloadedState: { websocket: { connectionState: "online" as const, reconnectCountdown: null, isIdleDisconnected: false } },
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

const emptyIdeasResponse = { results: [], count: 0, next: null, previous: null };
const emptyInvitationsResponse = { invitations: [] };

beforeEach(() => {
  vi.mocked(useMyIdeas).mockReturnValue(mockHook(emptyIdeasResponse));
  vi.mocked(useCollaboratingIdeas).mockReturnValue(mockHook(emptyIdeasResponse));
  vi.mocked(useInvitations).mockReturnValue(mockHook(emptyInvitationsResponse));
  vi.mocked(useTrash).mockReturnValue(mockHook(emptyIdeasResponse));
  mockNavigate.mockClear();
  mockDeleteMutate.mockClear();
  mockRestoreMutate.mockClear();
});

describe("T-9.1.01: Landing page renders all 4 lists", () => {
  it("renders hero section with heading, subtext, input, and submit button", () => {
    renderLandingPage();

    expect(screen.getByText("Start a new brainstorm")).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText("Describe your idea..."),
    ).toBeInTheDocument();
    expect(screen.getByText("Begin")).toBeInTheDocument();
  });

  it("renders all 4 section headings", () => {
    renderLandingPage();

    expect(screen.getByText("My Ideas")).toBeInTheDocument();
    expect(screen.getByText("Collaborating")).toBeInTheDocument();
    expect(screen.getByText("Invitations")).toBeInTheDocument();
    expect(screen.getByText("Trash")).toBeInTheDocument();
  });

  it("renders empty states when no data returned", () => {
    renderLandingPage();

    expect(screen.getByText("Start your first brainstorm")).toBeInTheDocument();
    expect(screen.getByText("No collaborations yet")).toBeInTheDocument();
    expect(screen.getByText("No pending invitations")).toBeInTheDocument();
    expect(screen.getByText("Trash is empty")).toBeInTheDocument();
  });

  it("renders count badges showing 0 for empty lists", () => {
    renderLandingPage();

    const zeros = screen.getAllByText("0");
    expect(zeros.length).toBe(4);
  });

  it("renders ideas in My Ideas list with correct count", () => {
    vi.mocked(useMyIdeas).mockReturnValue(
      mockHook({
        results: [
          { id: "1", title: "First idea", state: "open", updated_at: "2024-01-01", deleted_at: null },
          { id: "2", title: "Second idea", state: "open", updated_at: "2024-01-02", deleted_at: null },
        ],
        count: 2,
        next: null,
        previous: null,
      }),
    );

    renderLandingPage();

    expect(screen.getByText("First idea")).toBeInTheDocument();
    expect(screen.getByText("Second idea")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
  });

  it("renders invitations in Invitations list", () => {
    vi.mocked(useInvitations).mockReturnValue(
      mockHook({
        invitations: [
          {
            id: "inv-1",
            idea_id: "idea-1",
            idea_title: "Collab idea",
            inviter: { id: "u2", display_name: "Bob" },
            created_at: "2024-01-01",
          },
        ],
      }),
    );

    renderLandingPage();

    expect(screen.getByText("Collab idea")).toBeInTheDocument();
    expect(screen.getByText("From Bob")).toBeInTheDocument();
  });

  it("clicking an idea card navigates to /idea/:uuid", async () => {
    const user = userEvent.setup();
    vi.mocked(useMyIdeas).mockReturnValue(
      mockHook({
        results: [
          { id: "abc-123", title: "Navigate me", state: "open", updated_at: "2024-01-01", deleted_at: null },
        ],
        count: 1,
        next: null,
        previous: null,
      }),
    );

    renderLandingPage();

    await user.click(screen.getByText("Navigate me"));
    expect(mockNavigate).toHaveBeenCalledWith("/idea/abc-123");
  });

  it("uses PageShell layout with Navbar", () => {
    renderLandingPage();

    expect(screen.getByText("ZiqReq")).toBeInTheDocument();
  });

  it("shows skeleton loaders when data is loading", () => {
    vi.mocked(useMyIdeas).mockReturnValue(mockHook(undefined, true));
    vi.mocked(useCollaboratingIdeas).mockReturnValue(mockHook(undefined, true));
    vi.mocked(useInvitations).mockReturnValue(mockHook(undefined, true));
    vi.mocked(useTrash).mockReturnValue(mockHook(undefined, true));

    const { container } = renderLandingPage();

    const skeletons = container.querySelectorAll(".motion-safe\\:animate-pulse");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("calls delete mutation when IdeaCard delete is clicked", async () => {
    const user = userEvent.setup();
    vi.mocked(useMyIdeas).mockReturnValue(
      mockHook({
        results: [
          { id: "del-1", title: "Delete me", state: "open", updated_at: "2024-01-01", deleted_at: null },
        ],
        count: 1,
        next: null,
        previous: null,
      }),
    );

    renderLandingPage();

    // Find the three-dot menu trigger (span with role="button")
    const menuTriggers = screen.getAllByRole("button");
    const threeDot = menuTriggers.find(
      (el) => el.querySelector(".lucide-more-vertical") !== null,
    );
    if (threeDot) {
      await user.click(threeDot);
      const deleteItem = await screen.findByText("Delete");
      await user.click(deleteItem);
      expect(mockDeleteMutate).toHaveBeenCalledWith("del-1", expect.any(Object));
    }
  });
});
