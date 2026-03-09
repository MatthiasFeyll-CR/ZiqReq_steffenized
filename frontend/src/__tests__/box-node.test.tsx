import { describe, it, expect, vi, beforeAll } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import i18n from "@/i18n/config";

// Mock @xyflow/react — same pattern as board-canvas.test.tsx
vi.mock("@xyflow/react", () => ({
  Handle: ({ type, position, ...props }: Record<string, unknown>) => (
    <div data-testid={`handle-${type}`} data-position={position} {...props} />
  ),
  Position: { Top: "top", Bottom: "bottom", Left: "left", Right: "right" },
}));

import { BoxNode } from "@/components/board/BoxNode";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

// Helper to render BoxNode with required NodeProps shape
function renderBoxNode(
  dataOverrides: Record<string, unknown> = {},
  id = "test-node-id",
) {
  const defaultData = {
    title: "Test Title",
    body: "Line one\nLine two",
    created_by: "user" as const,
    is_locked: false,
    ...dataOverrides,
  };

  const props = {
    id,
    data: defaultData,
    type: "box" as const,
    selected: false,
    isConnectable: true,
    zIndex: 0,
    positionAbsoluteX: 0,
    positionAbsoluteY: 0,
    dragging: false,
    deletable: true,
    selectable: true,
    parentId: undefined,
    dragHandle: undefined,
    sourcePosition: undefined,
    targetPosition: undefined,
    width: 200,
    height: 100,
  } as Parameters<typeof BoxNode>[0];

  return render(<BoxNode {...props} />);
}

describe("T-3.1.01: BoxNode renders title and body", () => {
  it("renders title in the title bar", () => {
    renderBoxNode({ title: "My Box Title" });
    expect(screen.getByText("My Box Title")).toBeInTheDocument();
  });

  it("renders body as bullet list items", () => {
    renderBoxNode({ body: "First bullet\nSecond bullet" });
    expect(screen.getByText("First bullet")).toBeInTheDocument();
    expect(screen.getByText("Second bullet")).toBeInTheDocument();
  });

  it("renders with border, rounded-md, shadow-sm, and bg-card", () => {
    renderBoxNode();
    const node = screen.getByTestId("box-node");
    expect(node.className).toContain("border");
    expect(node.className).toContain("rounded-md");
    expect(node.className).toContain("shadow-sm");
    expect(node.className).toContain("bg-card");
  });

  it("applies min-width 192px and max-width 320px", () => {
    renderBoxNode();
    const node = screen.getByTestId("box-node");
    expect(node.style.minWidth).toBe("192px");
    expect(node.style.maxWidth).toBe("320px");
  });
});

describe("T-3.2.08: AI badge shows when created_by is ai", () => {
  it("shows AI badge (Bot icon) when created_by='ai'", () => {
    renderBoxNode({ created_by: "ai" });
    expect(screen.getByTestId("ai-badge")).toBeInTheDocument();
  });

  it("does not show AI badge when created_by='user'", () => {
    renderBoxNode({ created_by: "user" });
    expect(screen.queryByTestId("ai-badge")).not.toBeInTheDocument();
  });
});

describe("T-3.8.01: Reference button is visible", () => {
  it("renders reference button with Pin icon", () => {
    renderBoxNode();
    expect(screen.getByTestId("reference-button")).toBeInTheDocument();
    expect(screen.getByLabelText("Reference node")).toBeInTheDocument();
  });
});

describe("T-3.8.02: Reference button dispatches @board[uuid]", () => {
  it("dispatches board:reference CustomEvent with @board[nodeId] on click", () => {
    const handler = vi.fn();
    window.addEventListener("board:reference", handler);

    renderBoxNode({}, "abc-123");
    fireEvent.click(screen.getByTestId("reference-button"));

    expect(handler).toHaveBeenCalledTimes(1);
    const event = handler.mock.calls[0]![0] as CustomEvent;
    expect(event.detail).toBe("@board[abc-123]");

    window.removeEventListener("board:reference", handler);
  });

  it("uses data.nodeId over id when available", () => {
    const handler = vi.fn();
    window.addEventListener("board:reference", handler);

    renderBoxNode({ nodeId: "custom-uuid" }, "fallback-id");
    fireEvent.click(screen.getByTestId("reference-button"));

    const event = handler.mock.calls[0]![0] as CustomEvent;
    expect(event.detail).toBe("@board[custom-uuid]");

    window.removeEventListener("board:reference", handler);
  });
});
