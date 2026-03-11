import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import i18n from "@/i18n/config";
import { presenceReducer } from "@/store/presence-slice";
import { websocketReducer } from "@/store/websocket-slice";
import type { Idea } from "@/api/ideas";

// Mock BoardCanvas to avoid React Flow's ResizeObserver dependency in jsdom
vi.mock("@/components/board/BoardCanvas", () => ({
  BoardCanvas: () => <div data-testid="board-canvas">BoardCanvas</div>,
}));

vi.mock("@/app/providers", () => ({
  useWsReconnect: () => vi.fn(),
}));

// Mock child components to isolate section visibility behavior
vi.mock("@/components/chat/ChatMessageList", () => ({
  ChatMessageList: () => <div data-testid="chat-message-list">messages</div>,
}));
vi.mock("@/components/chat/ChatInput", () => ({
  ChatInput: ({ disabled }: { disabled?: boolean }) => (
    <div data-testid="chat-input" data-disabled={disabled}>
      input
    </div>
  ),
}));
vi.mock("@/components/workspace/ReviewTab", () => ({
  ReviewTab: () => <div data-testid="review-tab">ReviewTab</div>,
}));
vi.mock("@/components/review/ReviewSection", () => ({
  ReviewSection: () => <div data-testid="review-section">ReviewSection</div>,
}));

// Mock collaboration API for CollaboratorModal
vi.mock("@/api/collaboration", () => ({
  searchUsers: vi.fn().mockResolvedValue([]),
  sendInvitation: vi.fn(),
  fetchCollaborators: vi.fn().mockResolvedValue({ owner: null, co_owner: null, collaborators: [] }),
  removeCollaborator: vi.fn(),
  transferOwnership: vi.fn(),
  fetchPendingInvitations: vi.fn().mockResolvedValue({ invitations: [] }),
  revokeInvitation: vi.fn(),
}));

vi.mock("@/hooks/use-auth", () => ({
  useAuth: () => ({
    user: { id: "00000000-0000-0000-0000-000000000001", display_name: "Test User", email: "test@test.com", roles: [] },
    isAuthenticated: true,
    isDevBypass: false,
    hasRole: () => false,
    logout: () => {},
    setUser: () => {},
  }),
  AuthContext: { Provider: ({ children }: { children: React.ReactNode }) => children },
}));

// Mock fetchIdea
vi.mock("@/api/ideas", async () => {
  const actual = await vi.importActual("@/api/ideas");
  return {
    ...actual,
    fetchIdea: vi.fn(),
  };
});

import { fetchIdea } from "@/api/ideas";
import IdeaWorkspacePage from "@/pages/IdeaWorkspace/index";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

beforeEach(() => {
  vi.mocked(fetchIdea).mockReset();
  document.title = "ZiqReq";
});

function makeIdea(state: Idea["state"]): Idea {
  return {
    id: "11111111-1111-1111-1111-111111111111",
    title: "Test Idea",
    state,
    agent_mode: "interactive",
    visibility: "private",
    owner_id: "00000000-0000-0000-0000-000000000001",
    co_owner_id: null,
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
    collaborators: [],
  };
}

function renderWorkspace(idea: Idea) {
  vi.mocked(fetchIdea).mockResolvedValue(idea);
  const store = configureStore({
    reducer: { presence: presenceReducer, websocket: websocketReducer },
    preloadedState: {
      websocket: { connectionState: "online" as const, reconnectCountdown: null },
    },
  });
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <Provider store={store}>
        <MemoryRouter initialEntries={[`/idea/${idea.id}`]}>
          <Routes>
            <Route path="/idea/:id" element={<IdeaWorkspacePage />} />
          </Routes>
        </MemoryRouter>
      </Provider>
    </QueryClientProvider>,
  );
}

describe("T-1.2.01: review visible for open state (BRD generation available)", () => {
  it("shows Review tab when idea state is open", async () => {
    renderWorkspace(makeIdea("open"));

    await waitFor(() => {
      expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("tab-board")).toBeInTheDocument();
    expect(screen.getByTestId("tab-review")).toBeInTheDocument();
  });
});

describe("T-1.2.02: review visible after submit", () => {
  it("shows Review tab when idea is in_review", async () => {
    renderWorkspace(makeIdea("in_review"));

    await waitFor(() => {
      expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("tab-review")).toBeInTheDocument();
  });

  it("shows Review tab when idea is rejected", async () => {
    renderWorkspace(makeIdea("rejected"));

    await waitFor(() => {
      expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("tab-review")).toBeInTheDocument();
  });

  it("shows Review tab when idea is accepted", async () => {
    renderWorkspace(makeIdea("accepted"));

    await waitFor(() => {
      expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("tab-review")).toBeInTheDocument();
  });
});

describe("T-1.2.03: review visibility persists across all states", () => {
  const statesWithReview: Idea["state"][] = [
    "in_review",
    "accepted",
    "dropped",
    "rejected",
  ];

  for (const state of statesWithReview) {
    it(`shows Review tab in ${state} state`, async () => {
      renderWorkspace(makeIdea(state));

      await waitFor(() => {
        expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
      });

      expect(screen.getByTestId("tab-review")).toBeInTheDocument();
    });
  }

  it("shows Review tab in open state (BRD generation)", async () => {
    renderWorkspace(makeIdea("open"));

    await waitFor(() => {
      expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("tab-review")).toBeInTheDocument();
  });
});

describe("T-1.4.01: open state — chat enabled, no lock overlay", () => {
  it("does not show lock overlay when idea is open", async () => {
    renderWorkspace(makeIdea("open"));

    await waitFor(() => {
      expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
    });

    expect(screen.queryByTestId("lock-overlay")).not.toBeInTheDocument();
    expect(screen.getByTestId("chat-input")).toHaveAttribute(
      "data-disabled",
      "false",
    );
  });
});

describe("T-1.4.02: in_review state — chat locked with overlay", () => {
  it("shows lock overlay with explanation when idea is in_review", async () => {
    renderWorkspace(makeIdea("in_review"));

    await waitFor(() => {
      expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("lock-overlay")).toBeInTheDocument();
    expect(
      screen.getByText("Chat is locked while the idea is under review."),
    ).toBeInTheDocument();
    expect(screen.getByTestId("chat-input")).toHaveAttribute(
      "data-disabled",
      "true",
    );
  });
});

describe("T-1.4.03: rejected state — chat enabled, no lock", () => {
  it("does not show lock overlay when idea is rejected", async () => {
    renderWorkspace(makeIdea("rejected"));

    await waitFor(() => {
      expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
    });

    expect(screen.queryByTestId("lock-overlay")).not.toBeInTheDocument();
    expect(screen.getByTestId("chat-input")).toHaveAttribute(
      "data-disabled",
      "false",
    );
  });
});

describe("T-1.4.04: accepted state — all read-only with lock overlay", () => {
  it("shows lock overlay when idea is accepted", async () => {
    renderWorkspace(makeIdea("accepted"));

    await waitFor(() => {
      expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("lock-overlay")).toBeInTheDocument();
    expect(
      screen.getByText(
        "This idea has been accepted. All sections are read-only.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByTestId("chat-input")).toHaveAttribute(
      "data-disabled",
      "true",
    );
  });
});

describe("T-1.4.05: dropped state — all read-only with lock overlay", () => {
  it("shows lock overlay when idea is dropped", async () => {
    renderWorkspace(makeIdea("dropped"));

    await waitFor(() => {
      expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("lock-overlay")).toBeInTheDocument();
    expect(
      screen.getByText(
        "This idea has been dropped. All sections are read-only.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByTestId("chat-input")).toHaveAttribute(
      "data-disabled",
      "true",
    );
  });
});
