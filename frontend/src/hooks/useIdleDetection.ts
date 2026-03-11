import { useEffect, useRef, useCallback } from "react";
import { useWsSend } from "@/app/providers";

const THROTTLE_MS = 500;
const DEFAULT_IDLE_TIMEOUT = 300; // seconds

interface UseIdleDetectionOptions {
  ideaId: string;
  idleTimeout?: number; // seconds
}

/**
 * Detects user idle state via mouse inactivity and tab visibility.
 * Sends presence_update WebSocket messages when idle state changes.
 */
export function useIdleDetection({
  ideaId,
  idleTimeout = DEFAULT_IDLE_TIMEOUT,
}: UseIdleDetectionOptions) {
  const sendMessage = useWsSend();
  const isIdleRef = useRef(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastMoveRef = useRef<number>(0);

  const sendPresence = useCallback(
    (state: "idle" | "active") => {
      sendMessage({
        type: "presence_update",
        payload: {
          idea_id: ideaId,
          state,
        },
      });
    },
    [sendMessage, ideaId],
  );

  const setIdle = useCallback(() => {
    if (!isIdleRef.current) {
      isIdleRef.current = true;
      sendPresence("idle");
    }
  }, [sendPresence]);

  const clearIdle = useCallback(() => {
    if (isIdleRef.current) {
      isIdleRef.current = false;
      sendPresence("active");
    }
  }, [sendPresence]);

  const resetTimer = useCallback(() => {
    if (timerRef.current !== null) {
      clearTimeout(timerRef.current);
    }
    timerRef.current = setTimeout(setIdle, idleTimeout * 1000);
  }, [idleTimeout, setIdle]);

  useEffect(() => {
    // Start the idle timer
    resetTimer();

    // Throttled mouse move handler
    const handleMouseMove = () => {
      const now = Date.now();
      if (now - lastMoveRef.current < THROTTLE_MS) return;
      lastMoveRef.current = now;

      clearIdle();
      resetTimer();
    };

    // Tab visibility handler — idle immediately on hidden
    const handleVisibilityChange = () => {
      if (document.visibilityState === "hidden") {
        if (timerRef.current !== null) {
          clearTimeout(timerRef.current);
          timerRef.current = null;
        }
        setIdle();
      } else {
        // Tab became visible again — treat as activity
        clearIdle();
        resetTimer();
      }
    };

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      if (timerRef.current !== null) {
        clearTimeout(timerRef.current);
      }
    };
  }, [resetTimer, clearIdle, setIdle]);

  return { isIdle: isIdleRef };
}
