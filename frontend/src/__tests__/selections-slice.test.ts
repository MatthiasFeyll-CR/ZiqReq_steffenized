import { describe, it, expect } from "vitest";
import {
  selectionsReducer,
  updateSelection,
  removeUserSelections,
  clearIdeaSelections,
  selectIdeaSelections,
  selectNodeSelection,
  getUserColor,
} from "@/store/selections-slice";
import type { RootState } from "@/store/index";

const initialState = { byIdea: {} };

describe("T-3.5.01: Selections slice state management", () => {
  it("adds a user selection for a node", () => {
    const state = selectionsReducer(
      initialState,
      updateSelection({
        idea_id: "idea-1",
        user_id: "u1",
        display_name: "Alice",
        node_id: "node-1",
      }),
    );
    expect(state.byIdea["idea-1"]).toHaveLength(1);
    expect(state.byIdea["idea-1"]![0]).toEqual({
      user_id: "u1",
      display_name: "Alice",
      node_id: "node-1",
    });
  });

  it("updates an existing user's selected node", () => {
    let state = selectionsReducer(
      initialState,
      updateSelection({
        idea_id: "idea-1",
        user_id: "u1",
        display_name: "Alice",
        node_id: "node-1",
      }),
    );
    state = selectionsReducer(
      state,
      updateSelection({
        idea_id: "idea-1",
        user_id: "u1",
        display_name: "Alice",
        node_id: "node-2",
      }),
    );
    expect(state.byIdea["idea-1"]).toHaveLength(1);
    expect(state.byIdea["idea-1"]![0]!.node_id).toBe("node-2");
  });

  it("removes user selection on null node_id (deselection)", () => {
    let state = selectionsReducer(
      initialState,
      updateSelection({
        idea_id: "idea-1",
        user_id: "u1",
        display_name: "Alice",
        node_id: "node-1",
      }),
    );
    state = selectionsReducer(
      state,
      updateSelection({
        idea_id: "idea-1",
        user_id: "u1",
        display_name: "Alice",
        node_id: null,
      }),
    );
    expect(state.byIdea["idea-1"]).toHaveLength(0);
  });

  it("handles multiple users selecting different nodes", () => {
    let state = selectionsReducer(
      initialState,
      updateSelection({
        idea_id: "idea-1",
        user_id: "u1",
        display_name: "Alice",
        node_id: "node-1",
      }),
    );
    state = selectionsReducer(
      state,
      updateSelection({
        idea_id: "idea-1",
        user_id: "u2",
        display_name: "Bob",
        node_id: "node-2",
      }),
    );
    expect(state.byIdea["idea-1"]).toHaveLength(2);
  });

  it("removeUserSelections removes a specific user", () => {
    let state = selectionsReducer(
      initialState,
      updateSelection({
        idea_id: "idea-1",
        user_id: "u1",
        display_name: "Alice",
        node_id: "node-1",
      }),
    );
    state = selectionsReducer(
      state,
      removeUserSelections({ idea_id: "idea-1", user_id: "u1" }),
    );
    expect(state.byIdea["idea-1"]).toHaveLength(0);
  });

  it("clearIdeaSelections removes all selections for an idea", () => {
    let state = selectionsReducer(
      initialState,
      updateSelection({
        idea_id: "idea-1",
        user_id: "u1",
        display_name: "Alice",
        node_id: "node-1",
      }),
    );
    state = selectionsReducer(state, clearIdeaSelections("idea-1"));
    expect(state.byIdea["idea-1"]).toBeUndefined();
  });
});

describe("T-3.5.02: Selections selectors", () => {
  it("selectIdeaSelections returns selections for given idea", () => {
    const rootState = {
      selections: {
        byIdea: {
          "idea-1": [
            { user_id: "u1", display_name: "Alice", node_id: "node-1" },
          ],
        },
      },
    } as unknown as RootState;
    expect(selectIdeaSelections("idea-1")(rootState)).toHaveLength(1);
  });

  it("selectIdeaSelections returns empty array for unknown idea", () => {
    const rootState = {
      selections: { byIdea: {} },
    } as unknown as RootState;
    expect(selectIdeaSelections("unknown")(rootState)).toEqual([]);
  });

  it("selectNodeSelection returns the user who selected a specific node", () => {
    const rootState = {
      selections: {
        byIdea: {
          "idea-1": [
            { user_id: "u1", display_name: "Alice", node_id: "node-1" },
            { user_id: "u2", display_name: "Bob", node_id: "node-2" },
          ],
        },
      },
    } as unknown as RootState;
    const result = selectNodeSelection("idea-1", "node-1")(rootState);
    expect(result).toEqual({
      user_id: "u1",
      display_name: "Alice",
      node_id: "node-1",
    });
  });

  it("selectNodeSelection returns null when no user selected the node", () => {
    const rootState = {
      selections: {
        byIdea: {
          "idea-1": [
            { user_id: "u1", display_name: "Alice", node_id: "node-1" },
          ],
        },
      },
    } as unknown as RootState;
    expect(selectNodeSelection("idea-1", "node-99")(rootState)).toBeNull();
  });
});

describe("T-3.5.03: getUserColor deterministic color assignment", () => {
  it("returns the same color for the same user ID", () => {
    const color1 = getUserColor("user-abc-123");
    const color2 = getUserColor("user-abc-123");
    expect(color1).toBe(color2);
  });

  it("returns a valid hex color", () => {
    const color = getUserColor("some-user-id");
    expect(color).toMatch(/^#[0-9a-f]{6}$/);
  });

  it("returns different colors for different users (with high probability)", () => {
    const colors = new Set([
      getUserColor("user-1"),
      getUserColor("user-2"),
      getUserColor("user-3"),
      getUserColor("user-4"),
    ]);
    // At least 2 different colors out of 4 users
    expect(colors.size).toBeGreaterThanOrEqual(2);
  });
});
