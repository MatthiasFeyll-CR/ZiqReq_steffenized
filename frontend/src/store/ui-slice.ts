import { createSlice } from "@reduxjs/toolkit";

const uiSlice = createSlice({
  name: "ui",
  initialState: {
    dividerPosition: 50,
    activeTab: "board" as "board" | "review",
  },
  reducers: {},
});

export const uiReducer = uiSlice.reducer;
