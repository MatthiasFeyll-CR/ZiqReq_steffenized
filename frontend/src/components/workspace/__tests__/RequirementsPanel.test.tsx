import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, waitFor, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import i18n from "@/i18n/config";
import type { RequirementsDraft } from "@/api/projects";

// Mock the API module
vi.mock("@/api/projects", async () => {
  const actual = await vi.importActual("@/api/projects");
  return {
    ...actual,
    fetchRequirements: vi.fn(),
    patchRequirements: vi.fn(),
    addRequirementsItem: vi.fn(),
    patchRequirementsItem: vi.fn(),
    deleteRequirementsItem: vi.fn(),
    addRequirementsChild: vi.fn(),
    patchRequirementsChild: vi.fn(),
    deleteRequirementsChild: vi.fn(),
    reorderRequirements: vi.fn(),
  };
});

// Mock react-toastify
vi.mock("react-toastify", () => ({
  toast: {
    info: vi.fn(),
    error: vi.fn(),
    success: vi.fn(),
  },
}));

import { RequirementsPanel } from "../RequirementsPanel";
import {
  fetchRequirements,
  addRequirementsItem,
  deleteRequirementsItem,
} from "@/api/projects";
import { toast } from "react-toastify";

const mockFetchRequirements = fetchRequirements as ReturnType<typeof vi.fn>;
const mockAddItem = addRequirementsItem as ReturnType<typeof vi.fn>;
const mockDeleteItem = deleteRequirementsItem as ReturnType<typeof vi.fn>;
// reorderRequirements is mocked but called internally by drag-end handler

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

function makeSoftwareDraft(
  overrides: Partial<RequirementsDraft> = {},
): RequirementsDraft {
  return {
    title: "Test Project",
    short_description: "A test project description",
    structure: [
      {
        id: "epic-1",
        type: "epic",
        title: "Authentication Epic",
        description: "All auth features",
        children: [
          {
            id: "story-1",
            type: "user_story",
            title: "Login with Email",
            description: "As a user, I want to log in",
            acceptance_criteria: ["Email validation", "Password hashing"],
            priority: "high",
          },
          {
            id: "story-2",
            type: "user_story",
            title: "Password Reset",
            description: "As a user, I want to reset password",
            acceptance_criteria: ["Token generation"],
            priority: "medium",
          },
        ],
      },
      {
        id: "epic-2",
        type: "epic",
        title: "Dashboard Epic",
        description: "Dashboard features",
        children: [],
      },
    ],
    item_locks: {},
    allow_information_gaps: false,
    readiness_evaluation: {},
    ...overrides,
  };
}

function makeNonSoftwareDraft(
  overrides: Partial<RequirementsDraft> = {},
): RequirementsDraft {
  return {
    title: "Test Non-Software Project",
    short_description: "A non-software project",
    structure: [
      {
        id: "milestone-1",
        type: "milestone",
        title: "Phase 1",
        description: "First phase",
        children: [
          {
            id: "wp-1",
            type: "work_package",
            title: "Design Work",
            description: "Design deliverables",
            deliverables: ["Wireframes", "Mockups"],
            dependencies: ["Stakeholder approval"],
          },
        ],
      },
    ],
    item_locks: {},
    allow_information_gaps: false,
    readiness_evaluation: {},
    ...overrides,
  };
}

describe("T-3.3.01: RequirementsPanel renders items by type", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders EpicCards for software projects", async () => {
    mockFetchRequirements.mockResolvedValue(makeSoftwareDraft());

    render(
      <RequirementsPanel
        projectId="proj-1"
        projectType="software"
      />,
    );

    await waitFor(() => {
      expect(screen.getByTestId("requirements-panel")).toBeInTheDocument();
    });

    expect(screen.getByTestId("epic-card-epic-1")).toBeInTheDocument();
    expect(screen.getByTestId("epic-card-epic-2")).toBeInTheDocument();
    expect(screen.queryByTestId("milestone-card-epic-1")).not.toBeInTheDocument();
  });

  it("renders MilestoneCards for non-software projects", async () => {
    mockFetchRequirements.mockResolvedValue(makeNonSoftwareDraft());

    render(
      <RequirementsPanel
        projectId="proj-2"
        projectType="non_software"
      />,
    );

    await waitFor(() => {
      expect(screen.getByTestId("requirements-panel")).toBeInTheDocument();
    });

    expect(screen.getByTestId("milestone-card-milestone-1")).toBeInTheDocument();
    expect(screen.queryByTestId("epic-card-milestone-1")).not.toBeInTheDocument();
  });

  it("shows title and description", async () => {
    mockFetchRequirements.mockResolvedValue(makeSoftwareDraft());

    render(
      <RequirementsPanel
        projectId="proj-1"
        projectType="software"
      />,
    );

    await waitFor(() => {
      expect(screen.getByTestId("requirements-title")).toBeInTheDocument();
    });

    expect(screen.getByText("Test Project")).toBeInTheDocument();
    expect(screen.getByText("A test project description")).toBeInTheDocument();
  });

  it("shows children inside epic cards", async () => {
    mockFetchRequirements.mockResolvedValue(makeSoftwareDraft());

    render(
      <RequirementsPanel
        projectId="proj-1"
        projectType="software"
      />,
    );

    await waitFor(() => {
      expect(screen.getByTestId("user-story-card-story-1")).toBeInTheDocument();
    });

    expect(screen.getByText("Login with Email")).toBeInTheDocument();
    expect(screen.getByText("Password Reset")).toBeInTheDocument();
  });

  it("shows work packages inside milestone cards", async () => {
    mockFetchRequirements.mockResolvedValue(makeNonSoftwareDraft());

    render(
      <RequirementsPanel
        projectId="proj-2"
        projectType="non_software"
      />,
    );

    await waitFor(() => {
      expect(screen.getByTestId("work-package-card-wp-1")).toBeInTheDocument();
    });

    expect(screen.getByText("Design Work")).toBeInTheDocument();
  });

  it("shows contributors avatars", async () => {
    mockFetchRequirements.mockResolvedValue(makeSoftwareDraft());

    render(
      <RequirementsPanel
        projectId="proj-1"
        projectType="software"
        collaborators={[
          { user_id: "u-1", display_name: "Alice" },
          { user_id: "u-2", display_name: "Bob" },
        ]}
      />,
    );

    await waitFor(() => {
      expect(screen.getByTestId("requirements-contributors")).toBeInTheDocument();
    });

    expect(screen.getByText("A")).toBeInTheDocument();
    expect(screen.getByText("B")).toBeInTheDocument();
  });

  it("shows add button with correct label for software", async () => {
    mockFetchRequirements.mockResolvedValue(makeSoftwareDraft());

    render(
      <RequirementsPanel
        projectId="proj-1"
        projectType="software"
      />,
    );

    await waitFor(() => {
      expect(screen.getByTestId("add-item-button")).toBeInTheDocument();
    });

    expect(screen.getByText("Add Epic")).toBeInTheDocument();
  });

  it("hides add/edit/delete buttons when readOnly", async () => {
    mockFetchRequirements.mockResolvedValue(makeSoftwareDraft());

    render(
      <RequirementsPanel
        projectId="proj-1"
        projectType="software"
        readOnly
      />,
    );

    await waitFor(() => {
      expect(screen.getByTestId("requirements-panel")).toBeInTheDocument();
    });

    expect(screen.queryByTestId("add-item-button")).not.toBeInTheDocument();
    expect(screen.queryByTestId("edit-item-epic-1")).not.toBeInTheDocument();
    expect(screen.queryByTestId("delete-item-epic-1")).not.toBeInTheDocument();
  });
});

describe("T-3.3.02: CRUD operations on items", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("adds a new epic via editor dialog", async () => {
    mockFetchRequirements.mockResolvedValue(
      makeSoftwareDraft({ structure: [] }),
    );
    mockAddItem.mockResolvedValue({
      id: "new-epic",
      type: "epic",
      title: "New Epic",
      description: "Desc",
      children: [],
    });

    const user = userEvent.setup();
    render(
      <RequirementsPanel
        projectId="proj-1"
        projectType="software"
      />,
    );

    await waitFor(() => {
      expect(screen.getByTestId("add-item-button")).toBeInTheDocument();
    });

    await user.click(screen.getByTestId("add-item-button"));

    // Editor dialog should appear
    await waitFor(() => {
      expect(screen.getByTestId("editor-title")).toBeInTheDocument();
    });

    await user.type(screen.getByTestId("editor-title"), "New Epic");
    await user.click(screen.getByTestId("editor-save"));

    await waitFor(() => {
      expect(mockAddItem).toHaveBeenCalledWith("proj-1", expect.objectContaining({
        title: "New Epic",
        type: "epic",
      }));
    });
  });

  it("deletes an item optimistically", async () => {
    mockFetchRequirements.mockResolvedValue(makeSoftwareDraft());
    mockDeleteItem.mockResolvedValue(undefined);

    const user = userEvent.setup();
    render(
      <RequirementsPanel
        projectId="proj-1"
        projectType="software"
      />,
    );

    await waitFor(() => {
      expect(screen.getByTestId("epic-card-epic-1")).toBeInTheDocument();
    });

    await user.click(screen.getByTestId("delete-item-epic-1"));

    await waitFor(() => {
      expect(screen.queryByTestId("epic-card-epic-1")).not.toBeInTheDocument();
    });

    expect(mockDeleteItem).toHaveBeenCalledWith("proj-1", "epic-1");
  });
});

describe("T-3.3.03: WebSocket sync on remote update", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("updates structure when ws:requirements_updated fires", async () => {
    mockFetchRequirements.mockResolvedValue(makeSoftwareDraft());

    render(
      <RequirementsPanel
        projectId="proj-1"
        projectType="software"
      />,
    );

    await waitFor(() => {
      expect(screen.getByTestId("epic-card-epic-1")).toBeInTheDocument();
    });

    // Dispatch WS event with new structure
    act(() => {
      window.dispatchEvent(
        new CustomEvent("ws:requirements_updated", {
          detail: {
            project_id: "proj-1",
            payload: {
              structure: [
                {
                  id: "epic-3",
                  type: "epic",
                  title: "New Remote Epic",
                  description: "Added remotely",
                  children: [],
                },
              ],
              updated_by: "other-user",
            },
          },
        }),
      );
    });

    await waitFor(() => {
      expect(screen.getByTestId("epic-card-epic-3")).toBeInTheDocument();
    });

    expect(screen.getByText("New Remote Epic")).toBeInTheDocument();
    // Old items should be gone
    expect(screen.queryByTestId("epic-card-epic-1")).not.toBeInTheDocument();

    // Toast should show for conflict notification
    expect(toast.info).toHaveBeenCalledWith(
      "Requirements updated by another user",
      expect.objectContaining({ toastId: "req-conflict" }),
    );
  });

  it("ignores ws events for different projects", async () => {
    mockFetchRequirements.mockResolvedValue(makeSoftwareDraft());

    render(
      <RequirementsPanel
        projectId="proj-1"
        projectType="software"
      />,
    );

    await waitFor(() => {
      expect(screen.getByTestId("epic-card-epic-1")).toBeInTheDocument();
    });

    act(() => {
      window.dispatchEvent(
        new CustomEvent("ws:requirements_updated", {
          detail: {
            project_id: "proj-other",
            payload: {
              structure: [],
              updated_by: "other-user",
            },
          },
        }),
      );
    });

    // Original items should still be there
    expect(screen.getByTestId("epic-card-epic-1")).toBeInTheDocument();
  });
});

describe("WorkspaceLayout split panel", () => {
  it("renders both panels when requirementsPanel is provided", async () => {
    const { WorkspaceLayout } = await import("../WorkspaceLayout");
    render(
      <WorkspaceLayout
        chatPanel={<div data-testid="test-chat">Chat</div>}
        requirementsPanel={<div data-testid="test-req">Requirements</div>}
      />,
    );

    expect(screen.getByTestId("chat-panel")).toBeInTheDocument();
    expect(screen.getByTestId("requirements-panel-container")).toBeInTheDocument();
    expect(screen.getByTestId("workspace-divider")).toBeInTheDocument();
    expect(screen.getByTestId("test-chat")).toBeInTheDocument();
    expect(screen.getByTestId("test-req")).toBeInTheDocument();
  });

  it("renders single panel without divider when no requirementsPanel", async () => {
    const { WorkspaceLayout } = await import("../WorkspaceLayout");
    render(
      <WorkspaceLayout chatPanel={<div>Chat</div>} />,
    );

    expect(screen.getByTestId("chat-panel")).toBeInTheDocument();
    expect(screen.queryByTestId("workspace-divider")).not.toBeInTheDocument();
    expect(screen.queryByTestId("requirements-panel-container")).not.toBeInTheDocument();
  });
});
