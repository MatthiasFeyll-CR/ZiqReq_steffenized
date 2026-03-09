import { createSlice } from "@reduxjs/toolkit";

const websocketSlice = createSlice({
  name: "websocket",
  initialState: {
    connected: false,
    reconnecting: false,
  },
  reducers: {},
});

export const websocketReducer = websocketSlice.reducer;
