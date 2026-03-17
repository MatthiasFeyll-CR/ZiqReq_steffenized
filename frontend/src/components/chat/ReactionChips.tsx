import { useState } from "react";
import { toast } from "react-toastify";
import { cn } from "@/lib/utils";
import {
  addReaction,
  removeReaction,
  type ReactionType,
} from "@/api/reactions";

const REACTION_CONFIG: { type: ReactionType; emoji: string }[] = [
  { type: "thumbs_up", emoji: "\uD83D\uDC4D" },
  { type: "thumbs_down", emoji: "\uD83D\uDC4E" },
  { type: "heart", emoji: "\u2764\uFE0F" },
];

interface ReactionState {
  active: ReactionType | null;
  counts: Record<ReactionType, number>;
}

interface ReactionChipsProps {
  projectId: string;
  messageId: string;
  initialActive?: ReactionType | null;
  initialCounts?: Record<ReactionType, number>;
}

export function ReactionChips({
  projectId,
  messageId,
  initialActive = null,
  initialCounts = { thumbs_up: 0, thumbs_down: 0, heart: 0 },
}: ReactionChipsProps) {
  const [state, setState] = useState<ReactionState>({
    active: initialActive,
    counts: { ...initialCounts },
  });
  const [pending, setPending] = useState(false);

  const handleToggle = async (type: ReactionType) => {
    if (pending) return;

    const wasActive = state.active === type;
    const prevState = { ...state, counts: { ...state.counts } };

    // Optimistic update
    setState((prev) => {
      const newCounts = { ...prev.counts };
      if (wasActive) {
        newCounts[type] = Math.max(0, newCounts[type] - 1);
        return { active: null, counts: newCounts };
      }
      // If switching from another reaction, decrement old
      if (prev.active) {
        newCounts[prev.active] = Math.max(0, newCounts[prev.active] - 1);
      }
      newCounts[type] = newCounts[type] + 1;
      return { active: type, counts: newCounts };
    });

    setPending(true);
    try {
      if (wasActive) {
        await removeReaction(projectId, messageId);
      } else {
        // If switching, remove old first
        if (prevState.active) {
          await removeReaction(projectId, messageId);
        }
        await addReaction(projectId, messageId, type);
      }
    } catch (err) {
      // Rollback
      setState(prevState);
      const message =
        err instanceof Error ? err.message : "Failed to update reaction";
      toast.error(message);
    } finally {
      setPending(false);
    }
  };

  return (
    <div
      className="flex gap-1 mt-1 opacity-0 group-hover:opacity-100 transition-opacity"
      data-testid={`reaction-chips-${messageId}`}
    >
      {REACTION_CONFIG.map(({ type, emoji }) => {
        const isActive = state.active === type;
        const count = state.counts[type];
        return (
          <button
            key={type}
            type="button"
            onClick={() => handleToggle(type)}
            disabled={pending}
            className={cn(
              "text-sm px-1.5 py-0.5 rounded-full cursor-pointer transition-colors",
              isActive
                ? "bg-primary/20 border border-primary"
                : "bg-muted hover:bg-muted/80 border border-transparent",
            )}
            data-testid={`reaction-${type}`}
            aria-label={type}
          >
            {emoji}
            {count > 0 && <span className="ml-0.5">{count}</span>}
          </button>
        );
      })}
    </div>
  );
}
