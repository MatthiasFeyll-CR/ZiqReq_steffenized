import { createSlice } from "@reduxjs/toolkit";

const rateLimitSlice = createSlice({
  name: "rateLimit",
  initialState: {
    lockedProjectIds: [] as string[],
  },
  reducers: {},
});

export const rateLimitReducer = rateLimitSlice.reducer;
