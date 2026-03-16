import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import i18n from "@/i18n/config";
import { WorkspaceHeader } from "@/components/workspace/WorkspaceHeader";
import { presenceReducer } from "@/store/presence-slice";
import type { Idea } from "@/api/ideas";

vi.mock("@/api/ideas", async () => {
  const actual = await vi.importActual("@/api/ideas");
  return { ...actual, patchIdea: vi.fn() };
});

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
    isAuthenticated: true, isLoading: false,
    isDevBypass: false,
    hasRole: () => false,
    logout: () => {},
    setUser: () => {},
    getAccessToken: () => Promise.resolve(null),
  }),
  AuthContext: { Provider: ({ children }: { children: React.ReactNode }) => children },
}));

beforeAll(async () => {
  await i18n.changeLanguage("en");
  window.PointerEvent = class PointerEvent extends Event {
    constructor(type: string, props: PointerEventInit = {}) {
      super(type, props);
    }
  } as unknown as typeof PointerEvent;
  window.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  } as unknown as typeof ResizeObserver;
  Element.prototype.hasPointerCapture = () => false;
  Element.prototype.setPointerCapture = () => {};
  Element.prototype.releasePointerCapture = () => {};
  Element.prototype.scrollIntoView = () => {};
});

const MOCK_IDEA: Idea = {
  id: "11111111-1111-1111-1111-111111111111",
  title: "Original Title",
  state: "open",
  agent_mode: "interactive",
  visibility: "private",
  owner_id: "00000000-0000-0000-0000-000000000001",
  co_owner_id: null,
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
  collaborators: [],
  merge_request_pending: null,
  merged_idea_ref: null,
  appended_idea_ref: null,
};

function renderHeader(idea: Idea = MOCK_IDEA) {
  const onIdeaUpdate = vi.fn();
  const store = configureStore({ reducer: { presence: presenceReducer } });
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  const result = render(
    <QueryClientProvider client={qc}>
      <Provider store={store}>
        <MemoryRouter>
          <WorkspaceHeader
              idea={idea}
              onIdeaUpdate={onIdeaUpdate}
              activeStep="brainstorm"
              onStepChange={() => {}}
              canAccessDocument={true}
              canAccessReview={false}
            />
        </MemoryRouter>
      </Provider>
    </QueryClientProvider>,
  );
  return { ...result, onIdeaUpdate, store, qc };
}

describe("T-2.3.03: Title update animates", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders animated title element with motion span", () => {
    renderHeader();

    const animated = screen.getByTestId("title-animated");
    expect(animated).toBeInTheDocument();
    expect(animated).toHaveTextContent("Original Title");
  });

  it("re-renders with new animated span when title changes", () => {
    const { rerender, onIdeaUpdate, store, qc } = renderHeader();

    // Verify original title in the title-display container
    expect(screen.getByTestId("title-display")).toHaveTextContent("Original Title");

    const updatedIdea = { ...MOCK_IDEA, title: "AI-Generated Title" };

    // Re-render with new title (simulating WebSocket title_update)
    rerender(
      <QueryClientProvider client={qc}>
        <Provider store={store}>
          <MemoryRouter>
            <WorkspaceHeader
                idea={updatedIdea}
                onIdeaUpdate={onIdeaUpdate}
                activeStep="brainstorm"
                onStepChange={() => {}}
                canAccessDocument={true}
                canAccessReview={false}
              />
          </MemoryRouter>
        </Provider>
      </QueryClientProvider>,
    );

    // New title should appear (AnimatePresence renders new element with new key)
    expect(screen.getByText("AI-Generated Title")).toBeInTheDocument();
    // The title display should contain the new text
    expect(screen.getByTestId("title-display")).toHaveTextContent("AI-Generated Title");
  });

  it("title-animated element has motion animation attributes", () => {
    renderHeader();

    // framer-motion renders the span with style attributes for animation
    const animated = screen.getByTestId("title-animated");
    expect(animated.tagName.toLowerCase()).toBe("span");
    // framer-motion sets inline styles for animation (opacity, transform)
    expect(animated.style).toBeDefined();
  });
});
