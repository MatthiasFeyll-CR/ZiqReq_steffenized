import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { websocketReducer } from "@/store/websocket-slice";
import i18n from "@/i18n/config";
import type { Idea } from "@/api/ideas";

vi.mock("@/components/workspace/WorkspaceLayout", () => ({
  WorkspaceLayout: () => <div data-testid="workspace-layout">WorkspaceLayout</div>,
}));
vi.mock("@/components/workspace/WorkspaceHeader", () => ({
  WorkspaceHeader: ({ idea }: { idea: { title: string } }) => (
    <div data-testid="workspace-header">{idea.title}</div>
  ),
}));
vi.mock("@/components/workspace/ChatPanel", () => ({
  ChatPanel: () => <div data-testid="chat-panel">ChatPanel</div>,
}));
vi.mock("@/components/workspace/DocumentView", () => ({
  DocumentView: () => <div data-testid="document-view">DocumentView</div>,
}));
vi.mock("@/components/workspace/InvitationBanner", () => ({
  InvitationBanner: () => null,
}));
vi.mock("@/app/providers", () => ({
  useWsReconnect: () => vi.fn(),
  useWsSend: () => vi.fn(),
}));

const { mockFetchIdea, mockFetchTimeline, mockFetchIdeaReviewers } = vi.hoisted(() => ({
  mockFetchIdea: vi.fn(),
  mockFetchTimeline: vi.fn(),
  mockFetchIdeaReviewers: vi.fn(),
}));

vi.mock("@/api/ideas", async () => {
  const actual = await vi.importActual("@/api/ideas");
  return {
    ...actual,
    fetchIdea: mockFetchIdea,
  };
});

vi.mock("@/api/chat", () => ({
  fetchChatMessages: vi.fn().mockResolvedValue({ messages: [], total: 0, limit: 1, offset: 0 }),
  sendChatMessage: vi.fn(),
}));

vi.mock("@/api/review", async () => {
  const actual = await vi.importActual("@/api/review");
  return {
    ...actual,
    fetchTimeline: mockFetchTimeline,
    fetchIdeaReviewers: mockFetchIdeaReviewers,
  };
});

import IdeaWorkspacePage from "@/pages/IdeaWorkspace/index";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

const IDEA_ID = "11111111-1111-1111-1111-111111111111";

function makeIdea(state: Idea["state"]): Idea {
  return {
    id: IDEA_ID,
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
  mockFetchIdea.mockResolvedValue(idea);

  const store = configureStore({
    reducer: { websocket: websocketReducer },
    preloadedState: {
      websocket: { connectionState: "online" as const, reconnectCountdown: null, isIdleDisconnected: false },
    },
  });
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });

  const url = step
    ? `/idea/${idea.id}?step=${step}`
    : `/idea/${idea.id}`;

  return render(
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={[url]}>
          <Routes>
            <Route path="/idea/:id" element={<IdeaWorkspacePage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    </Provider>,
  );
}

beforeEach(() => {
  mockFetchIdea.mockReset();
  mockFetchTimeline.mockReset();
  mockFetchIdeaReviewers.mockReset();
  mockFetchTimeline.mockResolvedValue([]);
  mockFetchIdeaReviewers.mockResolvedValue({ reviewers: [] });
  Element.prototype.scrollIntoView = vi.fn();
});

describe("T-1.2.01: Review step not accessible for never-submitted idea", () => {
  it("does not show review section when state is open (brainstorm step active)", async () => {
    renderWorkspace(makeIdea("open"));

    await waitFor(() => {
      expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
    });

    // Should be on brainstorm step, review section not rendered
    expect(screen.queryByTestId("review-section")).not.toBeInTheDocument();
  });
});

describe("T-1.2.02: Review step accessible after first submission", () => {
  it("auto-navigates to review step when state is in_review", async () => {
    renderWorkspace(makeIdea("in_review"));

    await waitFor(() => {
      expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("review-section")).toBeInTheDocument();
  });

  it("auto-navigates to review step when state is accepted", async () => {
    renderWorkspace(makeIdea("accepted"));

    await waitFor(() => {
      expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("review-section")).toBeInTheDocument();
  });

  it("shows brainstorm step when state is rejected (user can refine)", async () => {
    renderWorkspace(makeIdea("rejected"));

    await waitFor(() => {
      expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
    });

    // Rejected auto-navigates to brainstorm, but review step should be accessible
    expect(screen.getByTestId("workspace-layout")).toBeInTheDocument();
  });

  it("auto-navigates to review step when state is dropped", async () => {
    renderWorkspace(makeIdea("dropped"));

    await waitFor(() => {
      expect(screen.getByTestId("idea-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("review-section")).toBeInTheDocument();
  });
});

describe("UI-REVIEW.03: Review section rendering with timeline", () => {
  it("renders review section with header info for submitted idea", async () => {
    mockFetchTimeline.mockResolvedValue([
      {
        id: "entry-1",
        entry_type: "state_change",
        author: { id: "a1", display_name: "Alice" },
        content: "Submitted for review",
        parent_entry_id: null,
        old_state: "open",
        new_state: "in_review",
        old_version_id: null,
        new_version_id: null,
        created_at: "2026-03-01T10:00:00Z",
      },
    ]);
    mockFetchIdeaReviewers.mockResolvedValue({
      reviewers: [{ id: "r1", display_name: "Bob Reviewer" }],
    });

    renderWorkspace(makeIdea("in_review"));

    await waitFor(() => {
      expect(screen.getByTestId("review-section")).toBeInTheDocument();
    });

    // Header: title in review section
    const reviewHeader = screen.getByTestId("review-section-header");
    expect(reviewHeader).toHaveTextContent("Test Idea");
    expect(screen.getByText("In Review")).toBeInTheDocument();

    // Reviewers
    await waitFor(() => {
      expect(screen.getByTestId("reviewer-list")).toBeInTheDocument();
    });
    expect(screen.getByText("Bob Reviewer")).toBeInTheDocument();

    // Timeline entry
    await waitFor(() => {
      expect(screen.getByTestId("review-timeline")).toBeInTheDocument();
    });
    expect(screen.getByText("Submitted for review")).toBeInTheDocument();
  });

  it("shows empty timeline when no entries exist", async () => {
    renderWorkspace(makeIdea("in_review"));

    await waitFor(() => {
      expect(screen.getByTestId("review-section")).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByTestId("timeline-empty")).toBeInTheDocument();
    });
    expect(screen.getByText("No timeline entries yet")).toBeInTheDocument();
  });

  it("shows 'No reviewers assigned' when no reviewers", async () => {
    mockFetchIdeaReviewers.mockResolvedValue({ reviewers: [] });

    renderWorkspace(makeIdea("in_review"));

    await waitFor(() => {
      expect(screen.getByTestId("review-section")).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByTestId("no-reviewers")).toBeInTheDocument();
    });
  });
});
