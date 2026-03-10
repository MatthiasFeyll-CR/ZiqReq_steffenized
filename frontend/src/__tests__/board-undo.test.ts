import { describe, it, expect } from "vitest";
import {
  boardReducer,
  pushAction,
  undo,
  redo,
  type UndoEntry,
} from "@/store/board-slice";

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

const initialState = {
  undoStack: [] as UndoEntry[],
  redoStack: [] as UndoEntry[],
  selectedNodeIds: [] as string[],
};

describe("T-3.7.01: Undo reverses last board action", () => {
  it("undo pops from undoStack and pushes to redoStack", () => {
    const entry = makeEntry();
    const stateWithAction = boardReducer(initialState, pushAction(entry));
    expect(stateWithAction.undoStack).toHaveLength(1);

    const stateAfterUndo = boardReducer(stateWithAction, undo());
    expect(stateAfterUndo.undoStack).toHaveLength(0);
    expect(stateAfterUndo.redoStack).toHaveLength(1);
    expect(stateAfterUndo.redoStack[0]).toEqual(entry);
  });

  it("undo with empty stack is a no-op", () => {
    const state = boardReducer(initialState, undo());
    expect(state.undoStack).toHaveLength(0);
    expect(state.redoStack).toHaveLength(0);
  });

  it("undo preserves remaining undo entries", () => {
    const entry1 = makeEntry({ nodeId: "node-1" });
    const entry2 = makeEntry({ nodeId: "node-2" });
    let state = boardReducer(initialState, pushAction(entry1));
    state = boardReducer(state, pushAction(entry2));
    expect(state.undoStack).toHaveLength(2);

    state = boardReducer(state, undo());
    expect(state.undoStack).toHaveLength(1);
    expect(state.undoStack[0]!.nodeId).toBe("node-1");
    expect(state.redoStack[0]!.nodeId).toBe("node-2");
  });
});

describe("T-3.7.02: Redo re-applies undone action", () => {
  it("redo pops from redoStack and pushes to undoStack", () => {
    const entry = makeEntry();
    let state = boardReducer(initialState, pushAction(entry));
    state = boardReducer(state, undo());
    expect(state.redoStack).toHaveLength(1);

    state = boardReducer(state, redo());
    expect(state.undoStack).toHaveLength(1);
    expect(state.redoStack).toHaveLength(0);
    expect(state.undoStack[0]).toEqual(entry);
  });

  it("redo with empty stack is a no-op", () => {
    const state = boardReducer(initialState, redo());
    expect(state.undoStack).toHaveLength(0);
    expect(state.redoStack).toHaveLength(0);
  });
});

describe("New action clears redo stack", () => {
  it("pushAction clears the redo stack", () => {
    const entry1 = makeEntry({ nodeId: "node-1" });
    const entry2 = makeEntry({ nodeId: "node-2" });

    let state = boardReducer(initialState, pushAction(entry1));
    state = boardReducer(state, undo());
    expect(state.redoStack).toHaveLength(1);

    state = boardReducer(state, pushAction(entry2));
    expect(state.redoStack).toHaveLength(0);
    expect(state.undoStack).toHaveLength(1);
    expect(state.undoStack[0]!.nodeId).toBe("node-2");
  });
});

describe("T-3.7.04: Undo stack bounded at 100 entries", () => {
  it("drops oldest entry when stack exceeds 100", () => {
    let state = { ...initialState };
    for (let i = 0; i < 101; i++) {
      state = boardReducer(state, pushAction(makeEntry({ nodeId: `node-${i}` })));
    }

    expect(state.undoStack).toHaveLength(100);
    expect(state.undoStack[0]!.nodeId).toBe("node-1");
    expect(state.undoStack[99]!.nodeId).toBe("node-100");
  });
});

describe("UndoEntry structure", () => {
  it("each action has {type, data, previousState, source}", () => {
    const entry = makeEntry({
      type: "toggle_lock",
      nodeId: "n-1",
      data: { is_locked: true },
      previousState: { is_locked: false },
      source: "user",
    });
    const state = boardReducer(initialState, pushAction(entry));
    const stored = state.undoStack[0]!;
    expect(stored.type).toBe("toggle_lock");
    expect(stored.data).toEqual({ is_locked: true });
    expect(stored.previousState).toEqual({ is_locked: false });
    expect(stored.source).toBe("user");
    expect(stored.nodeId).toBe("n-1");
  });
});
