import { createSlice } from "@reduxjs/toolkit";

const rateLimitSlice = createSlice({
  name: "rateLimit",
  initialState: {
    lockedIdeaIds: [] as string[],
  },
  reducers: {},
});

export const rateLimitReducer = rateLimitSlice.reducer;
