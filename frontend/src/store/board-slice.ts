import { createSlice } from "@reduxjs/toolkit";

const boardSlice = createSlice({
  name: "board",
  initialState: {
    undoStack: [] as unknown[],
    redoStack: [] as unknown[],
    selectedNodeIds: [] as string[],
  },
  reducers: {},
});

export const boardReducer = boardSlice.reducer;
