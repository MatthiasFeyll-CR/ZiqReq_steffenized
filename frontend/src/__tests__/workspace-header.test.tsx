import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import i18n from "@/i18n/config";
import { WorkspaceHeader } from "@/components/workspace/WorkspaceHeader";
import { presenceReducer } from "@/store/presence-slice";
import type { Project } from "@/api/projects";

// Mock patchProject
vi.mock("@/api/projects", async () => {
  const actual = await vi.importActual("@/api/projects");
  return {
    ...actual,
    patchProject: vi.fn(),
  };
});

// Mock collaboration API to avoid network calls
vi.mock("@/api/collaboration", () => ({
  searchUsers: vi.fn().mockResolvedValue([]),
  sendInvitation: vi.fn(),
  fetchCollaborators: vi.fn().mockResolvedValue({ owner: null, collaborators: [] }),
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

// Mock useLazyProject — project is already persisted in these tests
vi.mock("@/hooks/use-lazy-project", () => ({
  useLazyProject: () => ({
    ensureProject: () => Promise.resolve("11111111-1111-1111-1111-111111111111"),
    isDraft: false,
  }),
}));

import { patchProject } from "@/api/projects";

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

const MOCK_PROJECT: Project = {
  id: "11111111-1111-1111-1111-111111111111",
  title: "Test Brainstorm",
  project_type: "software",
  state: "open",
  visibility: "private",
  owner: { id: "00000000-0000-0000-0000-000000000001", display_name: "Test User" },
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
  collaborators: [],
};

function renderHeader(props: Partial<{
  project: Project;
  onProjectUpdate: (project: Project) => void;
  readOnly: boolean;
}> = {}) {
  const onProjectUpdate = props.onProjectUpdate ?? vi.fn();
  const onStepChange = vi.fn();
  const store = configureStore({ reducer: { presence: presenceReducer } });
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return {
    onProjectUpdate,
    onStepChange,
    ...render(
      <QueryClientProvider client={qc}>
        <Provider store={store}>
          <MemoryRouter>
            <WorkspaceHeader
              project={props.project ?? MOCK_PROJECT}
              onProjectUpdate={onProjectUpdate}
              readOnly={props.readOnly ?? false}
              activeStep="define"
              onStepChange={onStepChange}
              canAccessStructure={true}
              canAccessReview={false}
            />
          </MemoryRouter>
        </Provider>
      </QueryClientProvider>,
    ),
  };
}

beforeEach(() => {
  vi.mocked(patchProject).mockReset();
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
    const updatedProject = { ...MOCK_PROJECT, title: "New Title" };
    vi.mocked(patchProject).mockResolvedValue(updatedProject);
    const onProjectUpdate = vi.fn();
    renderHeader({ onProjectUpdate });

    fireEvent.click(screen.getByTestId("title-display"));

    const input = screen.getByTestId("title-input");
    fireEvent.change(input, { target: { value: "New Title" } });
    fireEvent.keyDown(input, { key: "Enter" });

    expect(onProjectUpdate).toHaveBeenCalledWith(
      expect.objectContaining({ title: "New Title" }),
    );

    await waitFor(() => {
      expect(patchProject).toHaveBeenCalledWith(MOCK_PROJECT.id, { title: "New Title" });
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
    const updatedProject = { ...MOCK_PROJECT, title: "Edited Title" };
    vi.mocked(patchProject).mockResolvedValue(updatedProject);
    const onProjectUpdate = vi.fn();
    renderHeader({ onProjectUpdate });

    fireEvent.click(screen.getByTestId("title-display"));
    const input = screen.getByTestId("title-input");
    fireEvent.change(input, { target: { value: "Edited Title" } });
    fireEvent.keyDown(input, { key: "Enter" });

    await waitFor(() => {
      expect(patchProject).toHaveBeenCalledWith(MOCK_PROJECT.id, { title: "Edited Title" });
    });

    await waitFor(() => {
      expect(onProjectUpdate).toHaveBeenCalledWith(updatedProject);
    });
  });

  it("reverts title on PATCH failure", async () => {
    vi.mocked(patchProject).mockRejectedValue(new Error("Server error"));
    const onProjectUpdate = vi.fn();
    renderHeader({ onProjectUpdate });

    fireEvent.click(screen.getByTestId("title-display"));
    const input = screen.getByTestId("title-input");
    fireEvent.change(input, { target: { value: "Will Fail" } });
    fireEvent.keyDown(input, { key: "Enter" });

    expect(onProjectUpdate).toHaveBeenCalledWith(
      expect.objectContaining({ title: "Will Fail" }),
    );

    await waitFor(() => {
      expect(onProjectUpdate).toHaveBeenCalledWith(
        expect.objectContaining({ title: "Test Brainstorm" }),
      );
    });
  });
});

describe("T-1.6.03: updates document.title", () => {
  it("title change via optimistic update flows to parent which sets document.title", async () => {
    const updatedProject = { ...MOCK_PROJECT, title: "Updated Doc Title" };
    vi.mocked(patchProject).mockResolvedValue(updatedProject);
    const onProjectUpdate = vi.fn();
    renderHeader({ onProjectUpdate });

    fireEvent.click(screen.getByTestId("title-display"));
    const input = screen.getByTestId("title-input");
    fireEvent.change(input, { target: { value: "Updated Doc Title" } });
    fireEvent.keyDown(input, { key: "Enter" });

    await waitFor(() => {
      expect(onProjectUpdate).toHaveBeenCalledWith(updatedProject);
    });
  });
});

describe("Process stepper in header", () => {
  it("renders the process stepper", () => {
    renderHeader();

    expect(screen.getByTestId("process-stepper")).toBeInTheDocument();
    expect(screen.getByTestId("step-define")).toBeInTheDocument();
    expect(screen.getByTestId("step-structure")).toBeInTheDocument();
    expect(screen.getByTestId("step-review")).toBeInTheDocument();
  });

  it("shows state badge", () => {
    renderHeader();

    expect(screen.getByText("Open")).toBeInTheDocument();
  });

  it("calls onStepChange when clicking a step", () => {
    const { onStepChange } = renderHeader();

    fireEvent.click(screen.getByTestId("step-structure"));

    expect(onStepChange).toHaveBeenCalledWith("structure");
  });

  it("renders options menu trigger button", () => {
    renderHeader();

    expect(screen.getByTestId("options-menu-trigger")).toBeInTheDocument();
  });
});
