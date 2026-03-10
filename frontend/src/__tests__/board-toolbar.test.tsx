import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import i18n from "@/i18n/config";

// Mock @xyflow/react
const mockFitView = vi.fn();
const mockScreenToFlowPosition = vi.fn(() => ({ x: 0, y: 0 }));

vi.mock("@xyflow/react", () => ({
  useReactFlow: () => ({
    fitView: mockFitView,
    screenToFlowPosition: mockScreenToFlowPosition,
  }),
}));

import { BoardToolbar } from "@/components/board/BoardToolbar";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

beforeEach(() => {
  mockFitView.mockClear();
  mockScreenToFlowPosition.mockClear();
});

describe("T-3.3.03: BoardToolbar button actions", () => {
  it("click Add Box calls onAddBox callback", () => {
    const onAddBox = vi.fn();
    const onDeleteSelected = vi.fn();
    render(
      <BoardToolbar
        selectedCount={0}
        onAddBox={onAddBox}
        onDeleteSelected={onDeleteSelected}
      />,
    );
    fireEvent.click(screen.getByTestId("toolbar-add-box"));
    expect(onAddBox).toHaveBeenCalled();
  });

  it("click Fit View invokes fitView from useReactFlow", () => {
    const onAddBox = vi.fn();
    const onDeleteSelected = vi.fn();
    render(
      <BoardToolbar
        selectedCount={0}
        onAddBox={onAddBox}
        onDeleteSelected={onDeleteSelected}
      />,
    );
    fireEvent.click(screen.getByTestId("toolbar-fit-view"));
    expect(mockFitView).toHaveBeenCalled();
  });

  it("delete button is disabled when selectedCount=0", () => {
    const onAddBox = vi.fn();
    const onDeleteSelected = vi.fn();
    render(
      <BoardToolbar
        selectedCount={0}
        onAddBox={onAddBox}
        onDeleteSelected={onDeleteSelected}
      />,
    );
    const deleteBtn = screen.getByTestId("toolbar-delete");
    expect(deleteBtn).toBeDisabled();
  });

  it("delete button is enabled when selectedCount=1 and calls onDeleteSelected", () => {
    const onAddBox = vi.fn();
    const onDeleteSelected = vi.fn();
    render(
      <BoardToolbar
        selectedCount={1}
        onAddBox={onAddBox}
        onDeleteSelected={onDeleteSelected}
      />,
    );
    const deleteBtn = screen.getByTestId("toolbar-delete");
    expect(deleteBtn).not.toBeDisabled();
    fireEvent.click(deleteBtn);
    expect(onDeleteSelected).toHaveBeenCalled();
  });
});
