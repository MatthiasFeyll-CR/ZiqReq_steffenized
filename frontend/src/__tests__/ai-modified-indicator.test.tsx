import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import i18n from "@/i18n/config";

// Mock @xyflow/react
vi.mock("@xyflow/react", () => ({
  Handle: ({ type, position, ...props }: Record<string, unknown>) => (
    <div data-testid={`handle-${type}`} data-position={position} {...props} />
  ),
  Position: { Top: "top", Bottom: "bottom", Left: "left", Right: "right" },
  NodeResizer: (props: Record<string, unknown>) => (
    <div data-testid="node-resizer" {...props} />
  ),
}));

import { BoxNode } from "@/components/board/BoxNode";
import { GroupNode } from "@/components/board/GroupNode";
import { FreeTextNode } from "@/components/board/FreeTextNode";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

// Helper to build NodeProps-compatible props
function makeProps(
  type: string,
  data: Record<string, unknown>,
  id = "node-1",
) {
  return {
    id,
    data,
    type,
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
    height: 150,
  };
}

describe("T-3.4.01: AI-modified indicator visible", () => {
  it("BoxNode shows gold dot when ai_modified_indicator=true", () => {
    const props = makeProps("box", {
      title: "Test",
      body: "",
      created_by: "user",
      is_locked: false,
      ai_modified_indicator: true,
    }) as Parameters<typeof BoxNode>[0];
    render(<BoxNode {...props} />);
    const dot = screen.getByTestId("ai-modified-dot");
    expect(dot).toBeInTheDocument();
    expect(dot.className).toContain("bg-amber-400");
    expect(dot.className).toContain("h-2");
    expect(dot.className).toContain("w-2");
    expect(dot.className).toContain("rounded-full");
    expect(dot.className).toContain("motion-safe:animate-pulse");
  });

  it("BoxNode does not show gold dot when ai_modified_indicator=false", () => {
    const props = makeProps("box", {
      title: "Test",
      body: "",
      created_by: "user",
      is_locked: false,
      ai_modified_indicator: false,
    }) as Parameters<typeof BoxNode>[0];
    render(<BoxNode {...props} />);
    expect(screen.queryByTestId("ai-modified-dot")).not.toBeInTheDocument();
  });

  it("BoxNode does not show gold dot when ai_modified_indicator is undefined", () => {
    const props = makeProps("box", {
      title: "Test",
      body: "",
      created_by: "user",
      is_locked: false,
    }) as Parameters<typeof BoxNode>[0];
    render(<BoxNode {...props} />);
    expect(screen.queryByTestId("ai-modified-dot")).not.toBeInTheDocument();
  });

  it("GroupNode shows gold dot when ai_modified_indicator=true", () => {
    const props = makeProps("group", {
      title: "Group",
      is_locked: false,
      ai_modified_indicator: true,
    }) as Parameters<typeof GroupNode>[0];
    render(<GroupNode {...props} />);
    const dot = screen.getByTestId("ai-modified-dot");
    expect(dot).toBeInTheDocument();
    expect(dot.className).toContain("bg-amber-400");
  });

  it("GroupNode does not show gold dot when ai_modified_indicator=false", () => {
    const props = makeProps("group", {
      title: "Group",
      is_locked: false,
      ai_modified_indicator: false,
    }) as Parameters<typeof GroupNode>[0];
    render(<GroupNode {...props} />);
    expect(screen.queryByTestId("ai-modified-dot")).not.toBeInTheDocument();
  });

  it("FreeTextNode shows gold dot when ai_modified_indicator=true", () => {
    const props = makeProps("free_text", {
      body: "Hello",
      is_locked: false,
      ai_modified_indicator: true,
    }) as Parameters<typeof FreeTextNode>[0];
    render(<FreeTextNode {...props} />);
    const dot = screen.getByTestId("ai-modified-dot");
    expect(dot).toBeInTheDocument();
    expect(dot.className).toContain("bg-amber-400");
  });

  it("FreeTextNode does not show gold dot when ai_modified_indicator=false", () => {
    const props = makeProps("free_text", {
      body: "Hello",
      is_locked: false,
      ai_modified_indicator: false,
    }) as Parameters<typeof FreeTextNode>[0];
    render(<FreeTextNode {...props} />);
    expect(screen.queryByTestId("ai-modified-dot")).not.toBeInTheDocument();
  });
});

describe("T-3.4.02: Indicator clears on user selection (BoardCanvas)", () => {
  let mockUpdateBoardNode: ReturnType<typeof vi.fn>;
  let capturedOnNodeClick: ((...args: unknown[]) => void) | undefined;
  let mockNodesState: Record<string, unknown>[];
  let mockSetNodes: ReturnType<typeof vi.fn>;

  beforeEach(async () => {
    vi.resetModules();

    mockNodesState = [];
    mockSetNodes = vi.fn((updater: unknown) => {
      if (typeof updater === "function") {
        mockNodesState = (updater as (nds: Record<string, unknown>[]) => Record<string, unknown>[])(mockNodesState);
      } else {
        mockNodesState = updater as Record<string, unknown>[];
      }
    });

    mockUpdateBoardNode = vi.fn(() => Promise.resolve({}));

    vi.doMock("@/api/board", () => ({
      updateBoardNode: (ideaId: string, nodeId: string, updates: Record<string, unknown>) =>
        mockUpdateBoardNode(ideaId, nodeId, updates),
      fetchBoardNodes: vi.fn(() => Promise.resolve([])),
      fetchBoardConnections: vi.fn(() => Promise.resolve([])),
      createBoardNode: vi.fn(() => Promise.resolve({})),
      deleteBoardNode: vi.fn(() => Promise.resolve()),
    }));

    vi.doMock("@/hooks/use-board-undo", () => ({
      useBoardUndo: () => ({ undo: vi.fn(), redo: vi.fn(), canUndo: false, canRedo: false }),
    }));

    vi.doMock("react-redux", () => ({
      useDispatch: () => vi.fn(),
      useSelector: (selector: (state: Record<string, unknown>) => unknown) =>
        selector({
          board: { undoStack: [], redoStack: [], selectedNodeIds: [] },
          selections: { byIdea: {} },
        }),
    }));

    vi.doMock("@/app/providers", () => ({
      useWsSend: () => vi.fn(),
    }));

    vi.doMock("@/hooks/use-auth", () => ({
      useAuth: () => ({ user: { id: "test-user", display_name: "Test User" }, isAuthenticated: true, isLoading: false }),
    }));

    vi.doMock("@xyflow/react", () => {
      const BackgroundVariant = { Dots: "dots", Lines: "lines", Cross: "cross" };
      const MarkerType = { Arrow: "arrow", ArrowClosed: "arrowclosed" };
      const SelectionMode = { Partial: "partial", Full: "full" };
      return {
        SelectionMode,
        ReactFlow: ({ children, onNodeClick, nodes, ...props }: Record<string, unknown>) => {
          capturedOnNodeClick = onNodeClick as typeof capturedOnNodeClick;
          return (
            <div data-testid="react-flow" {...props}>
              {children as React.ReactNode}
            </div>
          );
        },
        Background: (props: Record<string, unknown>) => <div {...props} />,
        BackgroundVariant,
        MarkerType,
        MiniMap: (props: Record<string, unknown>) => <div {...props} />,
        Controls: (props: Record<string, unknown>) => <div {...props} />,
        useNodesState: () => [mockNodesState, mockSetNodes, vi.fn()],
        useEdgesState: (init: unknown[]) => [init, vi.fn(), vi.fn()],
        useReactFlow: () => ({
          getViewport: vi.fn(() => ({ x: 0, y: 0, zoom: 1 })),
          fitView: vi.fn(),
          screenToFlowPosition: vi.fn((pos: { x: number; y: number }) => pos),
          getInternalNode: () => undefined,
        }),
      };
    });

    capturedOnNodeClick = undefined;
  });

  it("clicking node with ai_modified_indicator=true calls PATCH with false", async () => {
    mockNodesState = [
      {
        id: "n1",
        type: "box",
        position: { x: 0, y: 0 },
        data: { title: "Test", ai_modified_indicator: true, is_locked: false },
      },
    ];

    const { BoardCanvas } = await import("@/components/board/BoardCanvas");
    render(<BoardCanvas ideaId="idea-1" />);

    expect(capturedOnNodeClick).toBeDefined();

    // Simulate clicking the node with ai_modified_indicator=true
    const mockEvent = {} as React.MouseEvent;
    capturedOnNodeClick!(mockEvent, {
      id: "n1",
      type: "box",
      position: { x: 0, y: 0 },
      data: { title: "Test", ai_modified_indicator: true, is_locked: false },
    });

    expect(mockUpdateBoardNode).toHaveBeenCalledWith("idea-1", "n1", {
      ai_modified_indicator: false,
    });
  });

  it("clicking node with ai_modified_indicator=true clears it in local state", async () => {
    mockNodesState = [
      {
        id: "n1",
        type: "box",
        position: { x: 0, y: 0 },
        data: { title: "Test", ai_modified_indicator: true, is_locked: false },
      },
    ];

    const { BoardCanvas } = await import("@/components/board/BoardCanvas");
    render(<BoardCanvas ideaId="idea-1" />);

    capturedOnNodeClick!({} as React.MouseEvent, {
      id: "n1",
      type: "box",
      position: { x: 0, y: 0 },
      data: { title: "Test", ai_modified_indicator: true, is_locked: false },
    });

    // The setNodes callback should have cleared the indicator
    const updatedNode = mockNodesState.find((n) => n.id === "n1") as Record<string, unknown>;
    expect((updatedNode.data as Record<string, unknown>).ai_modified_indicator).toBe(false);
  });

  it("clicking node without ai_modified_indicator does not call PATCH", async () => {
    mockNodesState = [
      {
        id: "n2",
        type: "box",
        position: { x: 0, y: 0 },
        data: { title: "Test", ai_modified_indicator: false, is_locked: false },
      },
    ];

    const { BoardCanvas } = await import("@/components/board/BoardCanvas");
    render(<BoardCanvas ideaId="idea-1" />);

    capturedOnNodeClick!({} as React.MouseEvent, {
      id: "n2",
      type: "box",
      position: { x: 0, y: 0 },
      data: { title: "Test", ai_modified_indicator: false, is_locked: false },
    });

    expect(mockUpdateBoardNode).not.toHaveBeenCalled();
  });
});
