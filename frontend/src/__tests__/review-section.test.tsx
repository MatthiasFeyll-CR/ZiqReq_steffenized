import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { websocketReducer } from "@/store/websocket-slice";
import i18n from "@/i18n/config";
import type { Project } from "@/api/projects";

vi.mock("@/components/workspace/WorkspaceLayout", () => ({
  WorkspaceLayout: () => <div data-testid="workspace-layout">WorkspaceLayout</div>,
}));
vi.mock("@/components/workspace/WorkspaceHeader", () => ({
  WorkspaceHeader: ({ project }: { project: { title: string } }) => (
    <div data-testid="workspace-header">{project.title}</div>
  ),
}));
vi.mock("@/components/workspace/ChatPanel", () => ({
  ChatPanel: () => <div data-testid="chat-panel">ChatPanel</div>,
}));
vi.mock("@/components/workspace/InvitationBanner", () => ({
  InvitationBanner: () => null,
}));
vi.mock("@/app/providers", () => ({
  useWsReconnect: () => vi.fn(),
  useWsSend: () => vi.fn(),
}));

const { mockFetchProject, mockFetchTimeline, mockFetchProjectReviewers } = vi.hoisted(() => ({
  mockFetchProject: vi.fn(),
  mockFetchTimeline: vi.fn(),
  mockFetchProjectReviewers: vi.fn(),
}));

vi.mock("@/api/projects", async () => {
  const actual = await vi.importActual("@/api/projects");
  return {
    ...actual,
    fetchProject: mockFetchProject,
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
    fetchProjectReviewers: mockFetchProjectReviewers,
  };
});

import ProjectWorkspacePage from "@/pages/ProjectWorkspace/index";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

const PROJECT_ID = "11111111-1111-1111-1111-111111111111";

function makeProject(state: Project["state"]): Project {
  return {
    id: PROJECT_ID,
    title: "Test Project",
    project_type: "software",
    state,
    visibility: "private",
    owner: { id: "00000000-0000-0000-0000-000000000001", display_name: "Test User" },
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
    collaborators: [],
  };
}

function renderWorkspace(project: Project, step?: string) {
  mockFetchProject.mockResolvedValue(project);

  const store = configureStore({
    reducer: { websocket: websocketReducer },
    preloadedState: {
      websocket: { connectionState: "online" as const, reconnectCountdown: null, isIdleDisconnected: false, hasEverConnected: true },
    },
  });
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });

  const url = step
    ? `/project/${project.id}?step=${step}`
    : `/project/${project.id}`;

  return render(
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={[url]}>
          <Routes>
            <Route path="/project/:id" element={<ProjectWorkspacePage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    </Provider>,
  );
}

beforeEach(() => {
  mockFetchProject.mockReset();
  mockFetchTimeline.mockReset();
  mockFetchProjectReviewers.mockReset();
  mockFetchTimeline.mockResolvedValue([]);
  mockFetchProjectReviewers.mockResolvedValue({ reviewers: [] });
  Element.prototype.scrollIntoView = vi.fn();
});

describe("T-1.2.01: Review step not accessible for never-submitted project", () => {
  it("does not show review section when state is open (define step active)", async () => {
    renderWorkspace(makeProject("open"));

    await waitFor(() => {
      expect(screen.getByTestId("project-workspace")).toBeInTheDocument();
    });

    // Should be on define step, review section not rendered
    expect(screen.queryByTestId("review-section")).not.toBeInTheDocument();
  });
});

describe("T-1.2.02: Review step accessible after first submission", () => {
  it("auto-navigates to review step when state is in_review", async () => {
    renderWorkspace(makeProject("in_review"));

    await waitFor(() => {
      expect(screen.getByTestId("project-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("review-section")).toBeInTheDocument();
  });

  it("auto-navigates to review step when state is accepted", async () => {
    renderWorkspace(makeProject("accepted"));

    await waitFor(() => {
      expect(screen.getByTestId("project-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("review-section")).toBeInTheDocument();
  });

  it("shows define step when state is rejected (user can refine)", async () => {
    renderWorkspace(makeProject("rejected"));

    await waitFor(() => {
      expect(screen.getByTestId("project-workspace")).toBeInTheDocument();
    });

    // Rejected auto-navigates to define, but review step should be accessible
    expect(screen.getByTestId("workspace-layout")).toBeInTheDocument();
  });

  it("auto-navigates to review step when state is dropped", async () => {
    renderWorkspace(makeProject("dropped"));

    await waitFor(() => {
      expect(screen.getByTestId("project-workspace")).toBeInTheDocument();
    });

    expect(screen.getByTestId("review-section")).toBeInTheDocument();
  });
});

describe("UI-REVIEW.03: Review section rendering with timeline", () => {
  it("renders review section with header info for submitted project", async () => {
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
    mockFetchProjectReviewers.mockResolvedValue({
      reviewers: [{ id: "r1", display_name: "Bob Reviewer" }],
    });

    renderWorkspace(makeProject("in_review"));

    await waitFor(() => {
      expect(screen.getByTestId("review-section")).toBeInTheDocument();
    });

    // Header: title in review section
    const reviewHeader = screen.getByTestId("review-section-header");
    expect(reviewHeader).toHaveTextContent("Test Project");
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
    renderWorkspace(makeProject("in_review"));

    await waitFor(() => {
      expect(screen.getByTestId("review-section")).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByTestId("timeline-empty")).toBeInTheDocument();
    });
    expect(screen.getByText("No timeline entries yet")).toBeInTheDocument();
  });

  it("shows 'No reviewers assigned' when no reviewers", async () => {
    mockFetchProjectReviewers.mockResolvedValue({ reviewers: [] });

    renderWorkspace(makeProject("in_review"));

    await waitFor(() => {
      expect(screen.getByTestId("review-section")).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByTestId("no-reviewers")).toBeInTheDocument();
    });
  });
});
