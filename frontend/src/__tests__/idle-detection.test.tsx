import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useIdleDetection } from "@/hooks/useIdleDetection";

// Mock useWsSend
const mockSendMessage = vi.fn();
vi.mock("@/app/providers", () => ({
  useWsSend: () => mockSendMessage,
}));

describe("T-15.1.01: Idle after timeout", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    mockSendMessage.mockClear();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("marks user idle after no mouse movement for idle_timeout seconds", () => {
    renderHook(() =>
      useIdleDetection({ projectId: "test-project", idleTimeout: 5 }),
    );

    // Advance past idle timeout (5 seconds)
    act(() => {
      vi.advanceTimersByTime(5000);
    });

    expect(mockSendMessage).toHaveBeenCalledWith({
      type: "presence_update",
      payload: {
        project_id: "test-project",
        state: "idle",
      },
    });
  });

  it("does not mark idle before timeout", () => {
    renderHook(() =>
      useIdleDetection({ projectId: "test-project", idleTimeout: 5 }),
    );

    act(() => {
      vi.advanceTimersByTime(4000);
    });

    expect(mockSendMessage).not.toHaveBeenCalled();
  });

  it("resets timer on mouse movement", () => {
    renderHook(() =>
      useIdleDetection({ projectId: "test-project", idleTimeout: 5 }),
    );

    // Advance 4 seconds, then move mouse
    act(() => {
      vi.advanceTimersByTime(4000);
    });

    act(() => {
      document.dispatchEvent(new MouseEvent("mousemove"));
    });

    // Advance another 4 seconds — should not be idle yet (timer reset)
    act(() => {
      vi.advanceTimersByTime(4000);
    });

    expect(mockSendMessage).not.toHaveBeenCalledWith(
      expect.objectContaining({
        payload: expect.objectContaining({ state: "idle" }),
      }),
    );

    // Advance 1 more second — now should be idle
    act(() => {
      vi.advanceTimersByTime(1000);
    });

    expect(mockSendMessage).toHaveBeenCalledWith({
      type: "presence_update",
      payload: {
        project_id: "test-project",
        state: "idle",
      },
    });
  });

  it("sends active state when mouse moves after idle", () => {
    renderHook(() =>
      useIdleDetection({ projectId: "test-project", idleTimeout: 5 }),
    );

    // Go idle
    act(() => {
      vi.advanceTimersByTime(5000);
    });

    mockSendMessage.mockClear();

    // Move mouse — should send active
    act(() => {
      document.dispatchEvent(new MouseEvent("mousemove"));
    });

    expect(mockSendMessage).toHaveBeenCalledWith({
      type: "presence_update",
      payload: {
        project_id: "test-project",
        state: "active",
      },
    });
  });

  it("uses default idle timeout of 300 seconds", () => {
    renderHook(() => useIdleDetection({ projectId: "test-project" }));

    // Not idle at 299s
    act(() => {
      vi.advanceTimersByTime(299_000);
    });
    expect(mockSendMessage).not.toHaveBeenCalled();

    // Idle at 300s
    act(() => {
      vi.advanceTimersByTime(1000);
    });
    expect(mockSendMessage).toHaveBeenCalledWith(
      expect.objectContaining({
        payload: expect.objectContaining({ state: "idle" }),
      }),
    );
  });
});

describe("T-15.1.02: Tab blur triggers idle", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    mockSendMessage.mockClear();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("sets idle immediately when tab becomes hidden", () => {
    renderHook(() =>
      useIdleDetection({ projectId: "test-project", idleTimeout: 300 }),
    );

    // Simulate tab blur
    act(() => {
      Object.defineProperty(document, "visibilityState", {
        value: "hidden",
        writable: true,
        configurable: true,
      });
      document.dispatchEvent(new Event("visibilitychange"));
    });

    expect(mockSendMessage).toHaveBeenCalledWith({
      type: "presence_update",
      payload: {
        project_id: "test-project",
        state: "idle",
      },
    });
  });

  it("clears idle when tab becomes visible again", () => {
    renderHook(() =>
      useIdleDetection({ projectId: "test-project", idleTimeout: 300 }),
    );

    // Tab blur
    act(() => {
      Object.defineProperty(document, "visibilityState", {
        value: "hidden",
        writable: true,
        configurable: true,
      });
      document.dispatchEvent(new Event("visibilitychange"));
    });

    mockSendMessage.mockClear();

    // Tab focus
    act(() => {
      Object.defineProperty(document, "visibilityState", {
        value: "visible",
        writable: true,
        configurable: true,
      });
      document.dispatchEvent(new Event("visibilitychange"));
    });

    expect(mockSendMessage).toHaveBeenCalledWith({
      type: "presence_update",
      payload: {
        project_id: "test-project",
        state: "active",
      },
    });
  });
});
