import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { RootState } from "./index";

export type ConnectionState = "online" | "offline";

interface WebsocketState {
  connectionState: ConnectionState;
  reconnectCountdown: number | null;
}

const initialState: WebsocketState = {
  connectionState: "offline",
  reconnectCountdown: null,
};

const websocketSlice = createSlice({
  name: "websocket",
  initialState,
  reducers: {
    setConnectionState(state, action: PayloadAction<ConnectionState>) {
      state.connectionState = action.payload;
      if (action.payload === "online") {
        state.reconnectCountdown = null;
      }
    },
    setReconnectCountdown(state, action: PayloadAction<number | null>) {
      state.reconnectCountdown = action.payload;
    },
  },
});

export const { setConnectionState, setReconnectCountdown } =
  websocketSlice.actions;

export const selectConnectionState = (state: RootState) =>
  state.websocket.connectionState;
export const selectReconnectCountdown = (state: RootState) =>
  state.websocket.reconnectCountdown;
export const selectIsOnline = (state: RootState) =>
  state.websocket.connectionState === "online";

export const websocketReducer = websocketSlice.reducer;
