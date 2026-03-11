import { useQuery } from "@tanstack/react-query";
import { FileText, Users } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ReviewTimeline } from "./ReviewTimeline";
import { fetchTimeline, fetchIdeaReviewers } from "@/api/review";
import type { Idea } from "@/api/ideas";

interface ReviewSectionProps {
  ideaId: string;
  idea: Idea;
}

const STATE_LABELS: Record<string, string> = {
  open: "Open",
  in_review: "In Review",
  accepted: "Accepted",
  dropped: "Dropped",
  rejected: "Rejected",
};

export function ReviewSection({ ideaId, idea }: ReviewSectionProps) {
  const {
    data: timelineEntries,
    isLoading: isTimelineLoading,
  } = useQuery({
    queryKey: ["timeline", ideaId],
    queryFn: () => fetchTimeline(ideaId),
  });

  const {
    data: reviewerData,
    isLoading: isReviewersLoading,
  } = useQuery({
    queryKey: ["reviewers", ideaId],
    queryFn: () => fetchIdeaReviewers(ideaId),
  });

  const reviewers = reviewerData?.reviewers ?? [];

  return (
    <div className="border-t bg-background p-6" data-testid="review-section">
      {/* Header area: PDF thumbnail, title, reviewers, state badge */}
      <div className="flex items-start gap-4 mb-6" data-testid="review-section-header">
        {/* PDF preview thumbnail */}
        <div className="w-16 h-20 bg-muted border rounded flex items-center justify-center shrink-0">
          <FileText className="h-8 w-8 text-muted-foreground" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-lg font-semibold truncate">{idea.title}</h2>
            <Badge
              variant={idea.state as "open" | "in_review" | "accepted" | "dropped" | "rejected"}
              className="shrink-0"
            >
              {STATE_LABELS[idea.state] || idea.state}
            </Badge>
          </div>

          {/* Assigned reviewers */}
          {isReviewersLoading ? (
            <Skeleton className="h-4 w-32" />
          ) : reviewers.length > 0 ? (
            <div className="flex items-center gap-1 text-sm text-muted-foreground" data-testid="reviewer-list">
              <Users className="h-3 w-3" />
              <span>
                {reviewers.map((r) => r.display_name).join(", ")}
              </span>
            </div>
          ) : (
            <div className="text-sm text-muted-foreground" data-testid="no-reviewers">
              No reviewers assigned
            </div>
          )}
        </div>
      </div>

      {/* Timeline */}
      <div className="mt-4">
        <h3 className="text-sm font-medium text-muted-foreground mb-3">Timeline</h3>
        {isTimelineLoading ? (
          <div className="space-y-3">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-3/4" />
          </div>
        ) : (
          <ReviewTimeline entries={timelineEntries ?? []} ideaId={ideaId} />
        )}
      </div>
    </div>
  );
}
