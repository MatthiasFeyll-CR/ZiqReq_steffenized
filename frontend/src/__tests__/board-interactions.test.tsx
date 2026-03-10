import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import i18n from "@/i18n/config";

const mockUpdateBoardNode = vi.fn<(ideaId: string, nodeId: string, updates: Record<string, unknown>) => Promise<unknown>>(
  () => Promise.resolve({}),
);
vi.mock("@/api/board", () => ({
  updateBoardNode: (ideaId: string, nodeId: string, updates: Record<string, unknown>) =>
    mockUpdateBoardNode(ideaId, nodeId, updates),
}));

let capturedOnNodeDragStop: ((...args: unknown[]) => void) | undefined;

vi.mock("@xyflow/react", () => {
  const BackgroundVariant = { Dots: "dots", Lines: "lines", Cross: "cross" };
  const MarkerType = { Arrow: "arrow", ArrowClosed: "arrowclosed" };
  return {
    ReactFlow: ({ children, onNodeDragStop, ...props }: Record<string, unknown>) => {
      capturedOnNodeDragStop = onNodeDragStop as typeof capturedOnNodeDragStop;
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
    useNodesState: (init: unknown[]) => [init, vi.fn(), vi.fn()],
    useEdgesState: (init: unknown[]) => [init, vi.fn(), vi.fn()],
    useReactFlow: () => ({ getViewport: vi.fn(() => ({ x: 0, y: 0, zoom: 1 })), fitView: vi.fn() }),
  };
});

import { BoardCanvas } from "@/components/board/BoardCanvas";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

beforeEach(() => {
  mockUpdateBoardNode.mockClear();
  capturedOnNodeDragStop = undefined;
});

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
