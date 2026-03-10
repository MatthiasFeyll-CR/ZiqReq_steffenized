import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { websocketReducer } from "@/store/websocket-slice";
import { ConnectionIndicator } from "@/components/layout/ConnectionIndicator";

function createStore(connectionState: "online" | "offline") {
  return configureStore({
    reducer: { websocket: websocketReducer },
    preloadedState: {
      websocket: { connectionState, reconnectCountdown: null },
    },
  });
}

function renderIndicator(connectionState: "online" | "offline" = "online") {
  return render(
    <Provider store={createStore(connectionState)}>
      <ConnectionIndicator />
    </Provider>,
  );
}

describe("T-6.6.01: ConnectionIndicator", () => {
  it("shows green dot and 'Online' when connected", () => {
    renderIndicator("online");
    const dot = screen.getByText("Online").previousElementSibling as HTMLElement;
    expect(screen.getByText("Online")).toBeInTheDocument();
    expect(dot).toHaveClass("bg-green-400");
  });

  it("shows red dot and 'Offline' when disconnected", () => {
    renderIndicator("offline");
    const dot = screen.getByText("Offline").previousElementSibling as HTMLElement;
    expect(screen.getByText("Offline")).toBeInTheDocument();
    expect(dot).toHaveClass("bg-red-400");
  });

  it("dot has transition-colors duration-200 for crossfade", () => {
    renderIndicator("online");
    const dot = screen.getByText("Online").previousElementSibling as HTMLElement;
    expect(dot).toHaveClass("transition-colors", "duration-200");
  });

  it("label is hidden on small screens (has hidden sm:inline)", () => {
    renderIndicator("online");
    const label = screen.getByText("Online");
    expect(label).toHaveClass("hidden", "sm:inline");
  });
});
