import { useCallback, useEffect, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, Download, MessageCircle, RefreshCw, Reply, User } from "lucide-react";
import { toast } from "react-toastify";
import { Button } from "@/components/ui/button";
import { CommentInput } from "./CommentInput";
import { postComment } from "@/api/review";
import type { TimelineEntry } from "@/api/review";

function formatState(state: string): string {
  return state
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleString();
}

function StateChangeDot({ state }: { state: string | null }) {
  const colorMap: Record<string, string> = {
    in_review: "bg-amber-400",
    accepted: "bg-green-500",
    rejected: "bg-orange-500",
    dropped: "bg-gray-400",
  };
  return (
    <div
      className={`w-2 h-2 mt-2 rounded-full shrink-0 ${colorMap[state ?? ""] ?? "bg-muted-foreground"}`}
    />
  );
}

function StateChangeEntry({ entry }: { entry: TimelineEntry }) {
  return (
    <div className="flex items-start gap-3">
      <StateChangeDot state={entry.new_state} />
      <div>
        <p className="text-sm text-muted-foreground italic">
          {entry.content ||
            `${formatState(entry.old_state || "")} → ${formatState(entry.new_state || "")}`}
        </p>
        {entry.author && (
          <span className="text-xs text-muted-foreground">
            by {entry.author.display_name}
          </span>
        )}
        <time className="block text-xs text-muted-foreground">
          {formatTime(entry.created_at)}
        </time>
      </div>
    </div>
  );
}

interface CommentEntryProps {
  entry: TimelineEntry;
  onReply: (entryId: string) => void;
}

function CommentEntry({ entry, onReply }: CommentEntryProps) {
  return (
    <div className="flex items-start gap-3">
      <div className="w-2 h-2 mt-2 rounded-full bg-sky-400 shrink-0" />
      <div className="flex-1 rounded border bg-card p-3">
        <div className="flex items-center gap-2 mb-1">
          <User className="h-3 w-3 text-muted-foreground" />
          <span className="text-sm font-medium">
            {entry.author?.display_name ?? "System"}
          </span>
          <time className="text-xs text-muted-foreground">
            {formatTime(entry.created_at)}
          </time>
        </div>
        <p className="text-sm">{entry.content}</p>
        <button
          className="flex items-center gap-1 mt-2 text-xs text-muted-foreground hover:text-foreground"
          onClick={() => onReply(entry.id)}
          data-testid={`reply-button-${entry.id}`}
        >
          <Reply className="h-3 w-3" />
          Reply
        </button>
      </div>
    </div>
  );
}

function ResubmissionEntry({ entry }: { entry: TimelineEntry }) {
  return (
    <div className="flex items-start gap-3">
      <div className="w-2 h-2 mt-2 rounded-full bg-primary shrink-0" />
      <div>
        <div className="flex items-center gap-2 text-sm">
          <RefreshCw className="h-3 w-3 text-muted-foreground" />
          <span>Resubmitted</span>
          {entry.old_version_id && entry.new_version_id && (
            <span className="text-muted-foreground flex items-center gap-1">
              <Button variant="ghost" size="sm" className="h-6 px-2 text-xs" data-testid="download-old-version">
                <Download className="h-3 w-3 mr-1" />
                v{entry.old_version_id.slice(0, 4)}
              </Button>
              <ArrowRight className="h-3 w-3" />
              <Button variant="ghost" size="sm" className="h-6 px-2 text-xs" data-testid="download-new-version">
                <Download className="h-3 w-3 mr-1" />
                v{entry.new_version_id.slice(0, 4)}
              </Button>
            </span>
          )}
        </div>
        {entry.author && (
          <span className="text-xs text-muted-foreground">
            by {entry.author.display_name}
          </span>
        )}
        <time className="block text-xs text-muted-foreground">
          {formatTime(entry.created_at)}
        </time>
      </div>
    </div>
  );
}

interface TimelineEntryItemProps {
  entry: TimelineEntry;
  onReply: (entryId: string) => void;
  replyingTo: string | null;
  onSubmitReply: (content: string, parentEntryId: string) => void;
  isReplyPending: boolean;
  onCancelReply: () => void;
}

function TimelineEntryItem({
  entry,
  onReply,
  replyingTo,
  onSubmitReply,
  isReplyPending,
  onCancelReply,
}: TimelineEntryItemProps) {
  const isNested = !!entry.parent_entry_id;
  const style = isNested ? { marginLeft: 24 } : undefined;

  return (
    <div style={style} data-testid={`timeline-entry-${entry.entry_type}`}>
      {entry.entry_type === "state_change" && <StateChangeEntry entry={entry} />}
      {entry.entry_type === "comment" && <CommentEntry entry={entry} onReply={onReply} />}
      {entry.entry_type === "resubmission" && <ResubmissionEntry entry={entry} />}
      {replyingTo === entry.id && (
        <div className="mt-2 ml-5" data-testid={`reply-input-${entry.id}`}>
          <CommentInput
            onSubmit={(content) => onSubmitReply(content, entry.id)}
            isPending={isReplyPending}
            placeholder="Write a reply..."
            autoFocus
            onCancel={onCancelReply}
          />
        </div>
      )}
    </div>
  );
}

interface ReviewTimelineProps {
  entries: TimelineEntry[];
  ideaId?: string;
}

export function ReviewTimeline({ entries, ideaId }: ReviewTimelineProps) {
  const queryClient = useQueryClient();
  const [replyingTo, setReplyingTo] = useState<string | null>(null);

  const commentMutation = useMutation({
    mutationFn: (data: { content: string; parent_entry_id?: string }) => {
      if (!ideaId) throw new Error("No idea ID");
      return postComment(ideaId, data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["timeline", ideaId] });
      setReplyingTo(null);
    },
    onError: (error: Error) => {
      toast.error(
        <div className="flex items-center justify-between gap-4">
          <span>{error.message || "Failed to post comment"}</span>
        </div>,
      );
    },
  });

  const handleReply = useCallback((entryId: string) => {
    setReplyingTo(entryId);
  }, []);

  const handleSubmitReply = useCallback(
    (content: string, parentEntryId: string) => {
      commentMutation.mutate({ content, parent_entry_id: parentEntryId });
    },
    [commentMutation],
  );

  const handleSubmitTopLevel = useCallback(
    (content: string) => {
      commentMutation.mutate({ content });
    },
    [commentMutation],
  );

  const handleCancelReply = useCallback(() => {
    setReplyingTo(null);
  }, []);

  // Listen for WebSocket timeline_update events to invalidate cache
  useEffect(() => {
    if (!ideaId) return;
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail?.idea_id === ideaId) {
        queryClient.invalidateQueries({ queryKey: ["timeline", ideaId] });
      }
    };
    window.addEventListener("ws:timeline_update", handler);
    return () => window.removeEventListener("ws:timeline_update", handler);
  }, [ideaId, queryClient]);

  if (entries.length === 0 && !ideaId) {
    return (
      <div className="flex items-center justify-center py-8 text-sm text-muted-foreground" data-testid="timeline-empty">
        <MessageCircle className="h-4 w-4 mr-2" />
        No timeline entries yet
      </div>
    );
  }

  return (
    <div data-testid="review-timeline">
      {entries.length === 0 ? (
        <div className="flex items-center justify-center py-8 text-sm text-muted-foreground" data-testid="timeline-empty">
          <MessageCircle className="h-4 w-4 mr-2" />
          No timeline entries yet
        </div>
      ) : (
        <div className="relative pl-4 border-l-2 border-border space-y-4">
          {entries.map((entry) => (
            <TimelineEntryItem
              key={entry.id}
              entry={entry}
              onReply={handleReply}
              replyingTo={replyingTo}
              onSubmitReply={handleSubmitReply}
              isReplyPending={commentMutation.isPending}
              onCancelReply={handleCancelReply}
            />
          ))}
        </div>
      )}

      {/* Top-level comment input */}
      {ideaId && (
        <div className="mt-4" data-testid="top-level-comment-input">
          <CommentInput
            onSubmit={handleSubmitTopLevel}
            isPending={commentMutation.isPending && replyingTo === null}
          />
        </div>
      )}
    </div>
  );
}
