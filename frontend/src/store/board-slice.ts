import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { RootState } from "./index";

const MAX_UNDO_STACK = 100;

export interface UndoEntry {
  type: string;
  nodeId: string;
  data: Record<string, unknown>;
  previousState: Record<string, unknown>;
  source: "user" | "ai";
}

interface BoardState {
  undoStack: UndoEntry[];
  redoStack: UndoEntry[];
  selectedNodeIds: string[];
}

const initialState: BoardState = {
  undoStack: [],
  redoStack: [],
  selectedNodeIds: [],
};

const boardSlice = createSlice({
  name: "board",
  initialState,
  reducers: {
    pushAction(state, action: PayloadAction<UndoEntry>) {
      state.undoStack.push(action.payload);
      if (state.undoStack.length > MAX_UNDO_STACK) {
        state.undoStack.shift();
      }
      state.redoStack = [];
    },
    undo(state) {
      const entry = state.undoStack.pop();
      if (entry) {
        state.redoStack.push(entry);
      }
    },
    redo(state) {
      const entry = state.redoStack.pop();
      if (entry) {
        state.undoStack.push(entry);
      }
    },
  },
});

export const { pushAction, undo, redo } = boardSlice.actions;

export const selectUndoStack = (state: RootState) => state.board.undoStack;
export const selectRedoStack = (state: RootState) => state.board.redoStack;
export const selectCanUndo = (state: RootState) => state.board.undoStack.length > 0;
export const selectCanRedo = (state: RootState) => state.board.redoStack.length > 0;
export const selectUndoTop = (state: RootState) =>
  state.board.undoStack.length > 0
    ? state.board.undoStack[state.board.undoStack.length - 1]
    : null;
export const selectRedoTop = (state: RootState) =>
  state.board.redoStack.length > 0
    ? state.board.redoStack[state.board.redoStack.length - 1]
    : null;

export const boardReducer = boardSlice.reducer;
