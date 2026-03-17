import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { RootState } from "./index";

export type PresenceState = "online" | "idle" | "offline";

export interface PresenceUser {
  user_id: string;
  display_name: string;
  state: PresenceState;
}

interface PresenceSliceState {
  /** Presence list per project_id */
  byProject: Record<string, PresenceUser[]>;
}

const initialState: PresenceSliceState = {
  byProject: {},
};

const presenceSlice = createSlice({
  name: "presence",
  initialState,
  reducers: {
    updatePresence(
      state,
      action: PayloadAction<{
        project_id: string;
        user: { id: string; display_name: string };
        state: PresenceState;
      }>,
    ) {
      const { project_id, user, state: presenceState } = action.payload;
      if (!state.byProject[project_id]) {
        state.byProject[project_id] = [];
      }
      const list = state.byProject[project_id]!;
      const idx = list.findIndex((u) => u.user_id === user.id);

      if (presenceState === "offline") {
        if (idx !== -1) {
          list.splice(idx, 1);
        }
      } else if (idx !== -1) {
        const entry = list[idx]!;
        entry.state = presenceState;
        entry.display_name = user.display_name;
      } else {
        list.push({
          user_id: user.id,
          display_name: user.display_name,
          state: presenceState,
        });
      }
    },
    clearProjectPresence(state, action: PayloadAction<string>) {
      delete state.byProject[action.payload];
    },
  },
});

export const { updatePresence, clearProjectPresence } = presenceSlice.actions;

export const selectProjectPresence = (projectId: string) => (state: RootState) =>
  state.presence.byProject[projectId] ?? [];

export const presenceReducer = presenceSlice.reducer;
