import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, act } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { NotificationBell } from "@/components/layout/NotificationBell";
import { toastNotificationReducer } from "@/store/toast-notification-slice";

const { mockFetchUnreadCount, mockMarkNotificationActioned } = vi.hoisted(
  () => ({
    mockFetchUnreadCount: vi.fn(),
    mockMarkNotificationActioned: vi.fn(),
  }),
);

vi.mock("@/api/notifications", () => ({
  fetchUnreadCount: mockFetchUnreadCount,
  markNotificationActioned: mockMarkNotificationActioned,
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

function createStore() {
  return configureStore({
    reducer: { toastNotifications: toastNotificationReducer },
  });
}

function renderBell() {
  const qc = createQueryClient();
  const store = createStore();
  return {
    store,
    ...render(
      <Provider store={store}>
        <QueryClientProvider client={qc}>
          <NotificationBell onTogglePanel={vi.fn()} />
        </QueryClientProvider>
      </Provider>,
    ),
  };
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
    mockMarkNotificationActioned.mockResolvedValue({});
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
      expect.objectContaining({ autoClose: 5000 }),
    );
  });

  it("displays success toast for collaborator_joined event", async () => {
    renderBell();
    await screen.findByRole("button", { name: "Notifications" });

    await act(async () => {
      dispatchNotification({
        event_type: "collaborator_joined",
        title: "Collaborator joined",
        body: "Bob joined your project",
      });
    });

    expect(toast.success).toHaveBeenCalledWith(
      "Collaborator joined: Bob joined your project",
      expect.objectContaining({ autoClose: 5000 }),
    );
  });

  it("displays warning toast for review_state_changed event", async () => {
    renderBell();
    await screen.findByRole("button", { name: "Notifications" });

    await act(async () => {
      dispatchNotification({
        event_type: "review_state_changed",
        title: "Review updated",
        body: "Your project was rejected",
      });
    });

    expect(toast.warning).toHaveBeenCalledWith(
      "Review updated: Your project was rejected",
      expect.objectContaining({ autoClose: 5000 }),
    );
  });

  it("displays warning toast for removed_from_project event", async () => {
    renderBell();
    await screen.findByRole("button", { name: "Notifications" });

    await act(async () => {
      dispatchNotification({
        event_type: "removed_from_project",
        title: "Removed",
        body: "You were removed from a project",
      });
    });

    expect(toast.warning).toHaveBeenCalledWith(
      "Removed: You were removed from a project",
      expect.objectContaining({ autoClose: 5000 }),
    );
  });

  it("silently ignores ai_delegation_complete event", async () => {
    renderBell();
    await screen.findByRole("button", { name: "Notifications" });

    await act(async () => {
      dispatchNotification({
        event_type: "ai_delegation_complete",
        title: "AI completed",
        body: "Delegation finished",
      });
    });

    expect(toast.info).not.toHaveBeenCalled();
    expect(toast.success).not.toHaveBeenCalled();
    expect(toast.warning).not.toHaveBeenCalled();
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

    expect(toast.info).toHaveBeenCalledWith(
      "You were mentioned",
      expect.objectContaining({ autoClose: 5000 }),
    );
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

  it("stores notification in bell when toast auto-closes (onClose without click)", async () => {
    const { store } = renderBell();
    await screen.findByRole("button", { name: "Notifications" });

    await act(async () => {
      dispatchNotification({
        notification_id: "n-123",
        event_type: "chat_mention",
        title: "You were mentioned",
        body: "In project X",
        reference_id: "proj-1",
        reference_type: "project",
      });
    });

    // Simulate toast auto-close (onClose fires without prior onClick)
    const toastCall = (toast.info as ReturnType<typeof vi.fn>).mock.calls[0]!;
    const options = toastCall[1] as { onClose: () => void };
    act(() => {
      options.onClose();
    });

    const items = store.getState().toastNotifications.items;
    expect(items).toHaveLength(1);
    expect(items[0]).toMatchObject({
      id: "n-123",
      event_type: "chat_mention",
      title: "You were mentioned",
    });
  });

  it("does NOT store notification when user clicks the toast", async () => {
    const { store } = renderBell();
    await screen.findByRole("button", { name: "Notifications" });

    await act(async () => {
      dispatchNotification({
        notification_id: "n-456",
        event_type: "chat_mention",
        title: "You were mentioned",
        body: "In project Y",
      });
    });

    const toastCall = (toast.info as ReturnType<typeof vi.fn>).mock.calls[0]!;
    const options = toastCall[1] as {
      onClick: () => void;
      onClose: () => void;
    };

    // User clicks the toast first, then it closes
    act(() => {
      options.onClick();
      options.onClose();
    });

    const items = store.getState().toastNotifications.items;
    expect(items).toHaveLength(0);
  });
});
