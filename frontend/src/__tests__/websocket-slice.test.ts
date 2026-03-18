import { describe, it, expect } from "vitest";
import {
  websocketReducer,
  setConnectionState,
  setReconnectCountdown,
  selectConnectionState,
  selectReconnectCountdown,
  selectIsOnline,
} from "@/store/websocket-slice";
import type { RootState } from "@/store/index";

const initialState = {
  connectionState: "offline" as const,
  reconnectCountdown: null as number | null,
  isIdleDisconnected: false,
  hasEverConnected: false,
};

describe("T-6.1.07: WebSocket connection state management", () => {
  it("sets connectionState to online", () => {
    const state = websocketReducer(initialState, setConnectionState("online"));
    expect(state.connectionState).toBe("online");
  });

  it("sets connectionState to offline", () => {
    const onlineState = websocketReducer(
      initialState,
      setConnectionState("online"),
    );
    const state = websocketReducer(onlineState, setConnectionState("offline"));
    expect(state.connectionState).toBe("offline");
  });

  it("clears reconnectCountdown when going online", () => {
    const withCountdown = websocketReducer(
      initialState,
      setReconnectCountdown(5),
    );
    const state = websocketReducer(
      withCountdown,
      setConnectionState("online"),
    );
    expect(state.reconnectCountdown).toBeNull();
  });

  it("sets and clears reconnectCountdown", () => {
    let state = websocketReducer(initialState, setReconnectCountdown(10));
    expect(state.reconnectCountdown).toBe(10);
    state = websocketReducer(state, setReconnectCountdown(null));
    expect(state.reconnectCountdown).toBeNull();
  });
});

describe("WebSocket selectors", () => {
  it("selectConnectionState returns connection state", () => {
    const rootState = {
      websocket: { connectionState: "online", reconnectCountdown: null, isIdleDisconnected: false, hasEverConnected: true },
    } as RootState;
    expect(selectConnectionState(rootState)).toBe("online");
  });

  it("selectReconnectCountdown returns countdown", () => {
    const rootState = {
      websocket: { connectionState: "offline", reconnectCountdown: 5, isIdleDisconnected: false, hasEverConnected: true },
    } as RootState;
    expect(selectReconnectCountdown(rootState)).toBe(5);
  });

  it("selectIsOnline returns true when online", () => {
    const rootState = {
      websocket: { connectionState: "online", reconnectCountdown: null, isIdleDisconnected: false, hasEverConnected: true },
    } as RootState;
    expect(selectIsOnline(rootState)).toBe(true);
  });

  it("selectIsOnline returns false when offline", () => {
    const rootState = {
      websocket: { connectionState: "offline", reconnectCountdown: null, isIdleDisconnected: false, hasEverConnected: true },
    } as RootState;
    expect(selectIsOnline(rootState)).toBe(false);
  });
});
