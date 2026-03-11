import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, act } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { NotificationBell } from "@/components/layout/NotificationBell";

const { mockFetchUnreadCount } = vi.hoisted(() => ({
  mockFetchUnreadCount: vi.fn(),
}));

vi.mock("@/api/notifications", () => ({
  fetchUnreadCount: mockFetchUnreadCount,
}));

vi.mock("react-toastify", () => ({
  toast: {
    info: vi.fn(),
    success: vi.fn(),
    warning: vi.fn(),
    error: vi.fn(),
  },
  ToastContainer: () => null,
}));

import { toast } from "react-toastify";

function createQueryClient() {
  return new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
}

function renderBell() {
  const qc = createQueryClient();
  return render(
    <QueryClientProvider client={qc}>
      <NotificationBell onTogglePanel={vi.fn()} />
    </QueryClientProvider>,
  );
}

function dispatchNotification(payload: Record<string, unknown>) {
  window.dispatchEvent(
    new CustomEvent("ws:notification", { detail: payload }),
  );
}

describe("WebSocket Notification Delivery — Toast & Bell Update", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockFetchUnreadCount.mockResolvedValue({ unread_count: 0 });
  });

  it("displays info toast for collaboration_invitation event", async () => {
    renderBell();
    await screen.findByRole("button", { name: "Notifications" });

    await act(async () => {
      dispatchNotification({
        event_type: "collaboration_invitation",
        title: "New invitation",
        body: "Alice invited you",
      });
    });

    expect(toast.info).toHaveBeenCalledWith(
      "New invitation: Alice invited you",
      { autoClose: 5000 },
    );
  });

  it("displays success toast for collaborator_joined event", async () => {
    renderBell();
    await screen.findByRole("button", { name: "Notifications" });

    await act(async () => {
      dispatchNotification({
        event_type: "collaborator_joined",
        title: "Collaborator joined",
        body: "Bob joined your idea",
      });
    });

    expect(toast.success).toHaveBeenCalledWith(
      "Collaborator joined: Bob joined your idea",
      { autoClose: 5000 },
    );
  });

  it("displays warning toast for review_state_changed event", async () => {
    renderBell();
    await screen.findByRole("button", { name: "Notifications" });

    await act(async () => {
      dispatchNotification({
        event_type: "review_state_changed",
        title: "Review updated",
        body: "Your idea was rejected",
      });
    });

    expect(toast.warning).toHaveBeenCalledWith(
      "Review updated: Your idea was rejected",
      { autoClose: 5000 },
    );
  });

  it("displays warning toast for removed_from_idea event", async () => {
    renderBell();
    await screen.findByRole("button", { name: "Notifications" });

    await act(async () => {
      dispatchNotification({
        event_type: "removed_from_idea",
        title: "Removed",
        body: "You were removed from an idea",
      });
    });

    expect(toast.warning).toHaveBeenCalledWith(
      "Removed: You were removed from an idea",
      { autoClose: 5000 },
    );
  });

  it("displays success toast for ai_delegation_complete event", async () => {
    renderBell();
    await screen.findByRole("button", { name: "Notifications" });

    await act(async () => {
      dispatchNotification({
        event_type: "ai_delegation_complete",
        title: "AI completed",
        body: "Delegation finished",
      });
    });

    expect(toast.success).toHaveBeenCalledWith(
      "AI completed: Delegation finished",
      { autoClose: 5000 },
    );
  });

  it("displays title-only toast when body is missing", async () => {
    renderBell();
    await screen.findByRole("button", { name: "Notifications" });

    await act(async () => {
      dispatchNotification({
        event_type: "chat_mention",
        title: "You were mentioned",
      });
    });

    expect(toast.info).toHaveBeenCalledWith("You were mentioned", {
      autoClose: 5000,
    });
  });

  it("does not show toast when title is missing", async () => {
    renderBell();
    await screen.findByRole("button", { name: "Notifications" });

    await act(async () => {
      dispatchNotification({ event_type: "chat_mention" });
    });

    expect(toast.info).not.toHaveBeenCalled();
    expect(toast.success).not.toHaveBeenCalled();
    expect(toast.warning).not.toHaveBeenCalled();
  });

  it("increments bell count on notification event", async () => {
    mockFetchUnreadCount
      .mockResolvedValueOnce({ unread_count: 2 })
      .mockResolvedValue({ unread_count: 3 });

    renderBell();
    expect(await screen.findByText("2")).toBeInTheDocument();

    await act(async () => {
      dispatchNotification({
        event_type: "chat_mention",
        title: "Mentioned",
        body: "Someone mentioned you",
      });
    });

    expect(await screen.findByText("3")).toBeInTheDocument();
  });
});
