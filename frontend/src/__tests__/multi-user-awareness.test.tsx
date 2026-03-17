import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import i18n from "@/i18n/config";
import type { ChatMessage } from "@/api/chat";
import type { Project } from "@/api/projects";

const PROJECT_ID = "11111111-1111-1111-1111-111111111111";
const OWNER_ID = "00000000-0000-0000-0000-000000000001";
const COLLAB_ID = "00000000-0000-0000-0000-000000000002";


const {
  mockFetchChatMessages,
  mockFetchCollaborators,
  mockLeaveProject,
  mockToastSuccess,
  mockToastError,
  mockSearchUsers,
  mockSendInvitation,
  mockRemoveCollaborator,
  mockTransferOwnership,
  mockFetchPendingInvitations,
  mockRevokeInvitation,
} = vi.hoisted(() => ({
  mockFetchChatMessages: vi.fn(),
  mockFetchCollaborators: vi.fn(),
  mockLeaveProject: vi.fn(),
  mockToastSuccess: vi.fn(),
  mockToastError: vi.fn(),
  mockSearchUsers: vi.fn(),
  mockSendInvitation: vi.fn(),
  mockRemoveCollaborator: vi.fn(),
  mockTransferOwnership: vi.fn(),
  mockFetchPendingInvitations: vi.fn(),
  mockRevokeInvitation: vi.fn(),
}));

vi.mock("@/api/chat", () => ({
  fetchChatMessages: mockFetchChatMessages,
  sendChatMessage: vi.fn(),
}));

vi.mock("@/api/collaboration", () => ({
  searchUsers: mockSearchUsers,
  sendInvitation: mockSendInvitation,
  fetchCollaborators: mockFetchCollaborators,
  removeCollaborator: mockRemoveCollaborator,
  transferOwnership: mockTransferOwnership,
  leaveProject: mockLeaveProject,
  fetchPendingInvitations: mockFetchPendingInvitations,
  revokeInvitation: mockRevokeInvitation,
}));

vi.mock("react-toastify", () => ({
  toast: Object.assign(vi.fn(), {
    success: mockToastSuccess,
    error: mockToastError,
  }),
  ToastContainer: () => null,
}));

vi.mock("@/hooks/use-auth", () => ({
  useAuth: () => ({
    user: { id: OWNER_ID, display_name: "Owner User", email: "owner@test.com", roles: [] },
    isAuthenticated: true, isLoading: false,
    isDevBypass: false,
    hasRole: () => false,
    logout: () => {},
    setUser: () => {},
    getAccessToken: () => Promise.resolve(null),
  }),
  AuthContext: { Provider: ({ children }: { children: React.ReactNode }) => children },
}));

// Mock ReactionChips to avoid complex setup
vi.mock("@/components/chat/ReactionChips", () => ({
  ReactionChips: () => null,
}));

import { ChatMessageList } from "@/components/chat/ChatMessageList";
import { CollaboratorModal } from "@/components/collaboration/CollaboratorModal";

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

function createQueryClient() {
  return new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
}

function makeProject(overrides: Partial<Project> = {}): Project {
  return {
    id: PROJECT_ID,
    title: "Test Idea",
    state: "open",
    agent_mode: "interactive",
    visibility: "collaborating",
    owner_id: OWNER_ID,
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
    collaborators: [],
    ...overrides,
  };
}

function makeMessage(overrides: Partial<ChatMessage> = {}): ChatMessage {
  return {
    id: "msg-1",
    project_id: PROJECT_ID,
    sender_type: "user",
    sender_id: OWNER_ID,
    ai_agent: null,
    content: "Hello world",
    message_type: "regular",
    created_at: "2024-01-01T12:00:00Z",
    ...overrides,
  };
}

beforeEach(() => {
  vi.resetAllMocks();
  mockSearchUsers.mockResolvedValue([]);
  mockFetchPendingInvitations.mockResolvedValue({ invitations: [] });
  mockFetchCollaborators.mockResolvedValue({
    owner: { id: OWNER_ID, display_name: "Owner User", email: "owner@test.com" },
    collaborators: [],
  });
});

/* ---------- Sender Names (UI-CHAT.05, T-2.5.01) ---------- */

describe("UI-CHAT.05 / T-2.5.01: Sender names in multi-user chat", () => {
  it("shows sender names when collaborators > 0", async () => {
    const project = makeProject({
      collaborators: [
        { user_id: COLLAB_ID, display_name: "Collab User" },
      ],
    });
    mockFetchChatMessages.mockResolvedValue({
      messages: [
        makeMessage({ id: "msg-1", sender_id: COLLAB_ID, content: "Hi from collab" }),
        makeMessage({ id: "msg-2", sender_id: OWNER_ID, content: "Hi from owner" }),
      ],
      total: 2,
      limit: 50,
      offset: 0,
    });

    render(
      <QueryClientProvider client={createQueryClient()}>
        <ChatMessageList project={project} />
      </QueryClientProvider>,
    );

    await waitFor(() => {
      expect(screen.getByText("Hi from collab")).toBeInTheDocument();
    });

    // Both sender names should be displayed in multi-user mode
    expect(screen.getByText("Collab User")).toBeInTheDocument();
    expect(screen.getByText("Owner User")).toBeInTheDocument();
  });

  it("does NOT show sender names for single-user ideas", async () => {
    const project = makeProject({ collaborators: [] });
    mockFetchChatMessages.mockResolvedValue({
      messages: [
        makeMessage({ id: "msg-1", sender_id: OWNER_ID, content: "Solo message" }),
      ],
      total: 1,
      limit: 50,
      offset: 0,
    });

    render(
      <QueryClientProvider client={createQueryClient()}>
        <ChatMessageList project={project} />
      </QueryClientProvider>,
    );

    await waitFor(() => {
      expect(screen.getByText("Solo message")).toBeInTheDocument();
    });

    // Sender name should NOT be present
    const bubbles = screen.getAllByTestId("user-message-bubble");
    for (const bubble of bubbles) {
      expect(bubble.querySelector(".text-xs.text-muted-foreground")).toBeNull();
    }
  });

  it("shows sender name with correct styling (text-xs text-muted-foreground)", async () => {
    const project = makeProject({
      collaborators: [
        { user_id: COLLAB_ID, display_name: "Collab User" },
      ],
    });
    mockFetchChatMessages.mockResolvedValue({
      messages: [
        makeMessage({ id: "msg-1", sender_id: OWNER_ID, content: "Owner msg" }),
      ],
      total: 1,
      limit: 50,
      offset: 0,
    });

    render(
      <QueryClientProvider client={createQueryClient()}>
        <ChatMessageList project={project} />
      </QueryClientProvider>,
    );

    await waitFor(() => {
      expect(screen.getByText("Owner msg")).toBeInTheDocument();
    });

    const senderEl = screen.getByText("Owner User");
    expect(senderEl.className).toContain("text-xs");
    expect(senderEl.className).toContain("text-muted-foreground");
  });
});

/* ---------- Leave button (T-8.4.07) ---------- */

describe("T-8.4.07: Single owner leave disabled", () => {
  function renderModal(props: { ownerId?: string } = {}) {
    const qc = createQueryClient();
    const onOpenChange = vi.fn();
    return {
      onOpenChange,
      ...render(
        <QueryClientProvider client={qc}>
          <CollaboratorModal
            projectId={PROJECT_ID}
            ownerId={props.ownerId ?? OWNER_ID}
            open={true}
            onOpenChange={onOpenChange}
          />
        </QueryClientProvider>,
      ),
    };
  }

  it("shows disabled Leave button with tooltip for single owner", async () => {
    const user = userEvent.setup();

    renderModal({ ownerId: OWNER_ID });

    await user.click(screen.getByTestId("tab-collaborators"));

    await waitFor(() => {
      expect(screen.getByTestId("collaborators-tab")).toBeInTheDocument();
    });

    const leaveButton = screen.getByTestId("leave-button");
    expect(leaveButton).toBeDisabled();
  });

});
