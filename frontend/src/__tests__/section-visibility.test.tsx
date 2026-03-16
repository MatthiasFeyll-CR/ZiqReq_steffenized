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

vi.mock("@/app/providers", () => ({
  useWsReconnect: () => vi.fn(),
  useWsSend: () => vi.fn(),
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
vi.mock("@/components/review/ReviewSection", () => ({
  ReviewSection: () => <div data-testid="review-section">ReviewSection</div>,
}));

// Mock collaboration API for CollaboratorModal
vi.mock("@/api/collaboration", () => ({
  searchUsers: vi.fn().mockResolvedValue([]),
  sendInvitation: vi.fn(),
  fetchCollaborators: vi.fn().mockResolvedValue({ owner: null, collaborators: [] }),
  removeCollaborator: vi.fn(),
  transferOwnership: vi.fn(),
  fetchPendingInvitations: vi.fn().mockResolvedValue({ invitations: [] }),
  revokeInvitation: vi.fn(),
  acceptInvitation: vi.fn(),
  declineInvitation: vi.fn(),
}));

vi.mock("@/hooks/use-auth", () => ({
  useAuth: () => ({
    user: { id: "00000000-0000-0000-0000-000000000001", display_name: "Test User", email: "test@test.com", roles: [] },
    isAuthenticated: true, isLoading: false,
    isDevBypass: false,
    hasRole: () => false,
    logout: () => {},
    setUser: () => {},
    getAccessToken: () => Promise.resolve(null),
  }),
  AuthContext: { Provider: ({ children }: { children: React.ReactNode }) => children },
}));

// Mock fetchIdea, fetchInvitations, and fetchChatMessages
vi.mock("@/api/ideas", async () => {
  const actual = await vi.importActual("@/api/ideas");
  return {
    ...actual,
    fetchIdea: vi.fn(),
    fetchInvitations: vi.fn().mockResolvedValue({ invitations: [] }),
  };
});

vi.mock("@/api/chat", () => ({
  fetchChatMessages: vi.fn().mockResolvedValue({ messages: [], total: 0, limit: 1, offset: 0 }),
  sendChatMessage: vi.fn(),
}));

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
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
    collaborators: [],
  };
}

function renderWorkspace(idea: Idea, step?: string) {
  vi.mocked(fetchIdea).mockResolvedValue(idea);
  const store = configureStore({
    reducer: { presence: presenceReducer, websocket: websocketReducer },
    preloadedState: {
      websocket: { connectionState: "online" as const, reconnectCountdown: null, isIdleDisconnected: false },
    },
  });
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  const url = step ? `/idea/${idea.id}?step=${step}` : `/idea/${idea.id}`;
  return render(
    <QueryClientProvider client={qc}>
      <Provider store={store}>
        <MemoryRouter initialEntries={[url]}>
          <Routes>
            <Route path="/idea/:id" element={<IdeaWorkspacePage />} />
          </Routes>
        </MemoryRouter>
      </Provider>
    </QueryClientProvider>,
  );
}

describe("T-1.2.01: process stepper renders with correct steps", () => {
  it("shows process stepper with brainstorm step active by default", async () => {
    renderWorkspace(makeIdea("open"));

    await waitFor(() => {
      expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("process-stepper")).toBeInTheDocument();
    expect(screen.getByTestId("step-brainstorm")).toHaveAttribute("aria-current", "step");
  });

  it("shows all three process steps", async () => {
    renderWorkspace(makeIdea("open"));

    await waitFor(() => {
      expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("step-brainstorm")).toBeInTheDocument();
    expect(screen.getByTestId("step-document")).toBeInTheDocument();
    expect(screen.getByTestId("step-review")).toBeInTheDocument();
  });
});

describe("T-1.2.02: review step accessible after submit", () => {
  it("auto-navigates to review step when idea is in_review", async () => {
    renderWorkspace(makeIdea("in_review"));

    await waitFor(() => {
      expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("step-review")).toHaveAttribute("aria-current", "step");
    expect(screen.getByTestId("review-section")).toBeInTheDocument();
  });

  it("auto-navigates to review step when idea is accepted", async () => {
    renderWorkspace(makeIdea("accepted"));

    await waitFor(() => {
      expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("step-review")).toHaveAttribute("aria-current", "step");
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

describe("T-1.4.02: in_review state — auto-navigated to review step", () => {
  it("shows review section when idea is in_review", async () => {
    renderWorkspace(makeIdea("in_review"));

    await waitFor(() => {
      expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("review-section")).toBeInTheDocument();
  });
});

describe("T-1.4.03: rejected state — auto-navigated to brainstorm, chat enabled", () => {
  it("shows brainstorm view when idea is rejected", async () => {
    renderWorkspace(makeIdea("rejected"));

    await waitFor(() => {
      expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("step-brainstorm")).toHaveAttribute("aria-current", "step");
    expect(screen.queryByTestId("lock-overlay")).not.toBeInTheDocument();
    expect(screen.getByTestId("chat-input")).toHaveAttribute(
      "data-disabled",
      "false",
    );
  });
});

describe("T-1.4.04: accepted state — review step with read-only", () => {
  it("auto-navigates to review step when idea is accepted", async () => {
    renderWorkspace(makeIdea("accepted"));

    await waitFor(() => {
      expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("step-review")).toHaveAttribute("aria-current", "step");
    expect(screen.getByTestId("review-section")).toBeInTheDocument();
  });
});

describe("T-1.4.05: dropped state — review step with read-only", () => {
  it("auto-navigates to review step when idea is dropped", async () => {
    renderWorkspace(makeIdea("dropped"));

    await waitFor(() => {
      expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("step-review")).toHaveAttribute("aria-current", "step");
    expect(screen.getByTestId("review-section")).toBeInTheDocument();
  });
});
