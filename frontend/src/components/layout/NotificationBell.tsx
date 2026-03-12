import { useCallback, useEffect, useRef, useState } from "react";
import { Bell } from "lucide-react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-toastify";
import { fetchUnreadCount } from "@/api/notifications";

function getToastType(eventType: string): "info" | "success" | "warning" {
  if (eventType.startsWith("review_state")) return "warning";
  if (eventType === "review_comment") return "info";
  if (
    eventType === "collaborator_joined" ||
    eventType === "merge_accepted" ||
    eventType.startsWith("ai_delegation")
  )
    return "success";
  if (
    eventType === "removed_from_idea" ||
    eventType === "merge_declined" ||
    eventType === "monitoring_alert" ||
    eventType === "rate_limit"
  )
    return "warning";
  return "info";
}

interface NotificationBellProps {
  onTogglePanel: () => void;
}

export function NotificationBell({ onTogglePanel }: NotificationBellProps) {
  const queryClient = useQueryClient();
  const { data } = useQuery({
    queryKey: ["notificationUnreadCount"],
    queryFn: fetchUnreadCount,
    refetchInterval: 60_000,
  });

  const count = data?.unread_count ?? 0;
  const [animate, setAnimate] = useState(false);
  const prevCountRef = useRef(count);

  useEffect(() => {
    if (count > prevCountRef.current) {
      setAnimate(true);
      const timer = setTimeout(() => setAnimate(false), 300);
      return () => clearTimeout(timer);
    }
    prevCountRef.current = count;
  }, [count]);

  // Event types that should be silently ignored (no toast, no bell increment)
  const SILENT_EVENT_TYPES = new Set(["ai_delegation_complete"]);

  const handleNotificationEvent = useCallback(
    (e: Event) => {
      const detail = (e as CustomEvent).detail as {
        event_type?: string;
        title?: string;
        body?: string;
      } | undefined;

      const eventType = detail?.event_type ?? "";

      // Skip silent event types entirely
      if (SILENT_EVENT_TYPES.has(eventType)) return;

      // Optimistic count update + server reconciliation
      queryClient.setQueryData<{ unread_count: number }>(
        ["notificationUnreadCount"],
        (old) => ({ unread_count: (old?.unread_count ?? 0) + 1 }),
      );
      queryClient.invalidateQueries({ queryKey: ["notificationUnreadCount"] });

      // Display toast with severity based on event type
      if (detail?.title) {
        const toastType = getToastType(eventType);
        const message = detail.body
          ? `${detail.title}: ${detail.body}`
          : detail.title;
        toast[toastType](message, { autoClose: 5000 });
      }
    },
    [queryClient],
  );

  useEffect(() => {
    window.addEventListener("ws:notification", handleNotificationEvent);
    return () => {
      window.removeEventListener("ws:notification", handleNotificationEvent);
    };
  }, [handleNotificationEvent]);

  const displayCount = count > 99 ? "99+" : String(count);

  return (
    <button
      className="relative rounded-full p-1.5 text-white/70 transition-colors hover:bg-white/10 hover:text-white"
      onClick={onTogglePanel}
      aria-label="Notifications"
    >
      <Bell className="h-5 w-5" />
      {count > 0 && (
        <span
          className={`absolute -right-1 -top-1 flex min-w-5 items-center justify-center rounded-full bg-primary px-1 text-xs font-bold text-primary-foreground ${animate ? "animate-scale-in" : ""}`}
          style={{ height: "1.25rem" }}
        >
          {displayCount}
        </span>
      )}
    </button>
  );
}
