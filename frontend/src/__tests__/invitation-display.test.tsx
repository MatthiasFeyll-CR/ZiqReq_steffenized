import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import i18n from "@/i18n/config";
import { InvitationCard } from "@/components/landing/InvitationCard";
import { InvitationBanner } from "@/components/workspace/InvitationBanner";

const PROJECT_ID = "11111111-1111-1111-1111-111111111111";
const INVITE_ID = "22222222-2222-2222-2222-222222222222";
const INVITER_NAME = "Alice Inviter";
const USER_ID = "00000000-0000-0000-0000-000000000001";

const {
  mockAcceptInvitation,
  mockDeclineInvitation,
  mockFetchInvitations,
  mockToastSuccess,
} = vi.hoisted(() => ({
  mockAcceptInvitation: vi.fn(),
  mockDeclineInvitation: vi.fn(),
  mockFetchInvitations: vi.fn(),
  mockToastSuccess: vi.fn(),
}));

vi.mock("@/api/collaboration", () => ({
  acceptInvitation: mockAcceptInvitation,
  declineInvitation: mockDeclineInvitation,
}));

vi.mock("@/api/projects", () => ({
  fetchInvitations: mockFetchInvitations,
}));

vi.mock("react-toastify", () => ({
  toast: Object.assign(vi.fn(), {
    success: mockToastSuccess,
    error: vi.fn(),
  }),
  ToastContainer: () => null,
}));

vi.mock("@/hooks/use-auth", () => ({
  useAuth: () => ({
    user: { id: USER_ID, display_name: "Test User", email: "test@test.com", roles: [] },
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

beforeEach(() => {
  vi.clearAllMocks();
  mockFetchInvitations.mockResolvedValue({
    invitations: [
      {
        id: INVITE_ID,
        project_id: PROJECT_ID,
        project_title: "Test Project",
        inviter: { id: "inviter-1", display_name: INVITER_NAME },
        created_at: "2024-01-01T00:00:00Z",
      },
    ],
  });
  mockAcceptInvitation.mockResolvedValue({ message: "Invitation accepted" });
  mockDeclineInvitation.mockResolvedValue({ message: "Invitation declined" });
});

describe("UI-INVITE.01: InvitationCard renders with inviter, project, accept/decline", () => {
  it("renders invitation card with inviter name, project title, and action buttons", () => {
    const qc = createQueryClient();
    render(
      <QueryClientProvider client={qc}>
        <MemoryRouter>
          <InvitationCard
            id={INVITE_ID}
            projectId={PROJECT_ID}
            projectTitle="Test Project"
            inviterName={INVITER_NAME}
            createdAt="2024-01-01T00:00:00Z"
          />
        </MemoryRouter>
      </QueryClientProvider>,
    );

    expect(screen.getByText("Test Project")).toBeInTheDocument();
    expect(screen.getByText(/Alice Inviter/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /accept/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /decline/i })).toBeInTheDocument();
  });

  it("calls onAccept when Accept button is clicked", async () => {
    const user = userEvent.setup();
    const qc = createQueryClient();
    const onAccept = vi.fn();
    render(
      <QueryClientProvider client={qc}>
        <MemoryRouter>
          <InvitationCard
            id={INVITE_ID}
            projectId={PROJECT_ID}
            projectTitle="Test Project"
            inviterName={INVITER_NAME}
            createdAt="2024-01-01T00:00:00Z"
            onAccept={onAccept}
          />
        </MemoryRouter>
      </QueryClientProvider>,
    );

    await user.click(screen.getByRole("button", { name: /accept/i }));
    expect(onAccept).toHaveBeenCalledWith(INVITE_ID, PROJECT_ID);
  });

  it("calls onDecline when Decline button is clicked", async () => {
    const user = userEvent.setup();
    const qc = createQueryClient();
    const onDecline = vi.fn();
    render(
      <QueryClientProvider client={qc}>
        <MemoryRouter>
          <InvitationCard
            id={INVITE_ID}
            projectId={PROJECT_ID}
            projectTitle="Test Project"
            inviterName={INVITER_NAME}
            createdAt="2024-01-01T00:00:00Z"
            onDecline={onDecline}
          />
        </MemoryRouter>
      </QueryClientProvider>,
    );

    await user.click(screen.getByRole("button", { name: /decline/i }));
    expect(onDecline).toHaveBeenCalledWith(INVITE_ID);
  });
});

describe("UI-INVITE.02: InvitationBanner renders in workspace", () => {
  it("shows banner when pending invitation exists for current project", async () => {
    const qc = createQueryClient();
    render(
      <QueryClientProvider client={qc}>
        <InvitationBanner projectId={PROJECT_ID} />
      </QueryClientProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("invitation-banner")).toBeInTheDocument();
    });

    expect(screen.getByText(INVITER_NAME)).toBeInTheDocument();
    expect(screen.getByText(/invited you to collaborate/)).toBeInTheDocument();
    expect(screen.getByTestId("banner-accept-button")).toBeInTheDocument();
    expect(screen.getByTestId("banner-decline-button")).toBeInTheDocument();
  });

  it("does not show banner when no pending invitation for this project", async () => {
    mockFetchInvitations.mockResolvedValue({ invitations: [] });

    const qc = createQueryClient();
    render(
      <QueryClientProvider client={qc}>
        <InvitationBanner projectId={PROJECT_ID} />
      </QueryClientProvider>,
    );

    await waitFor(() => {
      expect(mockFetchInvitations).toHaveBeenCalled();
    });

    expect(screen.queryByTestId("invitation-banner")).not.toBeInTheDocument();
  });
});

describe("UI-INVITE.03: Accept/decline from banner calls API and shows toast", () => {
  it("accept calls API and shows success toast", async () => {
    const user = userEvent.setup();
    const qc = createQueryClient();
    render(
      <QueryClientProvider client={qc}>
        <InvitationBanner projectId={PROJECT_ID} />
      </QueryClientProvider>,
    );

    const btn = await screen.findByTestId("banner-accept-button");
    await user.click(btn);

    await waitFor(() => {
      expect(mockAcceptInvitation).toHaveBeenCalled();
      expect(mockAcceptInvitation.mock.calls[0]?.[0]).toBe(INVITE_ID);
    });

    await waitFor(() => {
      expect(mockToastSuccess).toHaveBeenCalled();
    });
  });

  it("decline calls API and shows success toast", async () => {
    const user = userEvent.setup();
    const qc = createQueryClient();
    render(
      <QueryClientProvider client={qc}>
        <InvitationBanner projectId={PROJECT_ID} />
      </QueryClientProvider>,
    );

    const btn = await screen.findByTestId("banner-decline-button");
    await user.click(btn);

    await waitFor(() => {
      expect(mockDeclineInvitation).toHaveBeenCalled();
      expect(mockDeclineInvitation.mock.calls[0]?.[0]).toBe(INVITE_ID);
    });

    await waitFor(() => {
      expect(mockToastSuccess).toHaveBeenCalled();
    });
  });
});
