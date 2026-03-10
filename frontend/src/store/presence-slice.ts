import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { RootState } from "./index";

export type PresenceState = "online" | "idle" | "offline";

export interface PresenceUser {
  user_id: string;
  display_name: string;
  state: PresenceState;
}

interface PresenceSliceState {
  /** Presence list per idea_id */
  byIdea: Record<string, PresenceUser[]>;
}

const initialState: PresenceSliceState = {
  byIdea: {},
};

const presenceSlice = createSlice({
  name: "presence",
  initialState,
  reducers: {
    updatePresence(
      state,
      action: PayloadAction<{
        idea_id: string;
        user: { id: string; display_name: string };
        state: PresenceState;
      }>,
    ) {
      const { idea_id, user, state: presenceState } = action.payload;
      if (!state.byIdea[idea_id]) {
        state.byIdea[idea_id] = [];
      }
      const list = state.byIdea[idea_id]!;
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
    clearIdeaPresence(state, action: PayloadAction<string>) {
      delete state.byIdea[action.payload];
    },
  },
});

export const { updatePresence, clearIdeaPresence } = presenceSlice.actions;

export const selectIdeaPresence = (ideaId: string) => (state: RootState) =>
  state.presence.byIdea[ideaId] ?? [];

export const presenceReducer = presenceSlice.reducer;
