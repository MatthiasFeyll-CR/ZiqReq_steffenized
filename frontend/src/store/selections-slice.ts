import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { RootState } from "./index";

export interface UserSelection {
  user_id: string;
  display_name: string;
  node_id: string | null;
}

interface SelectionsState {
  /** Selections per idea_id */
  byIdea: Record<string, UserSelection[]>;
}

const initialState: SelectionsState = {
  byIdea: {},
};

const SELECTION_COLORS = [
  "#3b82f6", // blue
  "#ef4444", // red
  "#10b981", // emerald
  "#f59e0b", // amber
  "#8b5cf6", // violet
  "#ec4899", // pink
  "#06b6d4", // cyan
  "#f97316", // orange
];

/** Deterministic color for a user based on their ID */
export function getUserColor(userId: string): string {
  let hash = 0;
  for (let i = 0; i < userId.length; i++) {
    hash = (hash * 31 + userId.charCodeAt(i)) | 0;
  }
  return SELECTION_COLORS[Math.abs(hash) % SELECTION_COLORS.length]!;
}

const selectionsSlice = createSlice({
  name: "selections",
  initialState,
  reducers: {
    updateSelection(
      state,
      action: PayloadAction<{
        idea_id: string;
        user_id: string;
        display_name: string;
        node_id: string | null;
      }>,
    ) {
      const { idea_id, user_id, display_name, node_id } = action.payload;
      if (!state.byIdea[idea_id]) {
        state.byIdea[idea_id] = [];
      }
      const list = state.byIdea[idea_id]!;
      const idx = list.findIndex((u) => u.user_id === user_id);

      if (node_id === null) {
        // Deselection — remove user from list
        if (idx !== -1) {
          list.splice(idx, 1);
        }
      } else if (idx !== -1) {
        list[idx]!.node_id = node_id;
        list[idx]!.display_name = display_name;
      } else {
        list.push({ user_id, display_name, node_id });
      }
    },
    removeUserSelections(
      state,
      action: PayloadAction<{ idea_id: string; user_id: string }>,
    ) {
      const { idea_id, user_id } = action.payload;
      const list = state.byIdea[idea_id];
      if (list) {
        const idx = list.findIndex((u) => u.user_id === user_id);
        if (idx !== -1) list.splice(idx, 1);
      }
    },
    clearIdeaSelections(state, action: PayloadAction<string>) {
      delete state.byIdea[action.payload];
    },
  },
});

export const { updateSelection, removeUserSelections, clearIdeaSelections } =
  selectionsSlice.actions;

export const selectIdeaSelections =
  (ideaId: string) => (state: RootState) =>
    state.selections.byIdea[ideaId] ?? [];

/** Get the user who selected a specific node (if any) */
export const selectNodeSelection =
  (ideaId: string, nodeId: string) => (state: RootState) => {
    const list = state.selections.byIdea[ideaId];
    if (!list) return null;
    return list.find((s) => s.node_id === nodeId) ?? null;
  };

export const selectionsReducer = selectionsSlice.reducer;
