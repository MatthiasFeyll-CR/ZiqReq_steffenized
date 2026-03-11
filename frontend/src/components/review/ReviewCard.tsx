import { useNavigate } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { formatRelativeTime } from "@/lib/utils";
import type { ReviewIdea } from "@/api/review";

const STATE_DOT_COLORS: Record<string, string> = {
  open: "#0284C7",
  in_review: "#F59E0B",
  accepted: "#16A34A",
  dropped: "#9CA3AF",
  rejected: "#F97316",
};

const STATE_LABELS: Record<string, string> = {
  open: "Open",
  in_review: "In Review",
  accepted: "Accepted",
  dropped: "Dropped",
  rejected: "Rejected",
};

export interface ReviewCardProps {
  idea: ReviewIdea;
  category: "assigned" | "unassigned" | "accepted" | "rejected" | "dropped";
}

export function ReviewCard({ idea }: ReviewCardProps) {
  const navigate = useNavigate();

  return (
    <button
      type="button"
      className="flex w-full cursor-pointer items-center gap-3 rounded-lg border border-border bg-surface p-4 text-left transition-colors hover:bg-muted"
      onClick={() => navigate(`/idea/${idea.id}`)}
    >
      <span
        className="shrink-0 rounded-full"
        style={{
          width: 8,
          height: 8,
          backgroundColor: STATE_DOT_COLORS[idea.state] ?? "#9CA3AF",
        }}
        aria-label={STATE_LABELS[idea.state] ?? idea.state}
      />

      <div className="min-w-0 flex-1">
        <p className="truncate text-base font-medium text-foreground">
          {idea.title || "Untitled idea"}
        </p>
        <p className="text-sm text-text-secondary">
          by {idea.owner_name} &bull; Submitted {formatRelativeTime(idea.submitted_at)}
        </p>
      </div>

      <Badge variant={idea.state as "open" | "in_review" | "accepted" | "dropped" | "rejected"} className="shrink-0">
        {STATE_LABELS[idea.state] ?? idea.state}
      </Badge>
    </button>
  );
}
