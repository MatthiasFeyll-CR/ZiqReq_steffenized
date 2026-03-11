import { useCallback, useEffect, useState } from "react";
import { toast } from "react-toastify";
import i18n from "@/i18n/config";

/**
 * Tracks rate limit state for a specific idea's chat.
 * Listens for WebSocket events: rate_limit (locks) and ai_processing completed (unlocks).
 */
export function useRateLimit(ideaId: string) {
  const [isLimited, setIsLimited] = useState(false);

  useEffect(() => {
    const handleRateLimit = (e: Event) => {
      const detail = (e as CustomEvent<{ idea_id: string }>).detail;
      if (detail?.idea_id !== ideaId) return;
      setIsLimited(true);
      toast.warning(i18n.t("chat.rateLimited"));
    };

    const handleAiProcessing = (e: Event) => {
      const detail = (e as CustomEvent<{ idea_id: string; state: string }>).detail;
      if (detail?.idea_id !== ideaId) return;
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
  }, [ideaId]);

  const reset = useCallback(() => setIsLimited(false), []);

  return { isLimited, reset };
}
