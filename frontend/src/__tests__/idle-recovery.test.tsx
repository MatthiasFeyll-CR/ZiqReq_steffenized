import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { Provider } from "react-redux";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { configureStore } from "@reduxjs/toolkit";
import {
  websocketReducer,
  setConnectionState,
} from "@/store/websocket-slice";
import { useIdeaSync } from "@/hooks/useIdeaSync";
import type { Idea } from "@/api/ideas";

const mockReconnect = vi.fn();
const mockFetchIdea = vi.fn<(id: string) => Promise<Idea>>();

vi.mock("@/app/providers", () => ({
  useWsReconnect: () => mockReconnect,
  useWsSend: () => vi.fn(),
}));

vi.mock("@/api/ideas", () => ({
  fetchIdea: (...args: unknown[]) => mockFetchIdea(args[0] as string),
}));

function createStore(overrides: {
  connectionState?: "online" | "offline";
  isIdleDisconnected?: boolean;
} = {}) {
  return configureStore({
    reducer: { websocket: websocketReducer },
    preloadedState: {
      websocket: {
        connectionState: overrides.connectionState ?? "offline",
        reconnectCountdown: null,
        isIdleDisconnected: overrides.isIdleDisconnected ?? false,
      },
    },
  });
}

function createWrapper(store: ReturnType<typeof createStore>) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <Provider store={store}>
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      </Provider>
    );
  };
}

const fakeIdea: Idea = {
  id: "test-idea",
  title: "Updated Title",
  state: "open",
  agent_mode: "interactive",
  visibility: "private",
  owner_id: "user-1",
  co_owner_id: null,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
  collaborators: [],
  merge_request_pending: null,
  merged_idea_ref: null,
  appended_idea_ref: null,
};

describe("T-15.3.01: Mouse movement clears idle and triggers reconnection", () => {
  beforeEach(() => {
    mockReconnect.mockClear();
    mockFetchIdea.mockClear();
    mockFetchIdea.mockResolvedValue(fakeIdea);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("triggers reconnect on mouse move when idle-disconnected", () => {
    const store = createStore({
      connectionState: "offline",
      isIdleDisconnected: true,
    });
    const onIdeaUpdate = vi.fn();

    renderHook(
      () => useIdeaSync({ ideaId: "test-idea", onIdeaUpdate }),
      { wrapper: createWrapper(store) },
    );

    // Simulate mouse movement
    act(() => {
      document.dispatchEvent(new MouseEvent("mousemove"));
    });

    expect(mockReconnect).toHaveBeenCalledTimes(1);
    // isIdleDisconnected should be cleared
    expect(store.getState().websocket.isIdleDisconnected).toBe(false);
  });

  it("does not trigger reconnect on mouse move when not idle-disconnected", () => {
    const store = createStore({
      connectionState: "offline",
      isIdleDisconnected: false,
    });
    const onIdeaUpdate = vi.fn();

    renderHook(
      () => useIdeaSync({ ideaId: "test-idea", onIdeaUpdate }),
      { wrapper: createWrapper(store) },
    );

    act(() => {
      document.dispatchEvent(new MouseEvent("mousemove"));
    });

    expect(mockReconnect).not.toHaveBeenCalled();
  });

  it("refetches idea state on reconnect after idle disconnect", async () => {
    const store = createStore({
      connectionState: "offline",
      isIdleDisconnected: true,
    });
    const onIdeaUpdate = vi.fn();

    renderHook(
      () => useIdeaSync({ ideaId: "test-idea", onIdeaUpdate }),
      { wrapper: createWrapper(store) },
    );

    // Simulate mouse move → triggers reconnect
    act(() => {
      document.dispatchEvent(new MouseEvent("mousemove"));
    });

    // Simulate successful reconnection
    await act(async () => {
      store.dispatch(setConnectionState("online"));
    });

    expect(mockFetchIdea).toHaveBeenCalledWith("test-idea");
    expect(onIdeaUpdate).toHaveBeenCalledWith(fakeIdea);
  });

  it("does not refetch on reconnect if not returning from idle disconnect", async () => {
    const store = createStore({
      connectionState: "offline",
      isIdleDisconnected: false,
    });
    const onIdeaUpdate = vi.fn();

    renderHook(
      () => useIdeaSync({ ideaId: "test-idea", onIdeaUpdate }),
      { wrapper: createWrapper(store) },
    );

    // Reconnect without prior idle disconnect
    await act(async () => {
      store.dispatch(setConnectionState("online"));
    });

    expect(mockFetchIdea).not.toHaveBeenCalled();
    expect(onIdeaUpdate).not.toHaveBeenCalled();
  });

  it("handles fetch error gracefully during state sync", async () => {
    mockFetchIdea.mockRejectedValue(new Error("Network error"));

    const store = createStore({
      connectionState: "offline",
      isIdleDisconnected: true,
    });
    const onIdeaUpdate = vi.fn();

    renderHook(
      () => useIdeaSync({ ideaId: "test-idea", onIdeaUpdate }),
      { wrapper: createWrapper(store) },
    );

    // Simulate mouse move → triggers reconnect
    act(() => {
      document.dispatchEvent(new MouseEvent("mousemove"));
    });

    // Simulate successful reconnection — should not throw
    await act(async () => {
      store.dispatch(setConnectionState("online"));
    });

    expect(mockFetchIdea).toHaveBeenCalledWith("test-idea");
    expect(onIdeaUpdate).not.toHaveBeenCalled();
  });
});
