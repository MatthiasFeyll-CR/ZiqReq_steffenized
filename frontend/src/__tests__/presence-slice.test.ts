import { describe, it, expect } from "vitest";
import {
  presenceReducer,
  updatePresence,
  clearIdeaPresence,
  selectIdeaPresence,
} from "@/store/presence-slice";
import type { RootState } from "@/store/index";

const initialState = { byIdea: {} };

describe("T-6.3.01: Presence slice state management", () => {
  it("adds a user to presence list on online update", () => {
    const state = presenceReducer(
      initialState,
      updatePresence({
        idea_id: "idea-1",
        user: { id: "u1", display_name: "Alice" },
        state: "online",
      }),
    );
    expect(state.byIdea["idea-1"]).toHaveLength(1);
    expect(state.byIdea["idea-1"]![0]).toEqual({
      user_id: "u1",
      display_name: "Alice",
      state: "online",
    });
  });

  it("removes user from presence list on offline update", () => {
    let state = presenceReducer(
      initialState,
      updatePresence({
        idea_id: "idea-1",
        user: { id: "u1", display_name: "Alice" },
        state: "online",
      }),
    );
    state = presenceReducer(
      state,
      updatePresence({
        idea_id: "idea-1",
        user: { id: "u1", display_name: "Alice" },
        state: "offline",
      }),
    );
    expect(state.byIdea["idea-1"]).toHaveLength(0);
  });

  it("updates existing user state from online to idle", () => {
    let state = presenceReducer(
      initialState,
      updatePresence({
        idea_id: "idea-1",
        user: { id: "u1", display_name: "Alice" },
        state: "online",
      }),
    );
    state = presenceReducer(
      state,
      updatePresence({
        idea_id: "idea-1",
        user: { id: "u1", display_name: "Alice" },
        state: "idle",
      }),
    );
    expect(state.byIdea["idea-1"]).toHaveLength(1);
    expect(state.byIdea["idea-1"]![0]!.state).toBe("idle");
  });

  it("handles multiple users on same idea", () => {
    let state = presenceReducer(
      initialState,
      updatePresence({
        idea_id: "idea-1",
        user: { id: "u1", display_name: "Alice" },
        state: "online",
      }),
    );
    state = presenceReducer(
      state,
      updatePresence({
        idea_id: "idea-1",
        user: { id: "u2", display_name: "Bob" },
        state: "online",
      }),
    );
    expect(state.byIdea["idea-1"]).toHaveLength(2);
  });

  it("clearIdeaPresence removes all users for an idea", () => {
    let state = presenceReducer(
      initialState,
      updatePresence({
        idea_id: "idea-1",
        user: { id: "u1", display_name: "Alice" },
        state: "online",
      }),
    );
    state = presenceReducer(state, clearIdeaPresence("idea-1"));
    expect(state.byIdea["idea-1"]).toBeUndefined();
  });
});

describe("T-6.3.02: Presence selectors", () => {
  it("selectIdeaPresence returns users for given idea", () => {
    const rootState = {
      presence: {
        byIdea: {
          "idea-1": [
            { user_id: "u1", display_name: "Alice", state: "online" as const },
          ],
        },
      },
    } as unknown as RootState;
    expect(selectIdeaPresence("idea-1")(rootState)).toHaveLength(1);
  });

  it("selectIdeaPresence returns empty array for unknown idea", () => {
    const rootState = {
      presence: { byIdea: {} },
    } as unknown as RootState;
    expect(selectIdeaPresence("unknown")(rootState)).toEqual([]);
  });
});
