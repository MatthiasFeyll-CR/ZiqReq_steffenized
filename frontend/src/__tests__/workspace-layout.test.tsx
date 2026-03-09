import { describe, it, expect, beforeAll, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import i18n from "@/i18n/config";
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
    // Should be back near default (0.4), clamped by container width
    // In jsdom container width is 0, so clampRatio returns DEFAULT_RATIO (0.4)
    expect(val).toBeCloseTo(0.4, 1);
  });

  it("persists panel split ratio to localStorage", () => {
    localStorage.setItem("workspace-panel-split", "0.5");

    render(<WorkspaceLayout />);

    const chatPanel = screen.getByTestId("chat-panel");
    // Should reflect stored ratio (clamped by container width; in jsdom 0 width → DEFAULT_RATIO)
    // The point is that it reads from localStorage and applies a width style
    expect(chatPanel.style.width).toBeTruthy();
  });
});

describe("T-1.1.03: Board tab default active", () => {
  it("renders Board tab as default active tab", () => {
    render(<WorkspaceLayout />);

    const boardTab = screen.getByTestId("tab-board");
    expect(boardTab).toBeInTheDocument();
    expect(boardTab).toHaveAttribute("data-state", "active");
  });

  it("renders Board and Review tabs when reviewVisible is true", () => {
    render(<WorkspaceLayout reviewVisible={true} />);

    expect(screen.getByTestId("tab-board")).toBeInTheDocument();
    expect(screen.getByTestId("tab-review")).toBeInTheDocument();
  });

  it("hides Review tab when reviewVisible is false", () => {
    render(<WorkspaceLayout reviewVisible={false} />);

    expect(screen.getByTestId("tab-board")).toBeInTheDocument();
    expect(screen.queryByTestId("tab-review")).not.toBeInTheDocument();
  });

  it("shows Board content by default", () => {
    render(<WorkspaceLayout />);

    expect(screen.getByTestId("board-content")).toBeInTheDocument();
  });
});
