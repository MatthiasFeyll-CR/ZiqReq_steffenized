import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import i18n from "@/i18n/config";
import { presenceReducer } from "@/store/presence-slice";
import { websocketReducer } from "@/store/websocket-slice";
import type { Project } from "@/api/projects";

vi.mock("@/app/providers", () => ({
  useWsReconnect: () => vi.fn(),
  useWsSend: () => vi.fn(),
}));

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

vi.mock("@/api/projects", async () => {
  const actual = await vi.importActual("@/api/projects");
  return {
    ...actual,
    fetchProject: vi.fn(),
    fetchInvitations: vi.fn().mockResolvedValue({ invitations: [] }),
  };
});

vi.mock("@/api/chat", () => ({
  fetchChatMessages: vi.fn().mockResolvedValue({ messages: [], total: 0, limit: 1, offset: 0 }),
  sendChatMessage: vi.fn(),
}));

import { fetchProject } from "@/api/projects";
import ProjectWorkspacePage from "@/pages/ProjectWorkspace/index";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

const MOCK_PROJECT: Project = {
  id: "11111111-1111-1111-1111-111111111111",
  title: "Test Brainstorm",
  state: "open",
  agent_mode: "interactive",
  visibility: "private",
  owner_id: "00000000-0000-0000-0000-000000000001",
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
  collaborators: [],
};

const TOKEN = "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789";

function renderWorkspacePage(path: string) {
  const store = configureStore({
    reducer: {
      websocket: websocketReducer,
      presence: presenceReducer,
    },
    preloadedState: {
      websocket: { connectionState: "online" as const, reconnectCountdown: null, isIdleDisconnected: false },
    },
  });
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={[path]}>
          <Routes>
            <Route path="/project/:id" element={<ProjectWorkspacePage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    </Provider>,
  );
}

beforeEach(() => {
  vi.mocked(fetchProject).mockReset();
  vi.mocked(fetchProject).mockResolvedValue(MOCK_PROJECT);
});

describe("UI-SHARE.01: Detect ?token= param and enable read-only mode", () => {
  it("shows read-only banner when token is present", async () => {
    renderWorkspacePage(`/project/${MOCK_PROJECT.id}?token=${TOKEN}`);

    await waitFor(() => {
      expect(screen.getByTestId("project-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("read-only-banner")).toBeInTheDocument();
    expect(screen.getByText("Viewing shared idea (read-only)")).toBeInTheDocument();
  });

  it("does not show read-only banner without token", async () => {
    renderWorkspacePage(`/project/${MOCK_PROJECT.id}`);

    await waitFor(() => {
      expect(screen.getByTestId("project-workspace")).toBeInTheDocument();
    });

    expect(screen.queryByTestId("read-only-banner")).not.toBeInTheDocument();
  });

  it("passes token to fetchProject", async () => {
    renderWorkspacePage(`/project/${MOCK_PROJECT.id}?token=${TOKEN}`);

    await waitFor(() => {
      expect(fetchProject).toHaveBeenCalledWith(MOCK_PROJECT.id, TOKEN);
    });
  });
});

describe("UI-SHARE.02: Hide edit controls in read-only mode", () => {
  it("hides chat input and shows read-only notice", async () => {
    renderWorkspacePage(`/project/${MOCK_PROJECT.id}?token=${TOKEN}`);

    await waitFor(() => {
      expect(screen.getByTestId("project-workspace")).toBeInTheDocument();
    });

    expect(screen.queryByTestId("chat-input")).not.toBeInTheDocument();
    expect(screen.getByTestId("chat-read-only-notice")).toBeInTheDocument();
    expect(screen.getByText("Viewing shared idea — chat is read-only")).toBeInTheDocument();
  });

  it("shows chat input when not in read-only mode", async () => {
    renderWorkspacePage(`/project/${MOCK_PROJECT.id}`);

    await waitFor(() => {
      expect(screen.getByTestId("project-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("chat-input")).toBeInTheDocument();
    expect(screen.queryByTestId("chat-read-only-notice")).not.toBeInTheDocument();
  });

  it("hides manage collaborators button", async () => {
    renderWorkspacePage(`/project/${MOCK_PROJECT.id}?token=${TOKEN}`);

    await waitFor(() => {
      expect(screen.getByTestId("project-workspace")).toBeInTheDocument();
    });

    expect(screen.queryByTestId("manage-collaborators-button")).not.toBeInTheDocument();
  });

  it("does not show invitation banner in read-only mode", async () => {
    renderWorkspacePage(`/project/${MOCK_PROJECT.id}?token=${TOKEN}`);

    await waitFor(() => {
      expect(screen.getByTestId("project-workspace")).toBeInTheDocument();
    });

    // InvitationBanner should not render at all in read-only mode
    expect(screen.queryByTestId("invitation-banner")).not.toBeInTheDocument();
  });
});
