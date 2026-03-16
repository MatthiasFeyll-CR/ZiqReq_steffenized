import { useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Check } from "lucide-react";
import { useTranslation } from "react-i18next";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useSelector, useDispatch } from "react-redux";
import {
  fetchNotifications,
  markNotificationActioned,
} from "@/api/notifications";
import type { Notification } from "@/api/notifications";
import { NotificationItem } from "./NotificationItem";
import type { RootState } from "@/store";
import {
  dismissToastNotification,
  type ToastNotification,
} from "@/store/toast-notification-slice";

interface NotificationPanelProps {
  onClose: () => void;
}

function getNavigationPath(refType?: string | null, refId?: string | null): string | null {
  if (!refId) return null;
  switch (refType) {
    case "idea":
    case "invitation":
      return `/idea/${refId}`;
    default:
      return null;
  }
}

export function NotificationPanel({ onClose }: NotificationPanelProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const dispatch = useDispatch();

  const localItems = useSelector(
    (state: RootState) => state.toastNotifications.items,
  );

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

  const handleServerItemClick = useCallback(
    (notification: Notification) => {
      markActioned.mutate(notification.id);
      const path = getNavigationPath(notification.reference_type, notification.reference_id);
      if (path) {
        navigate(path);
      }
      onClose();
    },
    [markActioned, navigate, onClose],
  );

  const handleLocalItemClick = useCallback(
    (item: ToastNotification) => {
      dispatch(dismissToastNotification(item.id));
      // Also mark on server if we have a server-side notification id
      markActioned.mutate(item.id);
      const path = getNavigationPath(item.reference_type, item.reference_id);
      if (path) {
        navigate(path);
      }
      onClose();
    },
    [dispatch, markActioned, navigate, onClose],
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

  const serverNotifications = data?.notifications ?? [];

  // Deduplicate: if a local item already exists in server list, skip the local one
  const serverIds = new Set(serverNotifications.map((n) => n.id));
  const uniqueLocalItems = localItems.filter((l) => !serverIds.has(l.id));

  const hasItems = uniqueLocalItems.length > 0 || serverNotifications.length > 0;

  return (
    <div
      ref={panelRef}
      className="absolute right-0 top-full z-20 mt-2 w-96 rounded-lg border bg-popover text-popover-foreground shadow-lg"
      role="dialog"
      aria-label="Notifications"
    >
      <div className="border-b px-4 py-2">
        <h3 className="text-sm font-semibold">{t("notifications.title")}</h3>
      </div>
      {isLoading ? (
        <div className="px-4 py-8 text-center text-sm text-muted-foreground">
          {t("common.loading")}
        </div>
      ) : !hasItems ? (
        <div className="flex flex-col items-center gap-2 px-4 py-8">
          <Check className="h-8 w-8 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">{t("notifications.allCaughtUp")}</p>
        </div>
      ) : (
        <div className="max-h-96 overflow-y-auto" role="list" aria-label={t("notifications.title")}>
          {/* Local (missed toast) notifications — shown first */}
          {uniqueLocalItems.map((item) => (
            <NotificationItem
              key={`local-${item.id}`}
              notification={{
                id: item.id,
                user_id: "",
                event_type: item.event_type,
                title: item.title,
                body: item.body,
                reference_id: item.reference_id ?? null,
                reference_type: item.reference_type ?? null,
                is_read: false,
                action_taken: false,
                created_at: item.created_at,
              }}
              onClick={() => handleLocalItemClick(item)}
            />
          ))}
          {/* Server-persisted notifications */}
          {serverNotifications.map((n) => (
            <NotificationItem
              key={n.id}
              notification={n}
              onClick={handleServerItemClick}
            />
          ))}
        </div>
      )}
    </div>
  );
}
