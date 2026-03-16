import { useEffect, useRef, useCallback } from "react";
import { useAuth } from "./use-auth";
import { useDispatch } from "react-redux";
import {
  setConnectionState,
  setReconnectCountdown,
  setIdleDisconnected,
} from "@/store/websocket-slice";
import { updatePresence } from "@/store/presence-slice";
import { updateSelection } from "@/store/selections-slice";
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
  const { user, isAuthenticated, getAccessToken } = useAuth();
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

      ws.onmessage = (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "presence_update" && data.idea_id && data.payload) {
            dispatch(
              updatePresence({
                idea_id: data.idea_id,
                user: data.payload.user,
                state: data.payload.state,
              }),
            );
          } else if (data.type === "title_update" && data.idea_id && data.payload) {
            window.dispatchEvent(
              new CustomEvent("ws:title_update", {
                detail: { idea_id: data.idea_id, title: data.payload.title },
              }),
            );
          } else if (data.type === "ai_processing" && data.idea_id && data.payload) {
            window.dispatchEvent(
              new CustomEvent("ws:ai_processing", {
                detail: { idea_id: data.idea_id, state: data.payload.state },
              }),
            );
          } else if (data.type === "rate_limit" && data.idea_id) {
            window.dispatchEvent(
              new CustomEvent("ws:rate_limit", {
                detail: { idea_id: data.idea_id },
              }),
            );
          } else if (data.type === "notification" && data.payload) {
            window.dispatchEvent(
              new CustomEvent("ws:notification", {
                detail: data.payload,
              }),
            );
          } else if (data.type === "chat_message" && data.idea_id && data.payload) {
            window.dispatchEvent(
              new CustomEvent("ws:chat_message", {
                detail: { idea_id: data.idea_id, message: data.payload },
              }),
            );
          } else if (data.type === "ai_reaction" && data.idea_id && data.payload) {
            window.dispatchEvent(
              new CustomEvent("ws:ai_reaction", {
                detail: { idea_id: data.idea_id, ...data.payload },
              }),
            );
          } else if (data.type === "board_update" && data.idea_id && data.payload) {
            window.dispatchEvent(
              new CustomEvent("ws:board_update", {
                detail: { idea_id: data.idea_id, ...data.payload },
              }),
            );
          } else if (data.type === "brd_generating" && data.idea_id && data.payload) {
            window.dispatchEvent(
              new CustomEvent("ws:brd_generating", {
                detail: { idea_id: data.idea_id, ...data.payload },
              }),
            );
          } else if (data.type === "brd_ready" && data.idea_id && data.payload) {
            window.dispatchEvent(
              new CustomEvent("ws:brd_ready", {
                detail: { idea_id: data.idea_id, ...data.payload },
              }),
            );
          } else if (data.type === "comment_created" && data.payload) {
            window.dispatchEvent(
              new CustomEvent("ws:comment_created", {
                detail: data.payload,
              }),
            );
          } else if (data.type === "comment_updated" && data.payload) {
            window.dispatchEvent(
              new CustomEvent("ws:comment_updated", {
                detail: data.payload,
              }),
            );
          } else if (data.type === "comment_deleted" && data.payload) {
            window.dispatchEvent(
              new CustomEvent("ws:comment_deleted", {
                detail: data.payload,
              }),
            );
          } else if (data.type === "comment_reaction" && data.payload) {
            window.dispatchEvent(
              new CustomEvent("ws:comment_reaction", {
                detail: data.payload,
              }),
            );
          } else if (
            data.type === "board_selection" &&
            data.idea_id &&
            data.payload
          ) {
            dispatch(
              updateSelection({
                idea_id: data.idea_id,
                user_id: data.payload.user.id,
                display_name: data.payload.user.display_name,
                node_id: data.payload.node_id,
              }),
            );
          }
        } catch {
          // Ignore non-JSON messages
        }
      };

      ws.onclose = (event: CloseEvent) => {
        wsRef.current = null;
        const isIdleDisconnect = event.code === 4008;
        if (isIdleDisconnect) {
          dispatch(setIdleDisconnected(true));
        }
        dispatch(setConnectionState("offline"));
        if (!intentionalCloseRef.current && !isIdleDisconnect) {
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
      intentionalCloseRef.current = false;
      getAccessToken().then((token) => {
        if (token) {
          connect(token);
        }
      });
    } else {
      disconnect();
    }

    return () => {
      disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, user?.id]);

  const sendMessage = useCallback((msg: Record<string, unknown>) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(msg));
    }
  }, []);

  const reconnectNow = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return;
    if (!isAuthenticated || !user) return;
    clearTimers();
    backoffRef.current = INITIAL_BACKOFF_MS;
    getAccessToken().then((token) => {
      if (token) {
        connect(token);
      }
    });
  }, [isAuthenticated, user, clearTimers, connect, getAccessToken]);

  return { wsRef, disconnect, sendMessage, reconnectNow };
}
