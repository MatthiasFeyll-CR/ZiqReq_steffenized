import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import { presenceReducer, updatePresence } from "@/store/presence-slice";
import { PresenceIndicators } from "@/components/workspace/PresenceIndicators";

function makeStore() {
  return configureStore({
    reducer: { presence: presenceReducer },
  });
}

// Mock tooltip to avoid radix portal issues in tests
vi.mock("@radix-ui/react-tooltip", () => ({
  Provider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  Root: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  Trigger: ({ children, ...props }: { children: React.ReactNode }) => (
    <span {...props}>{children}</span>
  ),
  Content: ({ children }: { children: React.ReactNode }) => (
    <span>{children}</span>
  ),
}));

describe("T-6.3.02: PresenceIndicators component", () => {
  it("renders nothing when no presence data", () => {
    const store = makeStore();
    const { container } = render(
      <Provider store={store}>
        <PresenceIndicators projectId="proj-1" />
      </Provider>,
    );
    expect(container.innerHTML).toBe("");
  });

  it("renders avatars for online users", () => {
    const store = makeStore();
    store.dispatch(
      updatePresence({
        project_id: "proj-1",
        user: { id: "u1", display_name: "Alice Smith" },
        state: "online",
      }),
    );
    store.dispatch(
      updatePresence({
        project_id: "proj-1",
        user: { id: "u2", display_name: "Bob Jones" },
        state: "online",
      }),
    );

    render(
      <Provider store={store}>
        <PresenceIndicators projectId="proj-1" />
      </Provider>,
    );

    expect(screen.getByTestId("presence-indicators")).toBeInTheDocument();
    expect(screen.getByText("AS")).toBeInTheDocument();
    expect(screen.getByText("BJ")).toBeInTheDocument();
  });

  it("applies idle styling (opacity-50 grayscale) to idle users", () => {
    const store = makeStore();
    store.dispatch(
      updatePresence({
        project_id: "proj-1",
        user: { id: "u1", display_name: "Alice Smith" },
        state: "idle",
      }),
    );

    render(
      <Provider store={store}>
        <PresenceIndicators projectId="proj-1" />
      </Provider>,
    );

    // The Avatar (outer container) has opacity-50 grayscale, find it via the fallback text
    const fallback = screen.getByText("AS");
    // Walk up to find the Avatar element (the one with border-2)
    const avatarContainer = fallback.closest('[class*="border-2"]');
    expect(avatarContainer?.className).toContain("opacity-50");
    expect(avatarContainer?.className).toContain("grayscale");
  });

  it("shows +N overflow when more than 4 users", () => {
    const store = makeStore();
    for (let i = 1; i <= 6; i++) {
      store.dispatch(
        updatePresence({
          project_id: "proj-1",
          user: { id: `u${i}`, display_name: `User ${i}` },
          state: "online",
        }),
      );
    }

    render(
      <Provider store={store}>
        <PresenceIndicators projectId="proj-1" />
      </Provider>,
    );

    expect(screen.getByTestId("presence-overflow")).toHaveTextContent("+2");
  });
});
