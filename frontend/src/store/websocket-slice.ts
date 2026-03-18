import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { RootState } from "./index";

export type ConnectionState = "online" | "offline";

interface WebsocketState {
  connectionState: ConnectionState;
  reconnectCountdown: number | null;
  isIdleDisconnected: boolean;
  hasEverConnected: boolean;
}

const initialState: WebsocketState = {
  connectionState: "offline",
  reconnectCountdown: null,
  isIdleDisconnected: false,
  hasEverConnected: false,
};

const websocketSlice = createSlice({
  name: "websocket",
  initialState,
  reducers: {
    setConnectionState(state, action: PayloadAction<ConnectionState>) {
      state.connectionState = action.payload;
      if (action.payload === "online") {
        state.reconnectCountdown = null;
        state.isIdleDisconnected = false;
        state.hasEverConnected = true;
      }
    },
    setReconnectCountdown(state, action: PayloadAction<number | null>) {
      state.reconnectCountdown = action.payload;
    },
    setIdleDisconnected(state, action: PayloadAction<boolean>) {
      state.isIdleDisconnected = action.payload;
    },
  },
});

export const { setConnectionState, setReconnectCountdown, setIdleDisconnected } =
  websocketSlice.actions;

export const selectConnectionState = (state: RootState) =>
  state.websocket.connectionState;
export const selectReconnectCountdown = (state: RootState) =>
  state.websocket.reconnectCountdown;
export const selectIsOnline = (state: RootState) =>
  state.websocket.connectionState === "online";
export const selectIsIdleDisconnected = (state: RootState) =>
  state.websocket.isIdleDisconnected;
export const selectHasEverConnected = (state: RootState) =>
  state.websocket.hasEverConnected;

export const websocketReducer = websocketSlice.reducer;
