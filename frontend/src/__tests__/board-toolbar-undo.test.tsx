import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

vi.mock("@xyflow/react", () => ({
  useReactFlow: () => ({
    fitView: vi.fn(),
    screenToFlowPosition: vi.fn(() => ({ x: 0, y: 0 })),
  }),
}));

import { BoardToolbar } from "@/components/board/BoardToolbar";

const baseProps = {
  selectedCount: 0,
  onAddBox: vi.fn(),
  onDeleteSelected: vi.fn(),
  onUndo: vi.fn(),
  onRedo: vi.fn(),
};

describe("T-3.7.03: AI action undo shows 'Undo AI Action' label", () => {
  it("shows 'Undo AI Action' when undo stack top source is 'ai'", () => {
    render(
      <BoardToolbar
        {...baseProps}
        canUndo={true}
        undoTopSource="ai"
      />,
    );
    const undoBtn = screen.getByTestId("toolbar-undo");
    expect(undoBtn).toHaveAttribute("title", "Undo AI Action");
  });

  it("shows 'Undo' when undo stack top source is 'user'", () => {
    render(
      <BoardToolbar
        {...baseProps}
        canUndo={true}
        undoTopSource="user"
      />,
    );
    const undoBtn = screen.getByTestId("toolbar-undo");
    expect(undoBtn).toHaveAttribute("title", "Undo");
  });

  it("shows 'Redo AI Action' when redo stack top source is 'ai'", () => {
    render(
      <BoardToolbar
        {...baseProps}
        canRedo={true}
        redoTopSource="ai"
      />,
    );
    const redoBtn = screen.getByTestId("toolbar-redo");
    expect(redoBtn).toHaveAttribute("title", "Redo AI Action");
  });

  it("shows 'Redo' when redo stack top source is 'user'", () => {
    render(
      <BoardToolbar
        {...baseProps}
        canRedo={true}
        redoTopSource="user"
      />,
    );
    const redoBtn = screen.getByTestId("toolbar-redo");
    expect(redoBtn).toHaveAttribute("title", "Redo");
  });

  it("disables undo button when canUndo is false", () => {
    render(
      <BoardToolbar
        {...baseProps}
        canUndo={false}
        canRedo={true}
      />,
    );
    const undoBtn = screen.getByTestId("toolbar-undo");
    expect(undoBtn).toBeDisabled();
  });

  it("disables redo button when canRedo is false", () => {
    render(
      <BoardToolbar
        {...baseProps}
        canUndo={true}
        canRedo={false}
      />,
    );
    const redoBtn = screen.getByTestId("toolbar-redo");
    expect(redoBtn).toBeDisabled();
  });

  it("calls onUndo when undo button clicked", async () => {
    const onUndo = vi.fn();
    render(
      <BoardToolbar
        {...baseProps}
        onUndo={onUndo}
        canUndo={true}
      />,
    );
    await userEvent.click(screen.getByTestId("toolbar-undo"));
    expect(onUndo).toHaveBeenCalledOnce();
  });

  it("calls onRedo when redo button clicked", async () => {
    const onRedo = vi.fn();
    render(
      <BoardToolbar
        {...baseProps}
        onRedo={onRedo}
        canRedo={true}
      />,
    );
    await userEvent.click(screen.getByTestId("toolbar-redo"));
    expect(onRedo).toHaveBeenCalledOnce();
  });
});
