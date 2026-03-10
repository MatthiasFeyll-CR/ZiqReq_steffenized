import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { UserSelectionHighlight } from "@/components/board/UserSelectionHighlight";

describe("T-3.5.02: UserSelectionHighlight component", () => {
  it("renders children without highlight when selectedBy is null", () => {
    render(
      <UserSelectionHighlight selectedBy={null}>
        <div data-testid="child">Content</div>
      </UserSelectionHighlight>,
    );
    expect(screen.getByTestId("child")).toBeInTheDocument();
    expect(screen.queryByTestId("user-selection-highlight")).not.toBeInTheDocument();
  });

  it("renders colored border and name label when selectedBy is provided", () => {
    render(
      <UserSelectionHighlight
        selectedBy={{ user_id: "u1", display_name: "Alice" }}
      >
        <div data-testid="child">Content</div>
      </UserSelectionHighlight>,
    );
    expect(screen.getByTestId("user-selection-highlight")).toBeInTheDocument();
    expect(screen.getByTestId("selection-user-label")).toHaveTextContent("Alice");
    expect(screen.getByTestId("child")).toBeInTheDocument();
  });

  it("applies user-specific color to the name label", () => {
    render(
      <UserSelectionHighlight
        selectedBy={{ user_id: "u1", display_name: "Alice" }}
      >
        <div>Content</div>
      </UserSelectionHighlight>,
    );
    const label = screen.getByTestId("selection-user-label");
    expect(label.style.backgroundColor).toBeTruthy();
  });
});
