import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { Provider } from "react-redux";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { configureStore } from "@reduxjs/toolkit";
import { websocketReducer } from "@/store/websocket-slice";
import i18n from "@/i18n/config";

// Mock child components to isolate page-level behavior
vi.mock("@/components/workspace/WorkspaceLayout", () => ({
  WorkspaceLayout: () => <div data-testid="workspace-layout">WorkspaceLayout</div>,
}));
vi.mock("@/components/workspace/WorkspaceHeader", () => ({
  WorkspaceHeader: ({ idea }: { idea: { title: string } }) => (
    <div data-testid="workspace-header">{idea.title}</div>
  ),
}));
vi.mock("@/components/workspace/DocumentView", () => ({
  DocumentView: () => <div data-testid="document-view">DocumentView</div>,
}));
vi.mock("@/components/workspace/ChatPanel", () => ({
  ChatPanel: () => <div data-testid="chat-panel">ChatPanel</div>,
}));
vi.mock("@/components/review/ReviewSection", () => ({
  ReviewSection: () => <div data-testid="review-section">ReviewSection</div>,
}));
vi.mock("@/components/workspace/InvitationBanner", () => ({
  InvitationBanner: () => null,
}));
vi.mock("@/app/providers", () => ({
  useWsReconnect: () => vi.fn(),
  useWsSend: () => vi.fn(),
}));

// Mock fetchIdea
vi.mock("@/api/ideas", async () => {
  const actual = await vi.importActual("@/api/ideas");
  return {
    ...actual,
    fetchIdea: vi.fn(),
  };
});

vi.mock("@/api/chat", () => ({
  fetchChatMessages: vi.fn().mockResolvedValue({ messages: [], total: 0, limit: 1, offset: 0 }),
  sendChatMessage: vi.fn(),
}));

import { fetchIdea } from "@/api/ideas";
import type { Idea } from "@/api/ideas";
import IdeaWorkspacePage from "@/pages/IdeaWorkspace/index";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

const MOCK_IDEA: Idea = {
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

function renderWorkspacePage(uuid: string) {
  const store = configureStore({
    reducer: { websocket: websocketReducer },
    preloadedState: {
      websocket: { connectionState: "online" as const, reconnectCountdown: null, isIdleDisconnected: false },
    },
  });
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={[`/idea/${uuid}`]}>
          <Routes>
            <Route path="/idea/:id" element={<IdeaWorkspacePage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    </Provider>,
  );
}

beforeEach(() => {
  vi.mocked(fetchIdea).mockReset();
  document.title = "ZiqReq";
});

describe("T-1.7.01: /idea/:uuid renders workspace", () => {
  it("shows loading skeleton then renders workspace with idea data", async () => {
    vi.mocked(fetchIdea).mockResolvedValue(MOCK_IDEA);

    renderWorkspacePage(MOCK_IDEA.id);

    // Loading skeleton should appear first
    expect(screen.getByTestId("workspace-loading")).toBeInTheDocument();

    // After fetch resolves, workspace should render
    await waitFor(() => {
      expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("workspace-header")).toBeInTheDocument();
    expect(screen.getByText("Test Brainstorm")).toBeInTheDocument();
    expect(fetchIdea).toHaveBeenCalledWith(MOCK_IDEA.id);
  });

  it("updates document.title with idea title", async () => {
    vi.mocked(fetchIdea).mockResolvedValue(MOCK_IDEA);

    renderWorkspacePage(MOCK_IDEA.id);

    await waitFor(() => {
      expect(document.title).toBe("Test Brainstorm");
    });
  });
});

describe("T-1.7.02: invalid UUID → 404 error state", () => {
  it("shows error state when API returns 404", async () => {
    const err = new Error("Not found");
    (err as Error & { status: number }).status = 404;
    vi.mocked(fetchIdea).mockRejectedValue(err);

    renderWorkspacePage("bad-uuid");

    await waitFor(() => {
      expect(screen.getByTestId("workspace-error")).toBeInTheDocument();
    });

    expect(screen.getByText("Idea not found")).toBeInTheDocument();
  });

  it("shows error state when API returns 403", async () => {
    const err = new Error("Forbidden");
    (err as Error & { status: number }).status = 403;
    vi.mocked(fetchIdea).mockRejectedValue(err);

    renderWorkspacePage("no-access-uuid");

    await waitFor(() => {
      expect(screen.getByTestId("workspace-error")).toBeInTheDocument();
    });

    expect(
      screen.getByText("You don't have access to this idea"),
    ).toBeInTheDocument();
  });
});
