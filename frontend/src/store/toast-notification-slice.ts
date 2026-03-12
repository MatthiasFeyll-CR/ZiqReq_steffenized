import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

export interface ToastNotification {
  id: string;
  event_type: string;
  title: string;
  body: string;
  reference_id?: string;
  reference_type?: string;
  created_at: string;
}

interface ToastNotificationState {
  items: ToastNotification[];
}

const initialState: ToastNotificationState = {
  items: [],
};

const toastNotificationSlice = createSlice({
  name: "toastNotifications",
  initialState,
  reducers: {
    addToastNotification(state, action: PayloadAction<ToastNotification>) {
      state.items.unshift(action.payload);
    },
    dismissToastNotification(state, action: PayloadAction<string>) {
      state.items = state.items.filter((n) => n.id !== action.payload);
    },
    clearAllToastNotifications(state) {
      state.items = [];
    },
  },
});

export const {
  addToastNotification,
  dismissToastNotification,
  clearAllToastNotifications,
} = toastNotificationSlice.actions;

export const toastNotificationReducer = toastNotificationSlice.reducer;
