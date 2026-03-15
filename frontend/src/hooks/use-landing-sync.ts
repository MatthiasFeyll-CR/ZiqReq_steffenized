import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";

/**
 * Listens to WebSocket custom events and invalidates landing page
 * query caches so idea lists and invitations update in real time.
 */
export function useLandingSync() {
  const queryClient = useQueryClient();

  useEffect(() => {
    const invalidateAll = () => {
      queryClient.invalidateQueries({ queryKey: ["ideas"] });
      queryClient.invalidateQueries({ queryKey: ["invitations"] });
    };

    const onNotification = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      const eventType: string | undefined = detail?.event_type;

      if (
        eventType === "collaboration_invitation" ||
        eventType === "collaboration_accepted" ||
        eventType === "collaborator_joined" ||
        eventType === "collaborator_left" ||
        eventType === "removed_from_idea" ||
        eventType === "ownership_transferred"
      ) {
        queryClient.invalidateQueries({ queryKey: ["invitations"] });
        queryClient.invalidateQueries({ queryKey: ["ideas"] });
      } else {
        // Any other notification may affect idea state
        queryClient.invalidateQueries({ queryKey: ["ideas"] });
      }
    };

    const onTitleUpdate = () => {
      queryClient.invalidateQueries({ queryKey: ["ideas"] });
    };

    const onMergeComplete = () => invalidateAll();
    const onAppendComplete = () => invalidateAll();

    window.addEventListener("ws:notification", onNotification);
    window.addEventListener("ws:title_update", onTitleUpdate);
    window.addEventListener("ws:merge_complete", onMergeComplete);
    window.addEventListener("ws:append_complete", onAppendComplete);

    return () => {
      window.removeEventListener("ws:notification", onNotification);
      window.removeEventListener("ws:title_update", onTitleUpdate);
      window.removeEventListener("ws:merge_complete", onMergeComplete);
      window.removeEventListener("ws:append_complete", onAppendComplete);
    };
  }, [queryClient]);
}
