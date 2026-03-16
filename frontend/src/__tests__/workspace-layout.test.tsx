import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import i18n from "@/i18n/config";

vi.mock("@/components/board/BoardCanvas", () => ({
  BoardCanvas: () => <div data-testid="board-canvas">BoardCanvas</div>,
}));

import { WorkspaceLayout } from "@/components/workspace/WorkspaceLayout";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

beforeEach(() => {
  localStorage.clear();
});

describe("T-1.1.01: panels render", () => {
  it("renders chat panel and context panel side by side", () => {
    render(<WorkspaceLayout chatPanel={<div>Chat Content</div>} />);

    expect(screen.getByTestId("workspace-layout")).toBeInTheDocument();
    expect(screen.getByTestId("chat-panel")).toBeInTheDocument();
    expect(screen.getByTestId("context-panel")).toBeInTheDocument();
    expect(screen.getByTestId("panel-divider")).toBeInTheDocument();
    expect(screen.getByText("Chat Content")).toBeInTheDocument();
  });

  it("renders default chat placeholder when no chatPanel prop", () => {
    render(<WorkspaceLayout />);

    expect(screen.getByText("Chat")).toBeInTheDocument();
  });
});

describe("T-1.1.02: drag resizes panels", () => {
  it("divider responds to mousedown and stores ratio in localStorage", () => {
    render(<WorkspaceLayout />);

    const divider = screen.getByTestId("panel-divider");

    // Simulate drag start
    fireEvent.mouseDown(divider);

    // Simulate drag move - need to dispatch on document
    fireEvent.mouseMove(document, { clientX: 300 });
    fireEvent.mouseUp(document);

    // localStorage should have been updated
    const stored = localStorage.getItem("workspace-panel-split");
    expect(stored).toBeTruthy();
  });

  it("double-click resets to default 40/60 ratio", () => {
    // Set a non-default ratio first
    localStorage.setItem("workspace-panel-split", "0.7");

    render(<WorkspaceLayout />);

    const divider = screen.getByTestId("panel-divider");
    fireEvent.doubleClick(divider);

    const stored = localStorage.getItem("workspace-panel-split");
    expect(stored).toBeTruthy();
    const val = parseFloat(stored!);
    expect(val).toBeCloseTo(0.4, 1);
  });

  it("persists panel split ratio to localStorage", () => {
    localStorage.setItem("workspace-panel-split", "0.5");

    render(<WorkspaceLayout />);

    const chatPanel = screen.getByTestId("chat-panel");
    expect(chatPanel.style.width).toBeTruthy();
  });
});

describe("T-1.1.03: Board renders directly (no tabs)", () => {
  it("renders board canvas directly in context panel", () => {
    render(<WorkspaceLayout />);

    expect(screen.getByTestId("board-canvas")).toBeInTheDocument();
  });
});
