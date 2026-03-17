import { useEffect, useRef, useCallback } from "react";
import { useSelector, useDispatch } from "react-redux";
import { useQueryClient } from "@tanstack/react-query";
import {
  selectConnectionState,
  selectIsIdleDisconnected,
  setIdleDisconnected,
} from "@/store/websocket-slice";
import { useWsReconnect } from "@/app/providers";
import { fetchProject, type Project } from "@/api/projects";

interface UseProjectSyncOptions {
  projectId: string;
  onProjectUpdate: (project: Project) => void;
}

/**
 * Handles return-from-idle reconnection and state sync.
 * - Listens for mouse movement when idle-disconnected → triggers reconnect
 * - On successful reconnect after idle disconnect → refetches project state and invalidates queries
 */
export function useProjectSync({ projectId, onProjectUpdate }: UseProjectSyncOptions) {
  const connectionState = useSelector(selectConnectionState);
  const isIdleDisconnected = useSelector(selectIsIdleDisconnected);
  const reconnectNow = useWsReconnect();
  const dispatch = useDispatch();
  const queryClient = useQueryClient();

  const wasIdleDisconnectedRef = useRef(false);
  const onProjectUpdateRef = useRef(onProjectUpdate);
  onProjectUpdateRef.current = onProjectUpdate;
  const projectIdRef = useRef(projectId);
  projectIdRef.current = projectId;

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
      const updatedProject = await fetchProject(projectIdRef.current);
      onProjectUpdateRef.current(updatedProject);
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
