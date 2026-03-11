import {
  UserPlus,
  CheckCircle,
  XCircle,
  AlertCircle,
  AtSign,
  GitMerge,
  Bell,
} from "lucide-react";
import type { Notification } from "@/api/notifications";

function getIcon(eventType: string) {
  if (eventType.startsWith("collaboration") || eventType === "collaborator_joined" || eventType === "collaborator_left" || eventType === "removed_from_idea" || eventType === "ownership_transferred") {
    return <UserPlus className="h-4 w-4 shrink-0 text-blue-500" />;
  }
  if (eventType === "review_state_changed" || eventType === "idea_submitted" || eventType === "idea_assigned" || eventType === "idea_resubmitted") {
    return <CheckCircle className="h-4 w-4 shrink-0 text-green-500" />;
  }
  if (eventType === "review_comment") {
    return <AlertCircle className="h-4 w-4 shrink-0 text-amber-500" />;
  }
  if (eventType === "review_rejected" || eventType === "review_dropped") {
    return <XCircle className="h-4 w-4 shrink-0 text-red-500" />;
  }
  if (eventType === "chat_mention") {
    return <AtSign className="h-4 w-4 shrink-0 text-purple-500" />;
  }
  if (eventType.startsWith("similarity") || eventType.startsWith("merge") || eventType === "idea_closed_append") {
    return <GitMerge className="h-4 w-4 shrink-0 text-orange-500" />;
  }
  return <Bell className="h-4 w-4 shrink-0 text-muted-foreground" />;
}

function relativeTime(dateStr: string): string {
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const diffSec = Math.floor((now - then) / 1000);
  if (diffSec < 60) return "just now";
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  const diffDay = Math.floor(diffHr / 24);
  return `${diffDay}d ago`;
}

interface NotificationItemProps {
  notification: Notification;
  onClick: (notification: Notification) => void;
}

export function NotificationItem({ notification, onClick }: NotificationItemProps) {
  const isUnacted = !notification.action_taken;
  return (
    <button
      className={`flex w-full items-start gap-3 border-b px-4 py-3 text-left transition-colors hover:bg-muted/50 ${isUnacted ? "bg-primary/5" : ""}`}
      onClick={() => onClick(notification)}
    >
      <div className="mt-0.5">{getIcon(notification.event_type)}</div>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-foreground">{notification.title}</p>
        <p className="truncate text-xs text-muted-foreground">{notification.body}</p>
        <p className="mt-0.5 text-[10px] text-muted-foreground">
          {relativeTime(notification.created_at)}
        </p>
      </div>
    </button>
  );
}
