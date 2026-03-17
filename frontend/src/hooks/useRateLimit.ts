import { useCallback, useEffect, useState } from "react";
import { toast } from "react-toastify";
import i18n from "@/i18n/config";

/**
 * Tracks rate limit state for a specific project's chat.
 * Listens for WebSocket events: rate_limit (locks) and ai_processing completed (unlocks).
 */
export function useRateLimit(projectId: string) {
  const [isLimited, setIsLimited] = useState(false);

  useEffect(() => {
    const handleRateLimit = (e: Event) => {
      const detail = (e as CustomEvent<{ project_id: string }>).detail;
      if (detail?.project_id !== projectId) return;
      setIsLimited(true);
      toast.warning(i18n.t("chat.rateLimited"));

      // Also push to notification bell
      window.dispatchEvent(
        new CustomEvent("ws:notification", {
          detail: {
            event_type: "rate_limit",
            title: i18n.t("chat.rateLimited"),
          },
        }),
      );
    };

    const handleAiProcessing = (e: Event) => {
      const detail = (e as CustomEvent<{ project_id: string; state: string }>).detail;
      if (detail?.project_id !== projectId) return;
      if (detail.state === "completed" || detail.state === "failed") {
        setIsLimited(false);
      }
    };

    window.addEventListener("ws:rate_limit", handleRateLimit);
    window.addEventListener("ws:ai_processing", handleAiProcessing);
    return () => {
      window.removeEventListener("ws:rate_limit", handleRateLimit);
      window.removeEventListener("ws:ai_processing", handleAiProcessing);
    };
  }, [projectId]);

  const reset = useCallback(() => setIsLimited(false), []);

  return { isLimited, reset };
}
