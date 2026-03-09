import { useMemo } from "react";
import type { Idea } from "@/api/ideas";

export interface SectionVisibility {
  /** Whether the review tab should be shown */
  reviewVisible: boolean;
  /** Whether the chat panel is locked (read-only overlay) */
  chatLocked: boolean;
  /** Whether everything is read-only (accepted/dropped terminal states) */
  allReadOnly: boolean;
  /** Lock reason text for the overlay */
  lockReason: string | null;
}

/**
 * Derives section visibility and locking from idea.state.
 *
 * M3 heuristic: has_been_submitted = idea.state !== "open"
 * (If state is anything other than "open", the idea was submitted at least once.)
 */
export function useSectionVisibility(idea: Idea): SectionVisibility {
  return useMemo(() => {
    const { state } = idea;
    const hasBenSubmitted = state !== "open";

    switch (state) {
      case "open":
        return {
          reviewVisible: false,
          chatLocked: false,
          allReadOnly: false,
          lockReason: null,
        };
      case "in_review":
        return {
          reviewVisible: true,
          chatLocked: true,
          allReadOnly: false,
          lockReason: "Chat is locked while the idea is under review.",
        };
      case "rejected":
        return {
          reviewVisible: hasBenSubmitted,
          chatLocked: false,
          allReadOnly: false,
          lockReason: null,
        };
      case "accepted":
        return {
          reviewVisible: hasBenSubmitted,
          chatLocked: true,
          allReadOnly: true,
          lockReason: "This idea has been accepted. All sections are read-only.",
        };
      case "dropped":
        return {
          reviewVisible: hasBenSubmitted,
          chatLocked: true,
          allReadOnly: true,
          lockReason: "This idea has been dropped. All sections are read-only.",
        };
      default:
        return {
          reviewVisible: false,
          chatLocked: false,
          allReadOnly: false,
          lockReason: null,
        };
    }
  }, [idea]);
}
