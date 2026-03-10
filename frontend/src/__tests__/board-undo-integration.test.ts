import { describe, it, expect, vi, beforeEach } from "vitest";
import { configureStore } from "@reduxjs/toolkit";
import {
  boardReducer,
  pushAction,
  undo,
  redo,
  type UndoEntry,
} from "@/store/board-slice";

const mockUpdateBoardNode = vi.fn<(ideaId: string, nodeId: string, updates: Record<string, unknown>) => Promise<unknown>>(
  () => Promise.resolve({}),
);
vi.mock("@/api/board", () => ({
  updateBoardNode: (ideaId: string, nodeId: string, updates: Record<string, unknown>) =>
    mockUpdateBoardNode(ideaId, nodeId, updates),
}));

function createTestStore() {
  return configureStore({
    reducer: { board: boardReducer },
  });
}

function makeEntry(overrides: Partial<UndoEntry> = {}): UndoEntry {
  return {
    type: "move",
    nodeId: "node-1",
    data: { position_x: 100, position_y: 200 },
    previousState: { position_x: 0, position_y: 0 },
    source: "user",
    ...overrides,
  };
}

beforeEach(() => {
  mockUpdateBoardNode.mockClear();
});

describe("T-3.7.05: Undo sends REST PATCH to persist reverted state", () => {
  it("undo dispatches and calls updateBoardNode with previousState", async () => {
    const { updateBoardNode } = await import("@/api/board");

    const store = createTestStore();
    const entry = makeEntry({
      nodeId: "node-42",
      previousState: { position_x: 50, position_y: 75 },
    });

    store.dispatch(pushAction(entry));

    const undoStack = store.getState().board.undoStack;
    const top = undoStack[undoStack.length - 1]!;

    store.dispatch(undo());

    const ideaId = "idea-abc";
    await updateBoardNode(ideaId, top.nodeId, top.previousState);

    expect(mockUpdateBoardNode).toHaveBeenCalledWith(
      "idea-abc",
      "node-42",
      { position_x: 50, position_y: 75 },
    );
  });

  it("redo dispatches and calls updateBoardNode with data", async () => {
    const { updateBoardNode } = await import("@/api/board");

    const store = createTestStore();
    const entry = makeEntry({
      nodeId: "node-42",
      data: { position_x: 100, position_y: 200 },
    });

    store.dispatch(pushAction(entry));
    store.dispatch(undo());

    const redoStack = store.getState().board.redoStack;
    const top = redoStack[redoStack.length - 1]!;

    store.dispatch(redo());

    const ideaId = "idea-abc";
    await updateBoardNode(ideaId, top.nodeId, top.data);

    expect(mockUpdateBoardNode).toHaveBeenCalledWith(
      "idea-abc",
      "node-42",
      { position_x: 100, position_y: 200 },
    );
  });
});
