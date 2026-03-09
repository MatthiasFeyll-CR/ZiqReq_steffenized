import { configureStore } from "@reduxjs/toolkit";
import { boardReducer } from "./board-slice";
import { websocketReducer } from "./websocket-slice";
import { presenceReducer } from "./presence-slice";
import { uiReducer } from "./ui-slice";
import { rateLimitReducer } from "./rate-limit-slice";

export const store = configureStore({
  reducer: {
    board: boardReducer,
    websocket: websocketReducer,
    presence: presenceReducer,
    ui: uiReducer,
    rateLimit: rateLimitReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
