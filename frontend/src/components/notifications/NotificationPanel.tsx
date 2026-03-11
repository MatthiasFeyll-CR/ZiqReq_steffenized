import { useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Check } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  fetchNotifications,
  markNotificationActioned,
} from "@/api/notifications";
import type { Notification } from "@/api/notifications";
import { NotificationItem } from "./NotificationItem";

interface NotificationPanelProps {
  onClose: () => void;
}

function getNavigationPath(notification: Notification): string | null {
  if (!notification.reference_id) return null;
  switch (notification.reference_type) {
    case "idea":
      return `/ideas/${notification.reference_id}`;
    case "invitation":
      return `/ideas/${notification.reference_id}`;
    case "merge_request":
      return `/ideas/${notification.reference_id}`;
    default:
      return null;
  }
}

export function NotificationPanel({ onClose }: NotificationPanelProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => fetchNotifications(1, 20),
  });

  const markActioned = useMutation({
    mutationFn: markNotificationActioned,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["notificationUnreadCount"] });
    },
  });

  const handleItemClick = useCallback(
    (notification: Notification) => {
      markActioned.mutate(notification.id);
      const path = getNavigationPath(notification);
      if (path) {
        navigate(path);
      }
      onClose();
    },
    [markActioned, navigate, onClose],
  );

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    function handleClickOutside(e: MouseEvent) {
      if (
        panelRef.current &&
        !panelRef.current.contains(e.target as Node)
      ) {
        onClose();
      }
    }
    document.addEventListener("keydown", handleKeyDown);
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [onClose]);

  // Re-fetch on WebSocket notification events
  useEffect(() => {
    function handleWsNotification() {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    }
    window.addEventListener("ws:notification", handleWsNotification);
    return () => {
      window.removeEventListener("ws:notification", handleWsNotification);
    };
  }, [queryClient]);

  const notifications = data?.notifications ?? [];

  return (
    <div
      ref={panelRef}
      className="absolute right-0 top-full z-20 mt-2 w-96 rounded-lg border bg-popover text-popover-foreground shadow-lg"
      role="dialog"
      aria-label="Notifications"
    >
      <div className="border-b px-4 py-2">
        <h3 className="text-sm font-semibold">Notifications</h3>
      </div>
      {isLoading ? (
        <div className="px-4 py-8 text-center text-sm text-muted-foreground">
          Loading...
        </div>
      ) : notifications.length === 0 ? (
        <div className="flex flex-col items-center gap-2 px-4 py-8">
          <Check className="h-8 w-8 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">All caught up</p>
        </div>
      ) : (
        <div className="max-h-96 overflow-y-auto">
          {notifications.map((n) => (
            <NotificationItem
              key={n.id}
              notification={n}
              onClick={handleItemClick}
            />
          ))}
        </div>
      )}
    </div>
  );
}
