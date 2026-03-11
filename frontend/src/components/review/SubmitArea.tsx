import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Loader2 } from "lucide-react";
import { toast } from "react-toastify";
import { Button } from "@/components/ui/button";
import { submitIdea } from "@/api/ideas";
import { fetchReviewerUsers, type ReviewerUser } from "@/api/review";

interface SubmitAreaProps {
  ideaId: string;
  ideaState: string;
  onSubmitted?: () => void;
}

export function SubmitArea({ ideaId, ideaState, onSubmitted }: SubmitAreaProps) {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const [message, setMessage] = useState("");
  const [selectedReviewerIds, setSelectedReviewerIds] = useState<string[]>([]);

  const { data: reviewerUsers = [] } = useQuery({
    queryKey: ["reviewer-users"],
    queryFn: fetchReviewerUsers,
  });

  const submitMutation = useMutation({
    mutationFn: () =>
      submitIdea(ideaId, {
        message: message || undefined,
        reviewer_ids: selectedReviewerIds.length > 0 ? selectedReviewerIds : undefined,
      }),
    onSuccess: () => {
      toast.success(t("submit.success", "Idea submitted"));
      queryClient.invalidateQueries({ queryKey: ["brd", ideaId] });
      queryClient.invalidateQueries({ queryKey: ["idea", ideaId] });
      queryClient.invalidateQueries({ queryKey: ["timeline", ideaId] });
      setMessage("");
      setSelectedReviewerIds([]);
      onSubmitted?.();
    },
    onError: (error: Error) => {
      toast.error(
        <div className="flex items-center justify-between gap-4">
          <span>{error.message || t("submit.error", "Failed to submit idea")}</span>
          <button
            className="shrink-0 font-medium text-primary underline"
            onClick={() => submitMutation.mutate()}
          >
            {t("common.retry", "Retry")}
          </button>
        </div>,
      );
    },
  });

  // Only show for open or rejected states
  if (ideaState !== "open" && ideaState !== "rejected") {
    return null;
  }

  const handleToggleReviewer = (reviewerId: string) => {
    setSelectedReviewerIds((prev) =>
      prev.includes(reviewerId)
        ? prev.filter((id) => id !== reviewerId)
        : [...prev, reviewerId],
    );
  };

  return (
    <div className="border-t pt-4 mt-4 space-y-4" data-testid="submit-area">
      <div>
        <label className="block text-sm font-medium text-foreground mb-1">
          {t("submit.messageLabel", "Message for reviewers (optional)")}
        </label>
        <textarea
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 resize-y min-h-[80px]"
          placeholder={t("submit.messagePlaceholder", "Add a message for the reviewers...")}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          disabled={submitMutation.isPending}
          data-testid="submit-message"
        />
      </div>

      {reviewerUsers.length > 0 && (
        <div>
          <label className="block text-sm font-medium text-foreground mb-1">
            {t("submit.reviewerLabel", "Assign reviewers (optional)")}
          </label>
          <div
            className="border rounded-md p-2 max-h-[160px] overflow-y-auto space-y-1"
            data-testid="reviewer-selector"
          >
            {reviewerUsers.map((reviewer: ReviewerUser) => (
              <label
                key={reviewer.id}
                className="flex items-center gap-2 px-2 py-1 rounded hover:bg-accent cursor-pointer text-sm"
              >
                <input
                  type="checkbox"
                  checked={selectedReviewerIds.includes(reviewer.id)}
                  onChange={() => handleToggleReviewer(reviewer.id)}
                  disabled={submitMutation.isPending}
                  className="rounded border-input"
                />
                <span>{reviewer.display_name}</span>
                <span className="text-muted-foreground text-xs">({reviewer.email})</span>
              </label>
            ))}
          </div>
        </div>
      )}

      <div className="flex justify-end">
        <Button
          variant="primary"
          onClick={() => submitMutation.mutate()}
          disabled={submitMutation.isPending}
          data-testid="submit-button"
        >
          {submitMutation.isPending && (
            <Loader2 className="h-4 w-4 mr-2 motion-safe:animate-spin" />
          )}
          {t("submit.button", "Submit for Review")}
        </Button>
      </div>
    </div>
  );
}
