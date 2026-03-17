import { describe, it, expect } from "vitest";
import {
  presenceReducer,
  updatePresence,
  clearProjectPresence,
  selectProjectPresence,
} from "@/store/presence-slice";
import type { RootState } from "@/store/index";

const initialState = { byProject: {} };

describe("T-6.3.01: Presence slice state management", () => {
  it("adds a user to presence list on online update", () => {
    const state = presenceReducer(
      initialState,
      updatePresence({
        project_id: "proj-1",
        user: { id: "u1", display_name: "Alice" },
        state: "online",
      }),
    );
    expect(state.byProject["proj-1"]).toHaveLength(1);
    expect(state.byProject["proj-1"]![0]).toEqual({
      user_id: "u1",
      display_name: "Alice",
      state: "online",
    });
  });

  it("removes user from presence list on offline update", () => {
    let state = presenceReducer(
      initialState,
      updatePresence({
        project_id: "proj-1",
        user: { id: "u1", display_name: "Alice" },
        state: "online",
      }),
    );
    state = presenceReducer(
      state,
      updatePresence({
        project_id: "proj-1",
        user: { id: "u1", display_name: "Alice" },
        state: "offline",
      }),
    );
    expect(state.byProject["proj-1"]).toHaveLength(0);
  });

  it("updates existing user state from online to idle", () => {
    let state = presenceReducer(
      initialState,
      updatePresence({
        project_id: "proj-1",
        user: { id: "u1", display_name: "Alice" },
        state: "online",
      }),
    );
    state = presenceReducer(
      state,
      updatePresence({
        project_id: "proj-1",
        user: { id: "u1", display_name: "Alice" },
        state: "idle",
      }),
    );
    expect(state.byProject["proj-1"]).toHaveLength(1);
    expect(state.byProject["proj-1"]![0]!.state).toBe("idle");
  });

  it("handles multiple users on same project", () => {
    let state = presenceReducer(
      initialState,
      updatePresence({
        project_id: "proj-1",
        user: { id: "u1", display_name: "Alice" },
        state: "online",
      }),
    );
    state = presenceReducer(
      state,
      updatePresence({
        project_id: "proj-1",
        user: { id: "u2", display_name: "Bob" },
        state: "online",
      }),
    );
    expect(state.byProject["proj-1"]).toHaveLength(2);
  });

  it("clearProjectPresence removes all users for a project", () => {
    let state = presenceReducer(
      initialState,
      updatePresence({
        project_id: "proj-1",
        user: { id: "u1", display_name: "Alice" },
        state: "online",
      }),
    );
    state = presenceReducer(state, clearProjectPresence("proj-1"));
    expect(state.byProject["proj-1"]).toBeUndefined();
  });
});

describe("T-6.3.02: Presence selectors", () => {
  it("selectProjectPresence returns users for given project", () => {
    const rootState = {
      presence: {
        byProject: {
          "proj-1": [
            { user_id: "u1", display_name: "Alice", state: "online" as const },
          ],
        },
      },
    } as unknown as RootState;
    expect(selectProjectPresence("proj-1")(rootState)).toHaveLength(1);
  });

  it("selectProjectPresence returns empty array for unknown project", () => {
    const rootState = {
      presence: { byProject: {} },
    } as unknown as RootState;
    expect(selectProjectPresence("unknown")(rootState)).toEqual([]);
  });
});
