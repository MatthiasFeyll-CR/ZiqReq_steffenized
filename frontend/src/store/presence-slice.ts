import { createSlice } from "@reduxjs/toolkit";

const presenceSlice = createSlice({
  name: "presence",
  initialState: {
    onlineUsers: [] as string[],
    idleUsers: [] as string[],
  },
  reducers: {},
});

export const presenceReducer = presenceSlice.reducer;
