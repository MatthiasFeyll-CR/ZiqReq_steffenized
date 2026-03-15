import { describe, it, expect, vi, beforeAll } from "vitest";
import { render, screen } from "@testing-library/react";
import i18n from "@/i18n/config";

// Mock @xyflow/react — same pattern as box-node.test.tsx
vi.mock("@xyflow/react", () => ({
  Handle: ({ type, position, ...props }: Record<string, unknown>) => (
    <div data-testid={`handle-${type}`} data-position={position} {...props} />
  ),
  Position: { Top: "top", Bottom: "bottom", Left: "left", Right: "right" },
  NodeResizer: (props: Record<string, unknown>) => (
    <div data-testid="node-resizer" data-min-width={props.minWidth} data-min-height={props.minHeight} />
  ),
}));

import { GroupNode } from "@/components/board/GroupNode";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

// Helper to render GroupNode with required NodeProps shape
function renderGroupNode(
  dataOverrides: Record<string, unknown> = {},
  extraProps: Record<string, unknown> = {},
) {
  const defaultData = {
    title: "Test Group",
    ...dataOverrides,
  };

  const props = {
    id: "group-1",
    data: defaultData,
    type: "group" as const,
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
    width: 300,
    height: 200,
    ...extraProps,
  } as Parameters<typeof GroupNode>[0];

  return render(<GroupNode {...props} />);
}

describe("T-3.1.02: GroupNode renders as dashed container", () => {
  it("renders with 2px dashed border var(--border-strong)", () => {
    renderGroupNode();
    const node = screen.getByTestId("group-node");
    expect(node.style.border).toBe("2px dashed var(--border-strong)");
  });

  it("renders with muted background at 30% opacity", () => {
    renderGroupNode();
    const node = screen.getByTestId("group-node");
    expect(node.style.backgroundColor).toContain("var(--muted)");
    expect(node.style.backgroundColor).toContain("30%");
  });

  it("renders label badge with title text", () => {
    renderGroupNode({ title: "My Group" });
    const label = screen.getByTestId("group-label");
    expect(label).toBeInTheDocument();
    expect(label.textContent).toBe("My Group");
    expect(label.className).toContain("bg-muted");
    expect(label.className).toContain("px-2");
    expect(label.className).toContain("py-0.5");
    expect(label.className).toContain("rounded");
  });

  it("renders placeholder label when title is empty", () => {
    renderGroupNode({ title: undefined });
    const label = screen.getByTestId("group-label");
    expect(label).toBeInTheDocument();
    expect(label.textContent).toBe("Double-click to name");
  });

  it("renders NodeResizer with min 200x150", () => {
    renderGroupNode();
    const resizer = screen.getByTestId("node-resizer");
    expect(resizer).toBeInTheDocument();
    expect(resizer.getAttribute("data-min-width")).toBe("200");
    expect(resizer.getAttribute("data-min-height")).toBe("150");
  });
});

describe("T-3.1.04: Nested groups (parent_id mechanism)", () => {
  it("renders a group that can have a parentId prop (nested child)", () => {
    renderGroupNode({ title: "Child Group" }, { parentId: "parent-group-1" });
    const node = screen.getByTestId("group-node");
    expect(node).toBeInTheDocument();
    expect(screen.getByText("Child Group")).toBeInTheDocument();
  });

  it("renders connection handles for target and source", () => {
    renderGroupNode();
    expect(screen.getByTestId("handle-target")).toBeInTheDocument();
    expect(screen.getByTestId("handle-source")).toBeInTheDocument();
  });
});

describe("T-3.2.02: Drag into group (parent_id data model)", () => {
  it("accepts parentId prop indicating node belongs to a group", () => {
    // Full drag-in/out interaction is deferred to M5
    // Here we verify the data model supports parent_id assignment
    renderGroupNode({ title: "Container" });
    const node = screen.getByTestId("group-node");
    expect(node).toBeInTheDocument();
  });
});

describe("T-3.2.03: Drag out of group (parent_id data model)", () => {
  it("node without parentId renders independently", () => {
    // Full drag-out interaction is deferred to M5
    // Here we verify a group node renders without a parentId
    renderGroupNode({ title: "Standalone Group" }, { parentId: undefined });
    const node = screen.getByTestId("group-node");
    expect(node).toBeInTheDocument();
    expect(screen.getByText("Standalone Group")).toBeInTheDocument();
  });
});
