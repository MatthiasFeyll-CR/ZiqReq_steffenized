import { useCallback, useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import {
  fetchComments,
  createComment,
  markCommentsRead,
  type IdeaComment,
} from "@/api/comments";
import { CommentItem } from "./CommentItem";
import { CommentInput } from "./CommentInput";
import { SystemEventItem } from "./SystemEventItem";
import { Skeleton } from "@/components/ui/skeleton";
import { MessageSquareOff } from "lucide-react";

interface CommentsPanelProps {
  ideaId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  disabled?: boolean;
  currentUserId?: string;
  isOwnerOrCollaborator?: boolean;
  shareToken?: string | null;
}

export function CommentsPanel({
  ideaId,
  open,
  onOpenChange,
  disabled = false,
  currentUserId,
  isOwnerOrCollaborator = false,
  shareToken,
}: CommentsPanelProps) {
  const { t } = useTranslation();
  const [comments, setComments] = useState<IdeaComment[]>([]);
  const [loading, setLoading] = useState(true);
  const [replyTo, setReplyTo] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const loadComments = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchComments(ideaId, { page_size: 200, token: shareToken });
      setComments(data.results);
    } catch {
      // silently fail
    } finally {
      setLoading(false);
    }
  }, [ideaId, shareToken]);

  useEffect(() => {
    if (open) {
      loadComments();
      markCommentsRead(ideaId, shareToken).catch(() => {});
    }
  }, [open, ideaId, shareToken, loadComments]);

  // Scroll to bottom when comments change
  useEffect(() => {
    if (scrollRef.current && !loading) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [comments, loading]);

  // WebSocket listeners
  useEffect(() => {
    const onCreated = (e: Event) => {
      const comment = (e as CustomEvent).detail as IdeaComment;
      if (comment.idea_id === ideaId) {
        setComments((prev) => {
          if (prev.some((c) => c.id === comment.id)) return prev;
          return [...prev, comment];
        });
        if (open) {
          markCommentsRead(ideaId, shareToken).catch(() => {});
        }
      }
    };

    const onUpdated = (e: Event) => {
      const comment = (e as CustomEvent).detail as IdeaComment;
      if (comment.idea_id === ideaId) {
        setComments((prev) =>
          prev.map((c) => (c.id === comment.id ? comment : c))
        );
      }
    };

    const onDeleted = (e: Event) => {
      const { id, idea_id } = (e as CustomEvent).detail;
      if (idea_id === ideaId) {
        setComments((prev) =>
          prev.map((c) =>
            c.id === id
              ? { ...c, deleted_at: new Date().toISOString(), content: "" }
              : c
          )
        );
      }
    };

    const onReaction = (e: Event) => {
      const { comment_id, idea_id, emoji, user_id, action } = (
        e as CustomEvent
      ).detail;
      if (idea_id === ideaId) {
        setComments((prev) =>
          prev.map((c) => {
            if (c.id !== comment_id) return c;
            const reactions = [...c.reactions];
            const existing = reactions.find((r) => r.emoji === emoji);
            if (action === "added") {
              if (existing) {
                if (!existing.users.includes(user_id)) {
                  existing.users = [...existing.users, user_id];
                  existing.count = existing.users.length;
                }
              } else {
                reactions.push({ emoji, users: [user_id], count: 1 });
              }
            } else if (action === "removed" && existing) {
              existing.users = existing.users.filter((u) => u !== user_id);
              existing.count = existing.users.length;
              if (existing.count === 0) {
                const idx = reactions.indexOf(existing);
                reactions.splice(idx, 1);
              }
            }
            return { ...c, reactions };
          })
        );
      }
    };

    window.addEventListener("ws:comment_created", onCreated);
    window.addEventListener("ws:comment_updated", onUpdated);
    window.addEventListener("ws:comment_deleted", onDeleted);
    window.addEventListener("ws:comment_reaction", onReaction);
    return () => {
      window.removeEventListener("ws:comment_created", onCreated);
      window.removeEventListener("ws:comment_updated", onUpdated);
      window.removeEventListener("ws:comment_deleted", onDeleted);
      window.removeEventListener("ws:comment_reaction", onReaction);
    };
  }, [ideaId, open]);

  const handleSubmit = useCallback(
    async (content: string) => {
      await createComment(ideaId, {
        content,
        parent_id: replyTo,
      }, shareToken);
      setReplyTo(null);
    },
    [ideaId, replyTo, shareToken]
  );

  const handleCommentUpdated = useCallback((updated: IdeaComment) => {
    setComments((prev) =>
      prev.map((c) => (c.id === updated.id ? updated : c))
    );
  }, []);

  // Build thread structure
  const topLevel = comments.filter((c) => !c.parent_id);
  const repliesMap = new Map<string, IdeaComment[]>();
  for (const c of comments) {
    if (c.parent_id) {
      const existing = repliesMap.get(c.parent_id) || [];
      existing.push(c);
      repliesMap.set(c.parent_id, existing);
    }
  }

  const replyToComment = replyTo
    ? comments.find((c) => c.id === replyTo)
    : null;

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side="right"
        className="w-full sm:max-w-lg flex flex-col p-0"
        data-testid="comments-panel"
      >
        <SheetHeader className="px-6 pt-6 pb-3 border-b border-border">
          <SheetTitle>
            {t("comments.title", "Comments")}
          </SheetTitle>
          <SheetDescription className="sr-only">
            {t("comments.description", "Discussion and activity timeline for this idea")}
          </SheetDescription>
        </SheetHeader>

        <div
          ref={scrollRef}
          className="flex-1 overflow-y-auto px-4 py-3 space-y-1"
        >
          {loading ? (
            <div className="space-y-4 pt-2">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex gap-3">
                  <Skeleton className="h-8 w-8 rounded-full shrink-0" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-12 w-full" />
                  </div>
                </div>
              ))}
            </div>
          ) : topLevel.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
              <MessageSquareOff className="h-10 w-10 mb-3" />
              <p className="text-sm">
                {t("comments.empty", "No comments yet. Start the discussion!")}
              </p>
            </div>
          ) : (
            topLevel.map((comment) => (
              <div key={comment.id}>
                {comment.is_system_event ? (
                  <SystemEventItem comment={comment} />
                ) : (
                  <CommentItem
                    comment={comment}
                    ideaId={ideaId}
                    currentUserId={currentUserId}
                    isOwnerOrCollaborator={isOwnerOrCollaborator}
                    onReply={() => setReplyTo(comment.id)}
                    onUpdated={handleCommentUpdated}
                    shareToken={shareToken}
                  />
                )}
                {/* Nested replies */}
                {repliesMap.get(comment.id)?.map((reply) => (
                  <div key={reply.id} className="ml-8 border-l-2 border-border/50 pl-3">
                    {reply.is_system_event ? (
                      <SystemEventItem comment={reply} />
                    ) : (
                      <CommentItem
                        comment={reply}
                        ideaId={ideaId}
                        currentUserId={currentUserId}
                        isOwnerOrCollaborator={isOwnerOrCollaborator}
                        onReply={() => setReplyTo(reply.id)}
                        onUpdated={handleCommentUpdated}
                        isReply
                        shareToken={shareToken}
                      />
                    )}
                  </div>
                ))}
              </div>
            ))
          )}
        </div>

        {!disabled && (
          <div className="shrink-0 border-t border-border px-4 py-3">
            {replyToComment && (
              <div className="flex items-center gap-2 mb-2 text-xs text-muted-foreground">
                <span>
                  Replying to{" "}
                  <strong>
                    {replyToComment.author?.display_name || "comment"}
                  </strong>
                </span>
                <button
                  onClick={() => setReplyTo(null)}
                  className="text-xs text-destructive hover:underline"
                >
                  Cancel
                </button>
              </div>
            )}
            <CommentInput
              ideaId={ideaId}
              onSubmit={handleSubmit}
              placeholder={
                replyTo
                  ? t("comments.replyPlaceholder", "Write a reply...")
                  : t("comments.placeholder", "Write a comment...")
              }
            />
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}
