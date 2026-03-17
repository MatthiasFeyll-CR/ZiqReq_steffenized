import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useRateLimit } from "@/hooks/useRateLimit";

// Mock react-toastify
vi.mock("react-toastify", () => ({
  toast: {
    warning: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
    success: vi.fn(),
  },
}));

import { toast } from "react-toastify";

const PROJECT_ID = "22222222-2222-2222-2222-222222222222";

function dispatchRateLimit(projectId: string) {
  window.dispatchEvent(
    new CustomEvent("ws:rate_limit", {
      detail: { project_id: projectId },
    }),
  );
}

function dispatchAiProcessing(projectId: string, state: string) {
  window.dispatchEvent(
    new CustomEvent("ws:ai_processing", {
      detail: { project_id: projectId, state },
    }),
  );
}

describe("T-2.11.03: Rate limit warning toast", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows toast on rate_limit WebSocket event", () => {
    renderHook(() => useRateLimit(PROJECT_ID));

    act(() => {
      dispatchRateLimit(PROJECT_ID);
    });

    expect(toast.warning).toHaveBeenCalledWith(
      expect.stringContaining("locked"),
    );
  });

  it("sets isLimited to true on rate_limit event", () => {
    const { result } = renderHook(() => useRateLimit(PROJECT_ID));

    expect(result.current.isLimited).toBe(false);

    act(() => {
      dispatchRateLimit(PROJECT_ID);
    });

    expect(result.current.isLimited).toBe(true);
  });

  it("ignores rate_limit events for different project_id", () => {
    const { result } = renderHook(() => useRateLimit(PROJECT_ID));

    act(() => {
      dispatchRateLimit("other-idea-id");
    });

    expect(result.current.isLimited).toBe(false);
    expect(toast.warning).not.toHaveBeenCalled();
  });

  it("unlocks on ai_processing completed event", () => {
    const { result } = renderHook(() => useRateLimit(PROJECT_ID));

    act(() => {
      dispatchRateLimit(PROJECT_ID);
    });
    expect(result.current.isLimited).toBe(true);

    act(() => {
      dispatchAiProcessing(PROJECT_ID, "completed");
    });
    expect(result.current.isLimited).toBe(false);
  });

  it("unlocks on ai_processing failed event", () => {
    const { result } = renderHook(() => useRateLimit(PROJECT_ID));

    act(() => {
      dispatchRateLimit(PROJECT_ID);
    });
    expect(result.current.isLimited).toBe(true);

    act(() => {
      dispatchAiProcessing(PROJECT_ID, "failed");
    });
    expect(result.current.isLimited).toBe(false);
  });

  it("does not unlock on ai_processing started event", () => {
    const { result } = renderHook(() => useRateLimit(PROJECT_ID));

    act(() => {
      dispatchRateLimit(PROJECT_ID);
    });
    expect(result.current.isLimited).toBe(true);

    act(() => {
      dispatchAiProcessing(PROJECT_ID, "started");
    });
    expect(result.current.isLimited).toBe(true);
  });
});
