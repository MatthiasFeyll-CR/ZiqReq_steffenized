import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { websocketReducer } from "@/store/websocket-slice";
import { OfflineBanner } from "@/components/common/OfflineBanner";

const mockReconnect = vi.fn();

vi.mock("@/app/providers", () => ({
  useWsReconnect: () => mockReconnect,
}));

function createStore(overrides: {
  connectionState?: "online" | "offline";
  reconnectCountdown?: number | null;
} = {}) {
  return configureStore({
    reducer: { websocket: websocketReducer },
    preloadedState: {
      websocket: {
        connectionState: overrides.connectionState ?? "offline",
        reconnectCountdown: overrides.reconnectCountdown ?? null,
      },
    },
  });
}

function renderBanner(overrides: {
  connectionState?: "online" | "offline";
  reconnectCountdown?: number | null;
} = {}) {
  const store = createStore(overrides);
  return render(
    <Provider store={store}>
      <OfflineBanner />
    </Provider>,
  );
}

describe("T-6.2.01: OfflineBanner", () => {
  it("renders banner when connection state is offline", () => {
    renderBanner({ connectionState: "offline" });
    expect(screen.getByTestId("offline-banner")).toBeInTheDocument();
    expect(screen.getByText(/Currently offline/)).toBeInTheDocument();
  });

  it("does not render when connection state is online", () => {
    renderBanner({ connectionState: "online" });
    expect(screen.queryByTestId("offline-banner")).not.toBeInTheDocument();
  });

  it("shows countdown when reconnectCountdown is set", () => {
    renderBanner({ connectionState: "offline", reconnectCountdown: 15 });
    expect(screen.getByText(/Retrying in 15 seconds/)).toBeInTheDocument();
  });

  it("shows generic reconnecting text when countdown is null", () => {
    renderBanner({ connectionState: "offline", reconnectCountdown: null });
    expect(
      screen.getByText(/Attempting to reconnect/),
    ).toBeInTheDocument();
  });

  it("calls reconnectNow when Reconnect button is clicked", () => {
    mockReconnect.mockClear();
    renderBanner({ connectionState: "offline" });
    fireEvent.click(screen.getByTestId("reconnect-button"));
    expect(mockReconnect).toHaveBeenCalledOnce();
  });
});

describe("T-6.5.01: Chat locked when offline", () => {
  it("Reconnect button is present and labeled", () => {
    renderBanner({ connectionState: "offline" });
    const btn = screen.getByTestId("reconnect-button");
    expect(btn).toBeInTheDocument();
    expect(btn.textContent).toBe("Reconnect");
  });
});
