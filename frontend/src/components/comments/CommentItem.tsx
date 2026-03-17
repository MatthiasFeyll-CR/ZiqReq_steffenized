import { useCallback, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  updateComment,
  deleteComment,
  addReaction,
  removeReaction,
  type ProjectComment,
} from "@/api/comments";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { MoreHorizontal, Pencil, Reply, SmilePlus, Trash2 } from "lucide-react";
import { CommentContent } from "./CommentContent";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

const QUICK_EMOJIS = ["\u{1F44D}", "\u{1F44E}", "\u{2764}\u{FE0F}", "\u{1F389}", "\u{1F440}", "\u{1F4AF}"];

interface CommentItemProps {
  comment: ProjectComment;
  projectId: string;
  currentUserId?: string;
  isOwnerOrCollaborator?: boolean;
  onReply: () => void;
  onUpdated: (comment: ProjectComment) => void;
  isReply?: boolean;
  shareToken?: string | null;
}

export function CommentItem({
  comment,
  projectId,
  currentUserId,
  isOwnerOrCollaborator = false,
  onReply,
  onUpdated,
  isReply = false,
  shareToken,
}: CommentItemProps) {
  const { t } = useTranslation();
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(comment.content);
  const [showEmojis, setShowEmojis] = useState(false);

  const isDeleted = !!comment.deleted_at;
  const isAuthor = currentUserId === comment.author?.id;
  const canDelete = isAuthor || isOwnerOrCollaborator;

  const handleSaveEdit = useCallback(async () => {
    const trimmed = editContent.trim();
    if (!trimmed || trimmed === comment.content) {
      setIsEditing(false);
      return;
    }
    try {
      const updated = await updateComment(projectId, comment.id, {
        content: trimmed,
      }, shareToken);
      onUpdated(updated);
      setIsEditing(false);
    } catch {
      // stay in edit mode
    }
  }, [editContent, comment, projectId, onUpdated]);

  const handleDelete = useCallback(async () => {
    try {
      await deleteComment(projectId, comment.id, shareToken);
    } catch {
      // silently fail
    }
  }, [projectId, comment.id, shareToken]);

  const handleToggleReaction = useCallback(
    async (emoji: string) => {
      if (!currentUserId) return;
      const existing = comment.reactions.find((r) => r.emoji === emoji);
      const hasReacted = existing?.users.includes(currentUserId);
      try {
        if (hasReacted) {
          await removeReaction(projectId, comment.id, emoji, shareToken);
        } else {
          await addReaction(projectId, comment.id, emoji, shareToken);
        }
      } catch {
        // silently fail
      }
      setShowEmojis(false);
    },
    [projectId, comment, currentUserId, shareToken]
  );

  const timeAgo = formatTimeAgo(comment.created_at);
  const initials = comment.author?.display_name
    ?.split(" ")
    .map((n) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase() || "?";

  if (isDeleted) {
    return (
      <div className="flex gap-3 py-2 opacity-50">
        <Avatar size="sm">
          <AvatarFallback userId={comment.author?.id}>{initials}</AvatarFallback>
        </Avatar>
        <div className="flex-1 min-w-0">
          <p className="text-xs text-muted-foreground italic">
            {t("comments.deleted", "This comment has been deleted")}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={cn("group flex gap-3 py-2", isReply && "py-1.5")} data-testid="comment-item">
      <Avatar size="sm">
        <AvatarFallback userId={comment.author?.id}>{initials}</AvatarFallback>
      </Avatar>
      <div className="flex-1 min-w-0">
        <div className="flex items-baseline gap-2">
          <span className="text-sm font-medium text-foreground truncate">
            {comment.author?.display_name || "Unknown"}
          </span>
          <span className="text-xs text-muted-foreground shrink-0">
            {timeAgo}
          </span>
          {comment.is_edited && (
            <span className="text-xs text-muted-foreground">(edited)</span>
          )}

          {/* Actions */}
          <div className="ml-auto flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={() => setShowEmojis((s) => !s)}
              className="p-1 rounded hover:bg-muted text-muted-foreground"
              title="React"
            >
              <SmilePlus className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={onReply}
              className="p-1 rounded hover:bg-muted text-muted-foreground"
              title="Reply"
            >
              <Reply className="h-3.5 w-3.5" />
            </button>
            {(isAuthor || canDelete) && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="p-1 rounded hover:bg-muted text-muted-foreground">
                    <MoreHorizontal className="h-3.5 w-3.5" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  {isAuthor && (
                    <DropdownMenuItem
                      onClick={() => {
                        setEditContent(comment.content);
                        setIsEditing(true);
                      }}
                    >
                      <Pencil className="mr-2 h-3.5 w-3.5" />
                      {t("comments.edit", "Edit")}
                    </DropdownMenuItem>
                  )}
                  {canDelete && (
                    <DropdownMenuItem
                      className="text-destructive focus:text-destructive"
                      onClick={handleDelete}
                    >
                      <Trash2 className="mr-2 h-3.5 w-3.5" />
                      {t("comments.delete", "Delete")}
                    </DropdownMenuItem>
                  )}
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>
        </div>

        {/* Emoji picker row */}
        {showEmojis && (
          <div className="flex gap-1 mt-1">
            {QUICK_EMOJIS.map((emoji) => (
              <button
                key={emoji}
                onClick={() => handleToggleReaction(emoji)}
                className="text-base hover:bg-muted rounded px-1 py-0.5 transition-colors"
              >
                {emoji}
              </button>
            ))}
          </div>
        )}

        {/* Content */}
        {isEditing ? (
          <div className="mt-1 space-y-2">
            <Textarea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              className="min-h-[60px] text-sm"
              autoFocus
            />
            <div className="flex gap-2">
              <Button size="sm" onClick={handleSaveEdit}>
                {t("common.save", "Save")}
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setIsEditing(false)}
              >
                {t("common.cancel", "Cancel")}
              </Button>
            </div>
          </div>
        ) : (
          <div className="mt-0.5">
            <CommentContent content={comment.content} />
          </div>
        )}

        {/* Reactions */}
        {comment.reactions.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-1.5">
            {comment.reactions.map((r) => {
              const hasReacted = currentUserId
                ? r.users.includes(currentUserId)
                : false;
              return (
                <button
                  key={r.emoji}
                  onClick={() => handleToggleReaction(r.emoji)}
                  className={cn(
                    "inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-xs border transition-colors",
                    hasReacted
                      ? "bg-primary/10 border-primary/30 text-primary"
                      : "bg-muted border-border text-muted-foreground hover:border-primary/30"
                  )}
                >
                  <span>{r.emoji}</span>
                  <span>{r.count}</span>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

function formatTimeAgo(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMin = Math.floor(diffMs / 60_000);
  if (diffMin < 1) return "just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHours = Math.floor(diffMin / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });
}
