import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import React from "react";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { websocketReducer } from "@/store/websocket-slice";
import { boardReducer } from "@/store/board-slice";
import { presenceReducer } from "@/store/presence-slice";
import { uiReducer } from "@/store/ui-slice";
import { rateLimitReducer } from "@/store/rate-limit-slice";
import { useWebSocket } from "@/hooks/use-websocket";
import { AuthContext } from "@/hooks/use-auth";
import type { AuthContextValue } from "@/hooks/use-auth";
import type { ReactNode } from "react";

// Mock WebSocket
class MockWebSocket {
  static instances: MockWebSocket[] = [];
  url: string;
  onopen: (() => void) | null = null;
  onclose: ((event: { code: number }) => void) | null = null;
  onerror: (() => void) | null = null;
  onmessage: ((e: unknown) => void) | null = null;
  readyState = 0;
  close = vi.fn(() => {
    this.readyState = 3;
  });

  constructor(url: string) {
    this.url = url;
    MockWebSocket.instances.push(this);
  }

  simulateOpen() {
    this.readyState = 1;
    this.onopen?.();
  }

  simulateClose(code = 1000) {
    this.readyState = 3;
    this.onclose?.({ code });
  }

  simulateError() {
    this.onerror?.();
  }
}

vi.stubGlobal("WebSocket", MockWebSocket);

function createStore() {
  return configureStore({
    reducer: {
      board: boardReducer,
      websocket: websocketReducer,
      presence: presenceReducer,
      ui: uiReducer,
      rateLimit: rateLimitReducer,
    },
  });
}

function makeWrapper(
  store: ReturnType<typeof createStore>,
  authValue: AuthContextValue,
) {
  return function Wrapper({ children }: { children: ReactNode }) {
    return React.createElement(
      Provider,
      { store, children: React.createElement(AuthContext.Provider, { value: authValue, children }) },
    );
  };
}

const authenticatedAuth: AuthContextValue = {
  user: {
    id: "user-123",
    email: "test@dev.local",
    first_name: "Test",
    last_name: "User",
    display_name: "Test User",
    roles: ["user"],
  },
  isAuthenticated: true,
  isDevBypass: true,
  hasRole: () => false,
  logout: () => {},
  setUser: () => {},
  getAccessToken: () => Promise.resolve("user-123"),
};

const unauthenticatedAuth: AuthContextValue = {
  user: null,
  isAuthenticated: false,
  isDevBypass: true,
  hasRole: () => false,
  logout: () => {},
  setUser: () => {},
    getAccessToken: () => Promise.resolve(null),
};

describe("T-6.1.08: useWebSocket hook", () => {
  beforeEach(() => {
    MockWebSocket.instances = [];
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("connects to WebSocket when authenticated", async () => {
    const store = createStore();
    await act(async () => {
      renderHook(() => useWebSocket(), {
        wrapper: makeWrapper(store, authenticatedAuth),
      });
    });

    expect(MockWebSocket.instances).toHaveLength(1);
    expect(MockWebSocket.instances[0]!.url).toContain("token=user-123");
  });

  it("does not connect when not authenticated", async () => {
    const store = createStore();
    await act(async () => {
      renderHook(() => useWebSocket(), {
        wrapper: makeWrapper(store, unauthenticatedAuth),
      });
    });

    expect(MockWebSocket.instances).toHaveLength(0);
  });

  it("dispatches online state on open", async () => {
    const store = createStore();
    await act(async () => {
      renderHook(() => useWebSocket(), {
        wrapper: makeWrapper(store, authenticatedAuth),
      });
    });

    act(() => {
      MockWebSocket.instances[0]!.simulateOpen();
    });

    expect(store.getState().websocket.connectionState).toBe("online");
  });

  it("dispatches offline state on close and schedules reconnect", async () => {
    const store = createStore();
    await act(async () => {
      renderHook(() => useWebSocket(), {
        wrapper: makeWrapper(store, authenticatedAuth),
      });
    });

    act(() => {
      MockWebSocket.instances[0]!.simulateOpen();
    });

    act(() => {
      MockWebSocket.instances[0]!.simulateClose();
    });

    expect(store.getState().websocket.connectionState).toBe("offline");
    expect(store.getState().websocket.reconnectCountdown).toBe(1); // 1s initial backoff
  });

  it("cleans up on unmount — no reconnection timers fire", async () => {
    const store = createStore();
    let hookResult: ReturnType<typeof renderHook>;
    await act(async () => {
      hookResult = renderHook(() => useWebSocket(), {
        wrapper: makeWrapper(store, authenticatedAuth),
      });
    });

    act(() => {
      MockWebSocket.instances[0]!.simulateOpen();
    });
    act(() => {
      MockWebSocket.instances[0]!.simulateClose();
    });

    const instanceCountBeforeUnmount = MockWebSocket.instances.length;
    hookResult!.unmount();

    // Advance time well past any backoff — no new connections should be created
    act(() => {
      vi.advanceTimersByTime(60_000);
    });

    expect(MockWebSocket.instances.length).toBe(instanceCountBeforeUnmount);
  });
});

describe("LOOP-004: WebSocket reconnection backoff cap + cleanup", () => {
  beforeEach(() => {
    MockWebSocket.instances = [];
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("backoff caps at 30 seconds", async () => {
    const store = createStore();
    await act(async () => {
      renderHook(() => useWebSocket(), {
        wrapper: makeWrapper(store, authenticatedAuth),
      });
    });

    // Simulate repeated failed connections (close without open so backoff escalates)
    // Backoff sequence: 1s, 2s, 4s, 8s, 16s, 30s, 30s
    const expectedDelays = [1, 2, 4, 8, 16, 30, 30];

    for (let i = 0; i < expectedDelays.length; i++) {
      const ws = MockWebSocket.instances[MockWebSocket.instances.length - 1]!;

      // Close without open — simulates failed connection, backoff escalates
      act(() => {
        ws.simulateClose();
      });

      expect(store.getState().websocket.reconnectCountdown).toBe(
        expectedDelays[i],
      );

      // Advance time to trigger reconnection attempt, then flush microtask for async getAccessToken
      await act(async () => {
        vi.advanceTimersByTime(expectedDelays[i]! * 1000);
      });
    }
  });

  it("timers cleared on unmount — no leaks", async () => {
    const store = createStore();
    let hookResult: ReturnType<typeof renderHook>;
    await act(async () => {
      hookResult = renderHook(() => useWebSocket(), {
        wrapper: makeWrapper(store, authenticatedAuth),
      });
    });

    act(() => {
      MockWebSocket.instances[0]!.simulateOpen();
    });
    act(() => {
      MockWebSocket.instances[0]!.simulateClose();
    });

    // Should have a pending reconnect
    expect(store.getState().websocket.reconnectCountdown).toBe(1);

    hookResult!.unmount();

    // After unmount, state should show offline but countdown should be cleared
    expect(store.getState().websocket.connectionState).toBe("offline");
    expect(store.getState().websocket.reconnectCountdown).toBeNull();
  });

  it("reconnection stops on intentional disconnect (logout)", async () => {
    const store = createStore();
    let hookResult: { current: ReturnType<typeof useWebSocket> };
    await act(async () => {
      const { result } = renderHook(() => useWebSocket(), {
        wrapper: makeWrapper(store, authenticatedAuth),
      });
      hookResult = result;
    });

    act(() => {
      MockWebSocket.instances[0]!.simulateOpen();
    });

    // Intentional disconnect
    act(() => {
      hookResult!.current.disconnect();
    });

    expect(store.getState().websocket.connectionState).toBe("offline");
    expect(store.getState().websocket.reconnectCountdown).toBeNull();

    const countBefore = MockWebSocket.instances.length;
    act(() => {
      vi.advanceTimersByTime(60_000);
    });

    // No new connection attempts
    expect(MockWebSocket.instances.length).toBe(countBefore);
  });
});
