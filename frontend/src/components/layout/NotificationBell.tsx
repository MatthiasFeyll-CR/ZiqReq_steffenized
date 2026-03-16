import { useCallback, useEffect, useRef, useState } from "react";
import { Bell } from "lucide-react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-toastify";
import { useDispatch, useSelector } from "react-redux";
import { fetchUnreadCount } from "@/api/notifications";
import { markNotificationActioned } from "@/api/notifications";
import {
  addToastNotification,
  type ToastNotification,
} from "@/store/toast-notification-slice";
import type { RootState } from "@/store";

function getToastType(eventType: string): "info" | "success" | "warning" {
  if (eventType.startsWith("review_state")) return "warning";
  if (eventType === "review_comment") return "info";
  if (
    eventType === "collaborator_joined" ||
    eventType.startsWith("ai_delegation")
  )
    return "success";
  if (
    eventType === "removed_from_idea" ||
    eventType === "monitoring_alert" ||
    eventType === "rate_limit"
  )
    return "warning";
  return "info";
}

// Event types that should be silently ignored (no toast, no bell increment)
const SILENT_EVENT_TYPES = new Set(["ai_delegation_complete"]);

interface NotificationBellProps {
  onTogglePanel: () => void;
}

export function NotificationBell({ onTogglePanel }: NotificationBellProps) {
  const queryClient = useQueryClient();
  const dispatch = useDispatch();
  const { data } = useQuery({
    queryKey: ["notificationUnreadCount"],
    queryFn: fetchUnreadCount,
    refetchInterval: 60_000,
  });

  const localCount = useSelector(
    (state: RootState) => state.toastNotifications.items.length,
  );
  const serverCount = data?.unread_count ?? 0;
  const count = serverCount + localCount;

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

  const handleNotificationEvent = useCallback(
    (e: Event) => {
      const detail = (e as CustomEvent).detail as
        | {
            notification_id?: string;
            event_type?: string;
            title?: string;
            body?: string;
            reference_id?: string;
            reference_type?: string;
          }
        | undefined;

      const eventType = detail?.event_type ?? "";

      // Skip silent event types entirely
      if (SILENT_EVENT_TYPES.has(eventType)) return;

      // Optimistic count update + server reconciliation
      queryClient.setQueryData<{ unread_count: number }>(
        ["notificationUnreadCount"],
        (old) => ({ unread_count: (old?.unread_count ?? 0) + 1 }),
      );
      queryClient.invalidateQueries({ queryKey: ["notificationUnreadCount"] });

      if (detail?.title) {
        const toastType = getToastType(eventType);
        const message = detail.body
          ? `${detail.title}: ${detail.body}`
          : detail.title;

        // Track whether the user clicked (actioned) the toast
        let userActioned = false;

        const notifPayload: ToastNotification = {
          id: detail.notification_id ?? crypto.randomUUID(),
          event_type: eventType,
          title: detail.title,
          body: detail.body ?? "",
          reference_id: detail.reference_id,
          reference_type: detail.reference_type,
          created_at: new Date().toISOString(),
        };

        toast[toastType](message, {
          autoClose: 5000,
          onClick: () => {
            userActioned = true;
            // Mark as actioned on the server
            if (detail.notification_id) {
              markNotificationActioned(detail.notification_id).catch(() => {});
              queryClient.invalidateQueries({
                queryKey: ["notificationUnreadCount"],
              });
              queryClient.invalidateQueries({
                queryKey: ["notifications"],
              });
            }
          },
          onClose: () => {
            if (!userActioned) {
              // User ignored the toast — store it in the bell
              dispatch(addToastNotification(notifPayload));
            }
          },
        });
      }
    },
    [queryClient, dispatch],
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
