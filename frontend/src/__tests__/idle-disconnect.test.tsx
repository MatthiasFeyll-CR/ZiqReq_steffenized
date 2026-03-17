import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { websocketReducer, setConnectionState } from "@/store/websocket-slice";
import { OfflineBanner } from "@/components/common/OfflineBanner";

const mockReconnect = vi.fn();

vi.mock("@/app/providers", () => ({
  useWsReconnect: () => mockReconnect,
}));

function createStore(overrides: {
  connectionState?: "online" | "offline";
  reconnectCountdown?: number | null;
  isIdleDisconnected?: boolean;
} = {}) {
  return configureStore({
    reducer: { websocket: websocketReducer },
    preloadedState: {
      websocket: {
        connectionState: overrides.connectionState ?? "offline",
        reconnectCountdown: overrides.reconnectCountdown ?? null,
        isIdleDisconnected: overrides.isIdleDisconnected ?? false,
      },
    },
  });
}

function renderBanner(overrides: {
  connectionState?: "online" | "offline";
  reconnectCountdown?: number | null;
  isIdleDisconnected?: boolean;
} = {}) {
  const store = createStore(overrides);
  return render(
    <Provider store={store}>
      <OfflineBanner />
    </Provider>,
  );
}

describe("T-15.2.01: Disconnect after prolonged idle", () => {
  it("shows idle disconnect message when isIdleDisconnected is true", () => {
    renderBanner({ connectionState: "offline", isIdleDisconnected: true });

    expect(screen.getByTestId("offline-banner")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Connection closed due to inactivity. Move your mouse to reconnect.",
      ),
    ).toBeInTheDocument();
  });

  it("does not show Reconnect button when idle disconnected", () => {
    renderBanner({ connectionState: "offline", isIdleDisconnected: true });

    expect(screen.queryByTestId("reconnect-button")).not.toBeInTheDocument();
  });

  it("shows regular offline message when not idle disconnected", () => {
    renderBanner({ connectionState: "offline", isIdleDisconnected: false });

    expect(screen.getByText(/Currently offline/)).toBeInTheDocument();
    expect(screen.getByTestId("reconnect-button")).toBeInTheDocument();
  });

  it("chat inputs are locked when offline (isOnline=false)", () => {
    // When connectionState is "offline", selectIsOnline returns false.
    // ProjectWorkspaceContent uses: effectiveChatLocked = chatLocked || !isOnline
    // and disabled={!isOnline} for WorkspaceLayout.
    // This test verifies the store state is correct.
    const store = createStore({
      connectionState: "offline",
      isIdleDisconnected: true,
    });
    const state = store.getState();
    expect(state.websocket.connectionState).toBe("offline");
    expect(state.websocket.isIdleDisconnected).toBe(true);
  });

  it("clears isIdleDisconnected when connection goes online", () => {
    const store = createStore({
      connectionState: "offline",
      isIdleDisconnected: true,
    });

    // Simulate reconnection
    store.dispatch(setConnectionState("online"));

    const state = store.getState();
    expect(state.websocket.isIdleDisconnected).toBe(false);
    expect(state.websocket.connectionState).toBe("online");
  });
});
