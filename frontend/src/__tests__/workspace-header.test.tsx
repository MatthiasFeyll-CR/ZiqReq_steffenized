import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import i18n from "@/i18n/config";
import { WorkspaceHeader } from "@/components/workspace/WorkspaceHeader";
import { presenceReducer } from "@/store/presence-slice";
import type { Idea } from "@/api/ideas";

// Mock patchIdea
vi.mock("@/api/ideas", async () => {
  const actual = await vi.importActual("@/api/ideas");
  return {
    ...actual,
    patchIdea: vi.fn(),
  };
});

// Mock collaboration API to avoid network calls
vi.mock("@/api/collaboration", () => ({
  searchUsers: vi.fn().mockResolvedValue([]),
  sendInvitation: vi.fn(),
  fetchCollaborators: vi.fn().mockResolvedValue({ owner: null, co_owner: null, collaborators: [] }),
  removeCollaborator: vi.fn(),
  transferOwnership: vi.fn(),
  fetchPendingInvitations: vi.fn().mockResolvedValue({ invitations: [] }),
  revokeInvitation: vi.fn(),
}));

// Mock useAuth for CollaboratorModal
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

import { patchIdea } from "@/api/ideas";

// Radix Select uses pointer events; stub for jsdom
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
  title: "Test Brainstorm",
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

function renderHeader(props: Partial<{
  idea: Idea;
  onIdeaUpdate: (idea: Idea) => void;
  readOnly: boolean;
}> = {}) {
  const onIdeaUpdate = props.onIdeaUpdate ?? vi.fn();
  const onStepChange = vi.fn();
  const store = configureStore({ reducer: { presence: presenceReducer } });
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return {
    onIdeaUpdate,
    onStepChange,
    ...render(
      <QueryClientProvider client={qc}>
        <Provider store={store}>
          <MemoryRouter>
            <WorkspaceHeader
              idea={props.idea ?? MOCK_IDEA}
              onIdeaUpdate={onIdeaUpdate}
              readOnly={props.readOnly ?? false}
              activeStep="brainstorm"
              onStepChange={onStepChange}
              canAccessDocument={true}
              canAccessReview={false}
            />
          </MemoryRouter>
        </Provider>
      </QueryClientProvider>,
    ),
  };
}

beforeEach(() => {
  vi.mocked(patchIdea).mockReset();
});

describe("T-1.6.01: title editable", () => {
  it("renders title text that is clickable to edit", () => {
    renderHeader();

    const titleDisplay = screen.getByTestId("title-display");
    expect(titleDisplay).toBeInTheDocument();
    expect(titleDisplay).toHaveTextContent("Test Brainstorm");
  });

  it("enters edit mode on click and shows input", async () => {
    renderHeader();

    const titleDisplay = screen.getByTestId("title-display");
    fireEvent.click(titleDisplay);

    const titleInput = screen.getByTestId("title-input");
    expect(titleInput).toBeInTheDocument();
    expect(titleInput).toHaveValue("Test Brainstorm");
  });

  it("saves title on Enter key", async () => {
    const updatedIdea = { ...MOCK_IDEA, title: "New Title" };
    vi.mocked(patchIdea).mockResolvedValue(updatedIdea);
    const onIdeaUpdate = vi.fn();
    renderHeader({ onIdeaUpdate });

    fireEvent.click(screen.getByTestId("title-display"));

    const input = screen.getByTestId("title-input");
    fireEvent.change(input, { target: { value: "New Title" } });
    fireEvent.keyDown(input, { key: "Enter" });

    expect(onIdeaUpdate).toHaveBeenCalledWith(
      expect.objectContaining({ title: "New Title" }),
    );

    await waitFor(() => {
      expect(patchIdea).toHaveBeenCalledWith(MOCK_IDEA.id, { title: "New Title" });
    });
  });

  it("cancels edit on Escape key", () => {
    renderHeader();

    fireEvent.click(screen.getByTestId("title-display"));
    const input = screen.getByTestId("title-input");
    fireEvent.change(input, { target: { value: "Changed" } });
    fireEvent.keyDown(input, { key: "Escape" });

    expect(screen.getByTestId("title-display")).toBeInTheDocument();
    expect(screen.queryByTestId("title-input")).not.toBeInTheDocument();
  });

  it("does not enter edit mode when readOnly", () => {
    renderHeader({ readOnly: true });

    fireEvent.click(screen.getByTestId("title-display"));

    expect(screen.queryByTestId("title-input")).not.toBeInTheDocument();
  });
});

describe("T-1.6.02: sets title_manually_edited", () => {
  it("sends PATCH with title field which triggers title_manually_edited=true on backend", async () => {
    const updatedIdea = { ...MOCK_IDEA, title: "Edited Title" };
    vi.mocked(patchIdea).mockResolvedValue(updatedIdea);
    const onIdeaUpdate = vi.fn();
    renderHeader({ onIdeaUpdate });

    fireEvent.click(screen.getByTestId("title-display"));
    const input = screen.getByTestId("title-input");
    fireEvent.change(input, { target: { value: "Edited Title" } });
    fireEvent.keyDown(input, { key: "Enter" });

    await waitFor(() => {
      expect(patchIdea).toHaveBeenCalledWith(MOCK_IDEA.id, { title: "Edited Title" });
    });

    await waitFor(() => {
      expect(onIdeaUpdate).toHaveBeenCalledWith(updatedIdea);
    });
  });

  it("reverts title on PATCH failure", async () => {
    vi.mocked(patchIdea).mockRejectedValue(new Error("Server error"));
    const onIdeaUpdate = vi.fn();
    renderHeader({ onIdeaUpdate });

    fireEvent.click(screen.getByTestId("title-display"));
    const input = screen.getByTestId("title-input");
    fireEvent.change(input, { target: { value: "Will Fail" } });
    fireEvent.keyDown(input, { key: "Enter" });

    expect(onIdeaUpdate).toHaveBeenCalledWith(
      expect.objectContaining({ title: "Will Fail" }),
    );

    await waitFor(() => {
      expect(onIdeaUpdate).toHaveBeenCalledWith(
        expect.objectContaining({ title: "Test Brainstorm" }),
      );
    });
  });
});

describe("T-1.6.03: updates document.title", () => {
  it("title change via optimistic update flows to parent which sets document.title", async () => {
    const updatedIdea = { ...MOCK_IDEA, title: "Updated Doc Title" };
    vi.mocked(patchIdea).mockResolvedValue(updatedIdea);
    const onIdeaUpdate = vi.fn();
    renderHeader({ onIdeaUpdate });

    fireEvent.click(screen.getByTestId("title-display"));
    const input = screen.getByTestId("title-input");
    fireEvent.change(input, { target: { value: "Updated Doc Title" } });
    fireEvent.keyDown(input, { key: "Enter" });

    await waitFor(() => {
      expect(onIdeaUpdate).toHaveBeenCalledWith(updatedIdea);
    });
  });
});

describe("Process stepper in header", () => {
  it("renders the process stepper", () => {
    renderHeader();

    expect(screen.getByTestId("process-stepper")).toBeInTheDocument();
    expect(screen.getByTestId("step-brainstorm")).toBeInTheDocument();
    expect(screen.getByTestId("step-document")).toBeInTheDocument();
    expect(screen.getByTestId("step-review")).toBeInTheDocument();
  });

  it("shows state badge", () => {
    renderHeader();

    expect(screen.getByText("Open")).toBeInTheDocument();
  });

  it("calls onStepChange when clicking a step", () => {
    const { onStepChange } = renderHeader();

    fireEvent.click(screen.getByTestId("step-document"));

    expect(onStepChange).toHaveBeenCalledWith("document");
  });

  it("renders options menu trigger button", () => {
    renderHeader();

    expect(screen.getByTestId("options-menu-trigger")).toBeInTheDocument();
  });
});
