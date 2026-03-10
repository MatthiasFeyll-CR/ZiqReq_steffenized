import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import i18n from "@/i18n/config";

const mockUpdateBoardNode = vi.fn<(ideaId: string, nodeId: string, updates: Record<string, unknown>) => Promise<unknown>>(
  () => Promise.resolve({}),
);
vi.mock("@/api/board", () => ({
  updateBoardNode: (ideaId: string, nodeId: string, updates: Record<string, unknown>) =>
    mockUpdateBoardNode(ideaId, nodeId, updates),
}));

const mockDispatch = vi.fn();
vi.mock("react-redux", () => ({
  useDispatch: () => mockDispatch,
  useSelector: (selector: (state: Record<string, unknown>) => unknown) =>
    selector({
      board: {
        undoStack: [],
        redoStack: [],
        selectedNodeIds: [],
      },
    }),
}));

let capturedOnNodeDragStop: ((...args: unknown[]) => void) | undefined;
let capturedOnNodeDrag: ((...args: unknown[]) => void) | undefined;
let capturedNodes: Array<Record<string, unknown>> | undefined;

// Stateful mock for useNodesState so setNodes callback pattern works
let mockNodesState: Record<string, unknown>[] = [];
const mockSetNodes = vi.fn((updater: unknown) => {
  if (typeof updater === "function") {
    mockNodesState = (updater as (nds: Record<string, unknown>[]) => Record<string, unknown>[])(mockNodesState);
  } else {
    mockNodesState = updater as Record<string, unknown>[];
  }
});

// Map of node internals for getInternalNode mock
let mockInternals: Record<string, { internals: { positionAbsolute: { x: number; y: number } }; measured: { width?: number; height?: number } }> = {};

vi.mock("@xyflow/react", () => {
  const BackgroundVariant = { Dots: "dots", Lines: "lines", Cross: "cross" };
  const MarkerType = { Arrow: "arrow", ArrowClosed: "arrowclosed" };
  const SelectionMode = { Partial: "partial", Full: "full" };
  return {
    SelectionMode,
    ReactFlow: ({ children, onNodeDragStop, onNodeDrag, nodes, ...props }: Record<string, unknown>) => {
      capturedOnNodeDragStop = onNodeDragStop as typeof capturedOnNodeDragStop;
      capturedOnNodeDrag = onNodeDrag as typeof capturedOnNodeDrag;
      capturedNodes = nodes as typeof capturedNodes;
      return (
        <div data-testid="react-flow" {...props}>
          {children as React.ReactNode}
        </div>
      );
    },
    Background: (props: Record<string, unknown>) => <div data-testid="rf-background" {...props} />,
    BackgroundVariant,
    MarkerType,
    MiniMap: (props: Record<string, unknown>) => <div data-testid="rf-minimap" {...props} />,
    Controls: (props: Record<string, unknown>) => <div data-testid="rf-controls" {...props} />,
    useNodesState: () => [mockNodesState, mockSetNodes, vi.fn()],
    useEdgesState: (init: unknown[]) => [init, vi.fn(), vi.fn()],
    useReactFlow: () => ({
      getViewport: vi.fn(() => ({ x: 0, y: 0, zoom: 1 })),
      fitView: vi.fn(),
      screenToFlowPosition: vi.fn((pos: { x: number; y: number }) => pos),
      getInternalNode: (id: string) => mockInternals[id] ?? undefined,
    }),
  };
});

import { BoardCanvas } from "@/components/board/BoardCanvas";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

beforeEach(() => {
  mockUpdateBoardNode.mockClear();
  mockSetNodes.mockClear();
  mockDispatch.mockClear();
  capturedOnNodeDragStop = undefined;
  capturedOnNodeDrag = undefined;
  capturedNodes = undefined;
  mockNodesState = [];
  mockInternals = {};
});

/** Helper to set up nodes state and internals together */
function setupNodes(
  nodesData: Array<{
    id: string;
    type: string;
    parentId?: string;
    position: { x: number; y: number };
    absPosition: { x: number; y: number };
    width?: number;
    height?: number;
    data?: Record<string, unknown>;
  }>,
) {
  mockNodesState = nodesData.map(({ absPosition, ...rest }) => ({
    ...rest,
    data: rest.data ?? {},
  }));
  mockInternals = {};
  for (const n of nodesData) {
    mockInternals[n.id] = {
      internals: { positionAbsolute: n.absPosition },
      measured: { width: n.width, height: n.height },
    };
  }
}

describe("T-3.2.01: Drag moves node — position updates via REST", () => {
  it("calls updateBoardNode with new position on drag end", () => {
    render(<BoardCanvas ideaId="idea-123" />);

    expect(capturedOnNodeDragStop).toBeDefined();

    const mockEvent = {} as React.MouseEvent;
    const mockNode = {
      id: "node-456",
      position: { x: 100.5, y: 200.7 },
      data: {},
    };

    capturedOnNodeDragStop!(mockEvent, mockNode, [mockNode]);

    expect(mockUpdateBoardNode).toHaveBeenCalledWith("idea-123", "node-456", {
      position_x: 100.5,
      position_y: 200.7,
    });
  });

  it("does not call updateBoardNode when ideaId is not provided", () => {
    render(<BoardCanvas />);

    expect(capturedOnNodeDragStop).toBeDefined();

    const mockEvent = {} as React.MouseEvent;
    const mockNode = {
      id: "node-456",
      position: { x: 100, y: 200 },
      data: {},
    };

    capturedOnNodeDragStop!(mockEvent, mockNode, [mockNode]);

    expect(mockUpdateBoardNode).not.toHaveBeenCalled();
  });

  it("passes onNodeDragStop to ReactFlow component", () => {
    render(<BoardCanvas ideaId="idea-123" />);

    expect(screen.getByTestId("react-flow")).toBeInTheDocument();
    expect(capturedOnNodeDragStop).toBeInstanceOf(Function);
  });
});

describe("T-3.2.02: Drag box into group sets parent_id", () => {
  it("calls updateBoardNode with parent_id when node dropped inside a group", () => {
    setupNodes([
      {
        id: "group-1",
        type: "group",
        position: { x: 0, y: 0 },
        absPosition: { x: 0, y: 0 },
        width: 400,
        height: 300,
        data: { title: "Test Group" },
      },
      {
        id: "box-1",
        type: "box",
        position: { x: 500, y: 500 },
        absPosition: { x: 500, y: 500 },
        data: { title: "Test Box" },
      },
    ]);

    render(<BoardCanvas ideaId="idea-123" />);
    expect(capturedOnNodeDragStop).toBeDefined();

    // Also set up the internal for box-1 at its new dragged position
    mockInternals["box-1"] = {
      internals: { positionAbsolute: { x: 100, y: 100 } },
      measured: { width: 192, height: 80 },
    };

    const mockEvent = {} as React.MouseEvent;
    const mockNode = {
      id: "box-1",
      type: "box",
      position: { x: 100, y: 100 },
      data: { title: "Test Box" },
    };

    capturedOnNodeDragStop!(mockEvent, mockNode, [mockNode]);

    expect(mockUpdateBoardNode).toHaveBeenCalledWith(
      "idea-123",
      "box-1",
      expect.objectContaining({ parent_id: "group-1" }),
    );
  });

  it("updates node parentId in React Flow state when dropped into group", () => {
    setupNodes([
      {
        id: "group-1",
        type: "group",
        position: { x: 0, y: 0 },
        absPosition: { x: 0, y: 0 },
        width: 400,
        height: 300,
        data: { title: "Test Group" },
      },
      {
        id: "box-1",
        type: "box",
        position: { x: 500, y: 500 },
        absPosition: { x: 500, y: 500 },
        data: { title: "Test Box" },
      },
    ]);

    render(<BoardCanvas ideaId="idea-123" />);

    mockInternals["box-1"] = {
      internals: { positionAbsolute: { x: 100, y: 100 } },
      measured: { width: 192, height: 80 },
    };

    const mockEvent = {} as React.MouseEvent;
    const mockNode = {
      id: "box-1",
      type: "box",
      position: { x: 100, y: 100 },
      data: { title: "Test Box" },
    };

    capturedOnNodeDragStop!(mockEvent, mockNode, [mockNode]);

    const updatedBox = mockNodesState.find((n) => n.id === "box-1") as { parentId?: string } | undefined;
    expect(updatedBox?.parentId).toBe("group-1");
  });
});

describe("T-3.2.03: Drag box out of group clears parent_id", () => {
  it("calls updateBoardNode with parent_id null when node dragged outside all groups", () => {
    setupNodes([
      {
        id: "group-1",
        type: "group",
        position: { x: 0, y: 0 },
        absPosition: { x: 0, y: 0 },
        width: 400,
        height: 300,
        data: { title: "Test Group" },
      },
      {
        id: "box-1",
        type: "box",
        parentId: "group-1",
        position: { x: 50, y: 50 },
        absPosition: { x: 50, y: 50 },
        data: { title: "Test Box" },
      },
    ]);

    render(<BoardCanvas ideaId="idea-123" />);
    expect(capturedOnNodeDragStop).toBeDefined();

    // Box dragged outside group bounds
    mockInternals["box-1"] = {
      internals: { positionAbsolute: { x: 500, y: 500 } },
      measured: { width: 192, height: 80 },
    };

    const mockEvent = {} as React.MouseEvent;
    const mockNode = {
      id: "box-1",
      type: "box",
      parentId: "group-1",
      position: { x: 500, y: 500 },
      data: { title: "Test Box" },
    };

    capturedOnNodeDragStop!(mockEvent, mockNode, [mockNode]);

    expect(mockUpdateBoardNode).toHaveBeenCalledWith(
      "idea-123",
      "box-1",
      expect.objectContaining({ parent_id: null }),
    );
  });

  it("clears parentId in React Flow state when dragged out of group", () => {
    setupNodes([
      {
        id: "group-1",
        type: "group",
        position: { x: 0, y: 0 },
        absPosition: { x: 0, y: 0 },
        width: 400,
        height: 300,
        data: { title: "Test Group" },
      },
      {
        id: "box-1",
        type: "box",
        parentId: "group-1",
        position: { x: 50, y: 50 },
        absPosition: { x: 50, y: 50 },
        data: { title: "Test Box" },
      },
    ]);

    render(<BoardCanvas ideaId="idea-123" />);

    mockInternals["box-1"] = {
      internals: { positionAbsolute: { x: 500, y: 500 } },
      measured: { width: 192, height: 80 },
    };

    const mockEvent = {} as React.MouseEvent;
    const mockNode = {
      id: "box-1",
      type: "box",
      parentId: "group-1",
      position: { x: 500, y: 500 },
      data: { title: "Test Box" },
    };

    capturedOnNodeDragStop!(mockEvent, mockNode, [mockNode]);

    const updatedBox = mockNodesState.find((n) => n.id === "box-1") as { parentId?: string } | undefined;
    expect(updatedBox?.parentId).toBeUndefined();
  });
});

describe("Group nesting: visual drop zone feedback", () => {
  it("passes onNodeDrag to ReactFlow for hover detection", () => {
    render(<BoardCanvas ideaId="idea-123" />);
    expect(capturedOnNodeDrag).toBeInstanceOf(Function);
  });

  it("sets _dropTarget on group data when node dragged over it", () => {
    setupNodes([
      {
        id: "group-1",
        type: "group",
        position: { x: 0, y: 0 },
        absPosition: { x: 0, y: 0 },
        width: 400,
        height: 300,
        data: { title: "Test Group" },
      },
      {
        id: "box-1",
        type: "box",
        position: { x: 500, y: 500 },
        absPosition: { x: 500, y: 500 },
        data: { title: "Test Box" },
      },
    ]);

    render(<BoardCanvas ideaId="idea-123" />);

    mockInternals["box-1"] = {
      internals: { positionAbsolute: { x: 100, y: 100 } },
      measured: { width: 192, height: 80 },
    };

    const mockEvent = {} as React.MouseEvent;
    const mockNode = {
      id: "box-1",
      type: "box",
      position: { x: 100, y: 100 },
      data: { title: "Test Box" },
    };

    capturedOnNodeDrag!(mockEvent, mockNode, [mockNode]);

    const group = mockNodesState.find((n) => n.id === "group-1") as { data: { _dropTarget?: boolean } } | undefined;
    expect(group?.data._dropTarget).toBe(true);
  });
});

describe("Group nesting: nested groups supported", () => {
  it("selects the smallest (most nested) group when groups overlap", () => {
    setupNodes([
      {
        id: "outer-group",
        type: "group",
        position: { x: 0, y: 0 },
        absPosition: { x: 0, y: 0 },
        width: 600,
        height: 500,
        data: { title: "Outer" },
      },
      {
        id: "inner-group",
        type: "group",
        parentId: "outer-group",
        position: { x: 50, y: 50 },
        absPosition: { x: 50, y: 50 },
        width: 200,
        height: 200,
        data: { title: "Inner" },
      },
      {
        id: "box-1",
        type: "box",
        position: { x: 700, y: 700 },
        absPosition: { x: 700, y: 700 },
        data: { title: "Test Box" },
      },
    ]);

    render(<BoardCanvas ideaId="idea-123" />);

    // Drop at 100,100 — inside both outer (0,0-600,500) and inner (50,50-250,250)
    mockInternals["box-1"] = {
      internals: { positionAbsolute: { x: 100, y: 100 } },
      measured: { width: 192, height: 80 },
    };

    const mockEvent = {} as React.MouseEvent;
    const mockNode = {
      id: "box-1",
      type: "box",
      position: { x: 100, y: 100 },
      data: { title: "Test Box" },
    };

    capturedOnNodeDragStop!(mockEvent, mockNode, [mockNode]);

    // Should nest into inner group (smaller area)
    expect(mockUpdateBoardNode).toHaveBeenCalledWith(
      "idea-123",
      "box-1",
      expect.objectContaining({ parent_id: "inner-group" }),
    );
  });
});

describe("T-3.2.07: Lock toggle prevents editing and dragging", () => {
  it("sets draggable=false on locked nodes passed to ReactFlow", () => {
    setupNodes([
      {
        id: "box-1",
        type: "box",
        position: { x: 0, y: 0 },
        absPosition: { x: 0, y: 0 },
        data: { title: "Locked Box", is_locked: true },
      },
      {
        id: "box-2",
        type: "box",
        position: { x: 200, y: 0 },
        absPosition: { x: 200, y: 0 },
        data: { title: "Unlocked Box", is_locked: false },
      },
    ]);

    render(<BoardCanvas ideaId="idea-123" />);

    expect(capturedNodes).toBeDefined();
    const lockedNode = capturedNodes!.find((n) => n.id === "box-1");
    const unlockedNode = capturedNodes!.find((n) => n.id === "box-2");
    expect(lockedNode?.draggable).toBe(false);
    expect(unlockedNode?.draggable).toBe(true);
  });

  it("calls updateBoardNode with is_locked when lock is toggled", () => {
    setupNodes([
      {
        id: "box-1",
        type: "box",
        position: { x: 0, y: 0 },
        absPosition: { x: 0, y: 0 },
        data: { title: "Test Box", is_locked: false },
      },
    ]);

    render(<BoardCanvas ideaId="idea-123" />);

    // The processedNodes inject onToggleLock into data — invoke it directly
    expect(capturedNodes).toBeDefined();
    const node = capturedNodes!.find((n) => n.id === "box-1");
    const data = node?.data as { onToggleLock?: (nodeId: string, locked: boolean) => void };
    expect(data?.onToggleLock).toBeInstanceOf(Function);

    data!.onToggleLock!("box-1", true);

    expect(mockUpdateBoardNode).toHaveBeenCalledWith("idea-123", "box-1", {
      is_locked: true,
    });
  });

  it("updates node data is_locked in state when toggled", () => {
    setupNodes([
      {
        id: "box-1",
        type: "box",
        position: { x: 0, y: 0 },
        absPosition: { x: 0, y: 0 },
        data: { title: "Test Box", is_locked: false },
      },
    ]);

    render(<BoardCanvas ideaId="idea-123" />);

    const node = capturedNodes!.find((n) => n.id === "box-1");
    const data = node?.data as { onToggleLock?: (nodeId: string, locked: boolean) => void };
    data!.onToggleLock!("box-1", true);

    const updatedNode = mockNodesState.find((n) => n.id === "box-1") as { data: { is_locked?: boolean } };
    expect(updatedNode?.data.is_locked).toBe(true);
  });

  it("does not call updateBoardNode when ideaId is not provided", () => {
    setupNodes([
      {
        id: "box-1",
        type: "box",
        position: { x: 0, y: 0 },
        absPosition: { x: 0, y: 0 },
        data: { title: "Test Box", is_locked: false },
      },
    ]);

    render(<BoardCanvas />);

    const node = capturedNodes!.find((n) => n.id === "box-1");
    const data = node?.data as { onToggleLock?: (nodeId: string, locked: boolean) => void };
    data!.onToggleLock!("box-1", true);

    expect(mockUpdateBoardNode).not.toHaveBeenCalled();
  });

  it("locked nodes are not deleted by handleDeleteSelected", () => {
    setupNodes([
      {
        id: "box-1",
        type: "box",
        position: { x: 0, y: 0 },
        absPosition: { x: 0, y: 0 },
        data: { title: "Locked Box", is_locked: true },
      },
      {
        id: "box-2",
        type: "box",
        position: { x: 200, y: 0 },
        absPosition: { x: 200, y: 0 },
        data: { title: "Unlocked Box", is_locked: false },
      },
    ]);
    // Mark both as selected
    mockNodesState = mockNodesState.map((n) => ({ ...n, selected: true }));

    render(<BoardCanvas ideaId="idea-123" />);

    // Click the delete button
    const deleteBtn = screen.getByTestId("toolbar-delete");
    fireEvent.click(deleteBtn);

    // Locked node should remain
    expect(mockNodesState.find((n) => n.id === "box-1")).toBeDefined();
    // Unlocked selected node should be deleted
    expect(mockNodesState.find((n) => n.id === "box-2")).toBeUndefined();
  });
});
