import { useEffect, useRef, useCallback } from "react";
import { useSelector, useDispatch } from "react-redux";
import { useQueryClient } from "@tanstack/react-query";
import {
  selectConnectionState,
  selectIsIdleDisconnected,
  setIdleDisconnected,
} from "@/store/websocket-slice";
import { useWsReconnect } from "@/app/providers";
import { fetchIdea, type Idea } from "@/api/ideas";

interface UseIdeaSyncOptions {
  ideaId: string;
  onIdeaUpdate: (idea: Idea) => void;
}

/**
 * Handles return-from-idle reconnection and state sync.
 * - Listens for mouse movement when idle-disconnected → triggers reconnect
 * - On successful reconnect after idle disconnect → refetches idea state and invalidates queries
 */
export function useIdeaSync({ ideaId, onIdeaUpdate }: UseIdeaSyncOptions) {
  const connectionState = useSelector(selectConnectionState);
  const isIdleDisconnected = useSelector(selectIsIdleDisconnected);
  const reconnectNow = useWsReconnect();
  const dispatch = useDispatch();
  const queryClient = useQueryClient();

  const wasIdleDisconnectedRef = useRef(false);
  const onIdeaUpdateRef = useRef(onIdeaUpdate);
  onIdeaUpdateRef.current = onIdeaUpdate;
  const ideaIdRef = useRef(ideaId);
  ideaIdRef.current = ideaId;

  // Track when we were idle-disconnected so we know to sync on reconnect
  useEffect(() => {
    if (isIdleDisconnected) {
      wasIdleDisconnectedRef.current = true;
    }
  }, [isIdleDisconnected]);

  // Mouse move listener: reconnect when idle-disconnected
  useEffect(() => {
    if (!isIdleDisconnected) return;

    const handleMouseMove = () => {
      dispatch(setIdleDisconnected(false));
      reconnectNow();
    };

    document.addEventListener("mousemove", handleMouseMove);
    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
    };
  }, [isIdleDisconnected, reconnectNow, dispatch]);

  // State sync: when connection comes back online after idle disconnect
  const syncState = useCallback(async () => {
    try {
      const updatedIdea = await fetchIdea(ideaIdRef.current);
      onIdeaUpdateRef.current(updatedIdea);
    } catch {
      // Silently ignore sync errors — data will refresh on next interaction
    }
    // Invalidate all queries to ensure fresh data across the app
    queryClient.invalidateQueries();
  }, [queryClient]);

  useEffect(() => {
    if (connectionState === "online" && wasIdleDisconnectedRef.current) {
      wasIdleDisconnectedRef.current = false;
      syncState();
    }
  }, [connectionState, syncState]);
}
