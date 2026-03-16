import type { IdeaComment } from "@/api/comments";
import { CommentContent } from "./CommentContent";
import {
  ArrowRightLeft,
  GitBranch,
  LogIn,
  LogOut,
  UserMinus,
} from "lucide-react";

const EVENT_ICONS: Record<string, typeof ArrowRightLeft> = {
  state_changed: ArrowRightLeft,
  collaborator_joined: LogIn,
  collaborator_left: LogOut,
  collaborator_removed: UserMinus,
  owner_changed: GitBranch,
};

interface SystemEventItemProps {
  comment: IdeaComment;
}

export function SystemEventItem({ comment }: SystemEventItemProps) {
  const Icon = EVENT_ICONS[comment.system_event_type || ""] || ArrowRightLeft;
  const timeStr = new Date(comment.created_at).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className="flex items-center gap-2 py-2 text-xs text-muted-foreground" data-testid="system-event">
      <div className="h-6 w-6 rounded-full bg-muted flex items-center justify-center shrink-0">
        <Icon className="h-3 w-3" />
      </div>
      <div className="flex-1 min-w-0">
        <CommentContent content={comment.content} />
      </div>
      <span className="shrink-0">{timeStr}</span>
    </div>
  );
}
