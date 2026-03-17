import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import i18n from "@/i18n/config";
import { CollaboratorModal } from "@/components/collaboration/CollaboratorModal";

const PROJECT_ID = "11111111-1111-1111-1111-111111111111";
const OWNER_ID = "00000000-0000-0000-0000-000000000001";
const COLLAB_ID = "00000000-0000-0000-0000-000000000002";
const INVITE_ID = "22222222-2222-2222-2222-222222222222";

const {
  mockSearchUsers,
  mockSendBulkInvitations,
  mockFetchCollaborators,
  mockRemoveCollaborator,
  mockTransferOwnership,
  mockFetchPendingInvitations,
  mockRevokeInvitation,
  mockLeaveProject,
  mockToastSuccess,
  mockToastError,
} = vi.hoisted(() => ({
  mockSearchUsers: vi.fn(),
  mockSendBulkInvitations: vi.fn(),
  mockFetchCollaborators: vi.fn(),
  mockRemoveCollaborator: vi.fn(),
  mockTransferOwnership: vi.fn(),
  mockFetchPendingInvitations: vi.fn(),
  mockRevokeInvitation: vi.fn(),
  mockLeaveProject: vi.fn(),
  mockToastSuccess: vi.fn(),
  mockToastError: vi.fn(),
}));

vi.mock("@/api/collaboration", () => ({
  searchUsers: mockSearchUsers,
  sendBulkInvitations: mockSendBulkInvitations,
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

// Mock useLazyProject — project is already persisted in these tests
vi.mock("@/hooks/use-lazy-project", () => ({
  useLazyProject: () => ({
    ensureProject: () => Promise.resolve("11111111-1111-1111-1111-111111111111"),
    isDraft: false,
  }),
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

function renderModal(props?: { ownerId?: string }) {
  const qc = createQueryClient();
  const onOpenChange = vi.fn();
  return {
    onOpenChange,
    ...render(
      <QueryClientProvider client={qc}>
        <CollaboratorModal
          projectId={PROJECT_ID}
          ownerId={props?.ownerId ?? OWNER_ID}
          open={true}
          onOpenChange={onOpenChange}
        />
      </QueryClientProvider>,
    ),
  };
}

beforeEach(() => {
  vi.resetAllMocks();
  mockFetchCollaborators.mockResolvedValue({
    owner: { id: OWNER_ID, display_name: "Owner User", email: "owner@test.com" },
    collaborators: [
      { id: COLLAB_ID, display_name: "Collab User", email: "collab@test.com", joined_at: "2024-01-01T00:00:00Z" },
    ],
  });
  mockFetchPendingInvitations.mockResolvedValue({
    invitations: [
      {
        id: INVITE_ID,
        invitee: { id: "33333333-3333-3333-3333-333333333333", display_name: "Pending User", email: "pending@test.com" },
        created_at: "2024-01-01T00:00:00Z",
      },
    ],
  });
  mockSearchUsers.mockResolvedValue([]);
  mockSendBulkInvitations.mockResolvedValue({ results: [] });
  mockLeaveProject.mockResolvedValue({ message: "Left" });
});

describe("UI-COLLAB.01: Modal opens with 3 tabs", () => {
  it("renders modal with Invite, Collaborators, and Pending tabs", () => {
    renderModal();

    expect(screen.getByTestId("collaborator-modal")).toBeInTheDocument();
    expect(screen.getByTestId("tab-invite")).toBeInTheDocument();
    expect(screen.getByTestId("tab-collaborators")).toBeInTheDocument();
    expect(screen.getByTestId("tab-pending")).toBeInTheDocument();
  });

  it("defaults to Invite tab", () => {
    renderModal();

    expect(screen.getByTestId("invite-tab")).toBeInTheDocument();
  });
});

describe("UI-COLLAB.02: Invite tab search and invite", () => {
  it("shows search results after typing (debounced)", async () => {
    const user = userEvent.setup();
    mockSearchUsers.mockResolvedValue([
      { id: "user-1", display_name: "Alice Test", email: "alice@test.com", roles: ["user"] },
    ]);

    renderModal();

    const input = screen.getByTestId("invite-search-input");
    await user.type(input, "Ali");

    await waitFor(() => {
      expect(mockSearchUsers).toHaveBeenCalledWith("Ali");
    });

    await waitFor(() => {
      expect(screen.getByText("Alice Test")).toBeInTheDocument();
      expect(screen.getByText("alice@test.com")).toBeInTheDocument();
    });
  });

  it("selects user from search results and sends bulk invitation", async () => {
    const user = userEvent.setup();
    mockSearchUsers.mockResolvedValue([
      { id: "user-1", display_name: "Alice Test", email: "alice@test.com", roles: ["user"] },
    ]);
    mockSendBulkInvitations.mockResolvedValue({
      results: [{ invitee_id: "user-1", status: "pending" }],
    });

    renderModal();

    const input = screen.getByTestId("invite-search-input");
    await user.type(input, "Ali");

    await waitFor(() => {
      expect(screen.getByText("Alice Test")).toBeInTheDocument();
    });

    // Click the search result to select it
    await user.click(screen.getByTestId("search-result-user-1"));

    // Selected users should appear as chips
    await waitFor(() => {
      expect(screen.getByTestId("selected-users")).toBeInTheDocument();
    });

    // Click the invite button
    await user.click(screen.getByTestId("invite-selected-button"));

    await waitFor(() => {
      expect(mockSendBulkInvitations).toHaveBeenCalledWith(PROJECT_ID, ["user-1"]);
    });
  });
});

describe("UI-COLLAB.03: Collaborators tab — remove and transfer", () => {
  it("shows collaborator list with owner badge", async () => {
    const user = userEvent.setup();
    renderModal();

    await user.click(screen.getByTestId("tab-collaborators"));

    await waitFor(() => {
      expect(screen.getByTestId("collaborators-tab")).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText("Owner User")).toBeInTheDocument();
      expect(screen.getByText("Collab User")).toBeInTheDocument();
    });
  });

  it("removes collaborator with confirmation", async () => {
    const user = userEvent.setup();
    mockRemoveCollaborator.mockResolvedValue(undefined);

    renderModal();

    await user.click(screen.getByTestId("tab-collaborators"));

    await waitFor(() => {
      expect(screen.getByTestId(`remove-button-${COLLAB_ID}`)).toBeInTheDocument();
    });

    await user.click(screen.getByTestId(`remove-button-${COLLAB_ID}`));

    await waitFor(() => {
      expect(screen.getByTestId("remove-confirm-dialog")).toBeInTheDocument();
    });

    await user.click(screen.getByTestId("confirm-remove-button"));

    await waitFor(() => {
      expect(mockRemoveCollaborator).toHaveBeenCalledWith(PROJECT_ID, COLLAB_ID);
    });
    expect(mockToastSuccess).toHaveBeenCalledWith("Collaborator removed");
  });

  it("transfers ownership with confirmation", async () => {
    const user = userEvent.setup();
    mockTransferOwnership.mockResolvedValue({ message: "Ownership transferred" });

    renderModal();

    await user.click(screen.getByTestId("tab-collaborators"));

    await waitFor(() => {
      expect(screen.getByTestId(`transfer-button-${COLLAB_ID}`)).toBeInTheDocument();
    });

    await user.click(screen.getByTestId(`transfer-button-${COLLAB_ID}`));

    await waitFor(() => {
      expect(screen.getByTestId("transfer-confirm-dialog")).toBeInTheDocument();
    });

    await user.click(screen.getByTestId("confirm-transfer-button"));

    await waitFor(() => {
      expect(mockTransferOwnership).toHaveBeenCalledWith(PROJECT_ID, COLLAB_ID);
    });
    expect(mockToastSuccess).toHaveBeenCalledWith("Ownership transferred");
  });
});

describe("UI-COLLAB.04: Pending invitations tab — revoke", () => {
  it("shows pending invitations and allows revoke", async () => {
    const user = userEvent.setup();
    mockRevokeInvitation.mockResolvedValue({ message: "Invitation revoked" });

    renderModal();

    await user.click(screen.getByTestId("tab-pending"));

    await waitFor(() => {
      expect(screen.getByTestId("pending-tab")).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText("Pending User")).toBeInTheDocument();
    });

    await user.click(screen.getByTestId(`revoke-button-${INVITE_ID}`));

    await waitFor(() => {
      expect(mockRevokeInvitation).toHaveBeenCalledWith(INVITE_ID);
    });
    expect(mockToastSuccess).toHaveBeenCalledWith("Invitation revoked");
  });
});
