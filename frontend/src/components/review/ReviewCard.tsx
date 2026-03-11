import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Loader2 } from "lucide-react";
import { toast } from "react-toastify";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { formatRelativeTime } from "@/lib/utils";
import { useAuth } from "@/hooks/use-auth";
import { assignReview, unassignReview } from "@/api/review";
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

export function ReviewCard({ idea, category }: ReviewCardProps) {
  const navigate = useNavigate();
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const isConflictOfInterest =
    !!user &&
    (user.id === idea.owner_id || user.id === idea.co_owner_id);

  const assignMutation = useMutation({
    mutationFn: () => assignReview(idea.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reviews"] });
    },
    onError: (error: Error) => {
      toast.error(
        <div className="flex items-center justify-between gap-4">
          <span>{error.message || "Failed to assign"}</span>
          <button
            className="shrink-0 font-medium text-primary underline"
            onClick={() => assignMutation.mutate()}
          >
            Retry
          </button>
        </div>,
      );
    },
  });

  const unassignMutation = useMutation({
    mutationFn: () => unassignReview(idea.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reviews"] });
    },
    onError: (error: Error) => {
      toast.error(
        <div className="flex items-center justify-between gap-4">
          <span>{error.message || "Failed to unassign"}</span>
          <button
            className="shrink-0 font-medium text-primary underline"
            onClick={() => unassignMutation.mutate()}
          >
            Retry
          </button>
        </div>,
      );
    },
  });

  const handleActionClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (category === "unassigned") {
      assignMutation.mutate();
    } else if (category === "assigned") {
      unassignMutation.mutate();
    }
  };

  const isLoading = assignMutation.isPending || unassignMutation.isPending;
  const showActionButton = category === "assigned" || category === "unassigned";

  return (
    <div
      role="button"
      tabIndex={0}
      className="flex w-full cursor-pointer items-center gap-3 rounded-lg border border-border bg-surface p-4 text-left transition-colors hover:bg-muted"
      onClick={() => navigate(`/idea/${idea.id}`)}
      onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") navigate(`/idea/${idea.id}`); }}
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

      {showActionButton && (
        category === "unassigned" && isConflictOfInterest ? (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <span>
                  <Button
                    variant="primary"
                    size="sm"
                    disabled
                    data-testid="assign-button"
                    onClick={handleActionClick}
                  >
                    Assign
                  </Button>
                </span>
              </TooltipTrigger>
              <TooltipContent>Cannot review own idea</TooltipContent>
            </Tooltip>
          </TooltipProvider>
        ) : (
          <Button
            variant={category === "assigned" ? "secondary" : "primary"}
            size="sm"
            disabled={isLoading}
            data-testid={category === "assigned" ? "unassign-button" : "assign-button"}
            onClick={handleActionClick}
          >
            {isLoading && <Loader2 className="mr-1 h-3 w-3 animate-spin" />}
            {category === "assigned" ? "Unassign" : "Assign"}
          </Button>
        )
      )}
    </div>
  );
}
