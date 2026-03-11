import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { NotificationBell } from "@/components/layout/NotificationBell";

const { mockFetchUnreadCount } = vi.hoisted(() => ({
  mockFetchUnreadCount: vi.fn(),
}));

vi.mock("@/api/notifications", () => ({
  fetchUnreadCount: mockFetchUnreadCount,
}));

function createQueryClient() {
  return new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
}

function renderBell(onTogglePanel = vi.fn()) {
  const qc = createQueryClient();
  return {
    ...render(
      <QueryClientProvider client={qc}>
        <NotificationBell onTogglePanel={onTogglePanel} />
      </QueryClientProvider>,
    ),
    onTogglePanel,
  };
}

describe("NotificationBell", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders bell icon button", async () => {
    mockFetchUnreadCount.mockResolvedValue({ unread_count: 0 });
    renderBell();
    expect(screen.getByRole("button", { name: "Notifications" })).toBeInTheDocument();
  });

  it("shows badge when unread count > 0", async () => {
    mockFetchUnreadCount.mockResolvedValue({ unread_count: 5 });
    renderBell();
    expect(await screen.findByText("5")).toBeInTheDocument();
  });

  it("hides badge when unread count is 0", async () => {
    mockFetchUnreadCount.mockResolvedValue({ unread_count: 0 });
    renderBell();
    // Wait for query to settle
    await act(async () => {
      await new Promise((r) => setTimeout(r, 50));
    });
    expect(screen.queryByText("0")).not.toBeInTheDocument();
  });

  it("displays 99+ when count exceeds 99", async () => {
    mockFetchUnreadCount.mockResolvedValue({ unread_count: 150 });
    renderBell();
    expect(await screen.findByText("99+")).toBeInTheDocument();
  });

  it("calls onTogglePanel when clicked", async () => {
    mockFetchUnreadCount.mockResolvedValue({ unread_count: 0 });
    const { onTogglePanel } = renderBell();
    const button = screen.getByRole("button", { name: "Notifications" });
    await userEvent.click(button);
    expect(onTogglePanel).toHaveBeenCalledTimes(1);
  });

  it("increments count on ws:notification event", async () => {
    mockFetchUnreadCount
      .mockResolvedValueOnce({ unread_count: 3 })
      .mockResolvedValue({ unread_count: 4 });
    renderBell();
    expect(await screen.findByText("3")).toBeInTheDocument();

    // Dispatch a WebSocket notification event — optimistic update + refetch
    await act(async () => {
      window.dispatchEvent(new CustomEvent("ws:notification", { detail: {} }));
    });

    expect(await screen.findByText("4")).toBeInTheDocument();
  });
});
