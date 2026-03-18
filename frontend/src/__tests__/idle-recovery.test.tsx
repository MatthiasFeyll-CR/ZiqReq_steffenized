import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { Provider } from "react-redux";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { configureStore } from "@reduxjs/toolkit";
import {
  websocketReducer,
  setConnectionState,
} from "@/store/websocket-slice";
import { useProjectSync } from "@/hooks/useProjectSync";
import type { Project } from "@/api/projects";

const mockReconnect = vi.fn();
const mockFetchProject = vi.fn<(id: string) => Promise<Project>>();

vi.mock("@/app/providers", () => ({
  useWsReconnect: () => mockReconnect,
  useWsSend: () => vi.fn(),
}));

vi.mock("@/api/projects", () => ({
  fetchProject: (...args: unknown[]) => mockFetchProject(args[0] as string),
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
        hasEverConnected: true,
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

const fakeProject: Project = {
  id: "test-project",
  title: "Updated Title",
  project_type: "software",
  state: "open",
  visibility: "private",
  owner: { id: "user-1", display_name: "" },
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
  collaborators: [],
};

describe("T-15.3.01: Mouse movement clears idle and triggers reconnection", () => {
  beforeEach(() => {
    mockReconnect.mockClear();
    mockFetchProject.mockClear();
    mockFetchProject.mockResolvedValue(fakeProject);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("triggers reconnect on mouse move when idle-disconnected", () => {
    const store = createStore({
      connectionState: "offline",
      isIdleDisconnected: true,
    });
    const onProjectUpdate = vi.fn();

    renderHook(
      () => useProjectSync({ projectId: "test-project", onProjectUpdate }),
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
    const onProjectUpdate = vi.fn();

    renderHook(
      () => useProjectSync({ projectId: "test-project", onProjectUpdate }),
      { wrapper: createWrapper(store) },
    );

    act(() => {
      document.dispatchEvent(new MouseEvent("mousemove"));
    });

    expect(mockReconnect).not.toHaveBeenCalled();
  });

  it("refetches project state on reconnect after idle disconnect", async () => {
    const store = createStore({
      connectionState: "offline",
      isIdleDisconnected: true,
    });
    const onProjectUpdate = vi.fn();

    renderHook(
      () => useProjectSync({ projectId: "test-project", onProjectUpdate }),
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

    expect(mockFetchProject).toHaveBeenCalledWith("test-project");
    expect(onProjectUpdate).toHaveBeenCalledWith(fakeProject);
  });

  it("does not refetch on reconnect if not returning from idle disconnect", async () => {
    const store = createStore({
      connectionState: "offline",
      isIdleDisconnected: false,
    });
    const onProjectUpdate = vi.fn();

    renderHook(
      () => useProjectSync({ projectId: "test-project", onProjectUpdate }),
      { wrapper: createWrapper(store) },
    );

    // Reconnect without prior idle disconnect
    await act(async () => {
      store.dispatch(setConnectionState("online"));
    });

    expect(mockFetchProject).not.toHaveBeenCalled();
    expect(onProjectUpdate).not.toHaveBeenCalled();
  });

  it("handles fetch error gracefully during state sync", async () => {
    mockFetchProject.mockRejectedValue(new Error("Network error"));

    const store = createStore({
      connectionState: "offline",
      isIdleDisconnected: true,
    });
    const onProjectUpdate = vi.fn();

    renderHook(
      () => useProjectSync({ projectId: "test-project", onProjectUpdate }),
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

    expect(mockFetchProject).toHaveBeenCalledWith("test-project");
    expect(onProjectUpdate).not.toHaveBeenCalled();
  });
});
