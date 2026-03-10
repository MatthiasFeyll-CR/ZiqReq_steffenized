import { useEffect, useRef, useCallback } from "react";
import { useAuth } from "./use-auth";
import { useDispatch } from "react-redux";
import {
  setConnectionState,
  setReconnectCountdown,
} from "@/store/websocket-slice";
import { env } from "@/config/env";

const INITIAL_BACKOFF_MS = 1000;
const MAX_BACKOFF_MS = 30_000;
const BACKOFF_MULTIPLIER = 2;

function getWsUrl(token: string): string {
  const base = env.wsBaseUrl;
  // If base is a relative path, build full ws:// URL from current location
  if (base.startsWith("/")) {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${window.location.host}${base}/?token=${token}`;
  }
  // Already an absolute URL
  return `${base}/?token=${token}`;
}

export function useWebSocket() {
  const { user, isAuthenticated } = useAuth();
  const dispatch = useDispatch();

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const countdownTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const backoffRef = useRef(INITIAL_BACKOFF_MS);
  const intentionalCloseRef = useRef(false);

  const clearTimers = useCallback(() => {
    if (reconnectTimerRef.current !== null) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    if (countdownTimerRef.current !== null) {
      clearInterval(countdownTimerRef.current);
      countdownTimerRef.current = null;
    }
    dispatch(setReconnectCountdown(null));
  }, [dispatch]);

  const scheduleReconnect = useCallback(
    (token: string) => {
      const delay = backoffRef.current;

      // Start countdown
      let remaining = Math.ceil(delay / 1000);
      dispatch(setReconnectCountdown(remaining));
      countdownTimerRef.current = setInterval(() => {
        remaining -= 1;
        if (remaining <= 0) {
          if (countdownTimerRef.current !== null) {
            clearInterval(countdownTimerRef.current);
            countdownTimerRef.current = null;
          }
          dispatch(setReconnectCountdown(null));
        } else {
          dispatch(setReconnectCountdown(remaining));
        }
      }, 1000);

      reconnectTimerRef.current = setTimeout(() => {
        reconnectTimerRef.current = null;
        connect(token);
      }, delay);

      // Increase backoff for next attempt
      backoffRef.current = Math.min(
        backoffRef.current * BACKOFF_MULTIPLIER,
        MAX_BACKOFF_MS,
      );
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [dispatch],
  );

  const connect = useCallback(
    (token: string) => {
      // Close existing connection if any
      if (wsRef.current) {
        wsRef.current.onclose = null;
        wsRef.current.onerror = null;
        wsRef.current.onopen = null;
        wsRef.current.close();
        wsRef.current = null;
      }

      clearTimers();

      const url = getWsUrl(token);
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        backoffRef.current = INITIAL_BACKOFF_MS;
        dispatch(setConnectionState("online"));
      };

      ws.onclose = () => {
        wsRef.current = null;
        dispatch(setConnectionState("offline"));
        if (!intentionalCloseRef.current) {
          scheduleReconnect(token);
        }
      };

      ws.onerror = () => {
        // onclose will fire after onerror, which handles reconnection
        console.error("[WebSocket] connection error");
      };
    },
    [dispatch, clearTimers, scheduleReconnect],
  );

  const disconnect = useCallback(() => {
    intentionalCloseRef.current = true;
    clearTimers();
    if (wsRef.current) {
      wsRef.current.onclose = null;
      wsRef.current.onerror = null;
      wsRef.current.onopen = null;
      wsRef.current.close();
      wsRef.current = null;
    }
    dispatch(setConnectionState("offline"));
  }, [dispatch, clearTimers]);

  // Connect when authenticated, disconnect on logout or unmount
  useEffect(() => {
    if (isAuthenticated && user) {
      // In dev bypass mode, token = user ID
      const token = user.id;
      intentionalCloseRef.current = false;
      connect(token);
    } else {
      disconnect();
    }

    return () => {
      disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, user?.id]);

  return { wsRef, disconnect };
}
