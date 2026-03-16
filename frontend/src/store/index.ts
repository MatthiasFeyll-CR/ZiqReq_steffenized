import { configureStore } from "@reduxjs/toolkit";
import { websocketReducer } from "./websocket-slice";
import { presenceReducer } from "./presence-slice";
import { uiReducer } from "./ui-slice";
import { rateLimitReducer } from "./rate-limit-slice";
import { toastNotificationReducer } from "./toast-notification-slice";

export const store = configureStore({
  reducer: {
    websocket: websocketReducer,
    presence: presenceReducer,
    ui: uiReducer,
    rateLimit: rateLimitReducer,
    toastNotifications: toastNotificationReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
