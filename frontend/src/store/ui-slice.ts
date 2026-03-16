import { createSlice } from "@reduxjs/toolkit";

const uiSlice = createSlice({
  name: "ui",
  initialState: {
    dividerPosition: 50,
    activeTab: "chat" as "chat" | "review",
  },
  reducers: {},
});

export const uiReducer = uiSlice.reducer;
