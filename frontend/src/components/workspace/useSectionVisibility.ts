import { useMemo } from "react";
import type { Idea } from "@/api/ideas";

export interface SectionVisibility {
  /** Whether the chat panel is locked (read-only overlay) */
  chatLocked: boolean;
  /** Whether everything is read-only (accepted/dropped terminal states) */
  allReadOnly: boolean;
  /** Lock reason text for the overlay */
  lockReason: string | null;
}

/**
 * Derives section visibility and locking from idea.state.
 */
export function useSectionVisibility(idea: Idea): SectionVisibility {
  return useMemo(() => {
    const { state } = idea;

    switch (state) {
      case "open":
        return {
          chatLocked: false,
          allReadOnly: false,
          lockReason: null,
        };
      case "in_review":
        return {
          chatLocked: true,
          allReadOnly: false,
          lockReason: "Chat is locked while the idea is under review.",
        };
      case "rejected":
        return {
          chatLocked: false,
          allReadOnly: false,
          lockReason: null,
        };
      case "accepted":
        return {
          chatLocked: true,
          allReadOnly: true,
          lockReason: "This idea has been accepted. All sections are read-only.",
        };
      case "dropped":
        return {
          chatLocked: true,
          allReadOnly: true,
          lockReason: "This idea has been dropped. All sections are read-only.",
        };
      case "deleted":
        return {
          chatLocked: true,
          allReadOnly: true,
          lockReason: "This idea has been deleted. All sections are read-only.",
        };
      default:
        return {
          chatLocked: false,
          allReadOnly: false,
          lockReason: null,
        };
    }
  }, [idea]);
}
