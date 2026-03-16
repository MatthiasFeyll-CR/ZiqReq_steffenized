import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  ReactFlow,
  Background,
  BackgroundVariant,
  MiniMap,
  Controls,
  MarkerType,
  useNodesState,
  useEdgesState,
  useReactFlow,
  type OnConnect,
  type Node,
  type Edge,
  type NodeTypes,
  type EdgeTypes,
  type NodeChange,
  type EdgeChange,
  SelectionMode,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useSelector } from "react-redux";
import { BoxNode } from "./BoxNode";
import { GroupNode } from "./GroupNode";
import { FreeTextNode } from "./FreeTextNode";
import { ConnectionEdge } from "./ConnectionEdge";
import { BoardToolbar } from "./BoardToolbar";
import { AIProcessingOverlay } from "@/components/workspace/AIProcessingOverlay";
import { consumeAiProcessing } from "@/lib/ai-processing-flag";
import {
  updateBoardNode,
  createBoardNode,
  fetchBoardNodes,
  fetchBoardConnections,
  type BoardNode as ApiBoardNode,
  type BoardConnection as ApiBoardConnection,
} from "@/api/board";
import { useBoardUndo } from "@/hooks/use-board-undo";
import { useWsSend } from "@/app/providers";
import { useAuth } from "@/hooks/use-auth";
import { selectIdeaSelections } from "@/store/selections-slice";
import type { RootState } from "@/store";

const MIN_ZOOM = 0.25;
const MAX_ZOOM = 2;
const GRID_GAP = 20;

const nodeTypes: NodeTypes = {
  box: BoxNode,
  group: GroupNode,
  free_text: FreeTextNode,
};

const edgeTypes: EdgeTypes = {
  connection: ConnectionEdge,
};

const defaultEdgeOptions = {
  type: "connection" as const,
  markerEnd: { type: MarkerType.ArrowClosed, color: "gray" },
};

const defaultNodes: Node[] = [];
const defaultEdges: Edge[] = [];

interface NodeInfo {
  id: string;
  type?: string;
  parentId?: string;
  position: { x: number; y: number };
  absX: number;
  absY: number;
  width: number;
  height: number;
}

/**
 * Find the group node that contains the given absolute position.
 * Returns the smallest (most deeply nested) matching group,
 * excluding the dragged node itself and any of its descendants.
 */
function findParentGroup(
  nodeInfos: NodeInfo[],
  draggedNodeId: string,
  absoluteX: number,
  absoluteY: number,
): NodeInfo | null {
  const draggedDescendants = new Set<string>();
  function collectDescendants(parentId: string) {
    for (const n of nodeInfos) {
      if (n.parentId === parentId) {
        draggedDescendants.add(n.id);
        collectDescendants(n.id);
      }
    }
  }
  if (nodeInfos.find((n) => n.id === draggedNodeId)?.type === "group") {
    collectDescendants(draggedNodeId);
  }

  let bestGroup: NodeInfo | null = null;
  let bestArea = Infinity;

  for (const n of nodeInfos) {
    if (n.type !== "group") continue;
    if (n.id === draggedNodeId) continue;
    if (draggedDescendants.has(n.id)) continue;

    if (
      absoluteX >= n.absX &&
      absoluteX <= n.absX + n.width &&
      absoluteY >= n.absY &&
      absoluteY <= n.absY + n.height
    ) {
      const area = n.width * n.height;
      if (area < bestArea) {
        bestArea = area;
        bestGroup = n;
      }
    }
  }

  return bestGroup;
}

function apiNodeToReactFlow(n: ApiBoardNode): Node {
  return {
    id: n.id,
    type: n.node_type,
    position: { x: n.position_x, y: n.position_y },
    ...(n.parent_id ? { parentId: n.parent_id, expandParent: true } : {}),
    ...(n.width != null ? { width: n.width } : {}),
    ...(n.height != null ? { height: n.height } : {}),
    data: {
      title: n.title ?? "",
      body: n.body ?? "",
      created_by: n.created_by,
      is_locked: n.is_locked,
      ai_modified_indicator: n.ai_modified_indicator,
    },
  };
}

function apiConnectionToReactFlow(c: ApiBoardConnection): Edge {
  return {
    id: c.id,
    source: c.source_node_id,
    target: c.target_node_id,
    type: "connection",
    label: c.label || undefined,
  };
}

interface BoardCanvasProps {
  ideaId?: string;
  disabled?: boolean;
  readOnly?: boolean;
}

export function BoardCanvas({ ideaId, disabled, readOnly }: BoardCanvasProps) {
  const [nodes, setNodes, onNodesChangeRaw] = useNodesState(defaultNodes);
  const [edges, setEdges, onEdgesChangeRaw] = useEdgesState(defaultEdges);
  const dropTargetIdRef = useRef<string | null>(null);
  const [aiProcessing, setAiProcessing] = useState(
    () => !!ideaId && consumeAiProcessing(ideaId),
  );

  // When disabled, only allow selection changes (for visual highlighting) — block
  // position, dimension, add, remove, and reset changes so the board is truly frozen.
  const onNodesChange = useCallback(
    (changes: NodeChange[]) => {
      if (disabled) {
        const allowed = changes.filter((c) => c.type === "select");
        if (allowed.length > 0) onNodesChangeRaw(allowed);
        return;
      }
      onNodesChangeRaw(changes);
    },
    [disabled, onNodesChangeRaw],
  );

  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => {
      if (disabled) {
        const allowed = changes.filter((c) => c.type === "select");
        if (allowed.length > 0) onEdgesChangeRaw(allowed);
        return;
      }
      onEdgesChangeRaw(changes);
    },
    [disabled, onEdgesChangeRaw],
  );
  const { getInternalNode } = useReactFlow();
  const { push: pushUndoAction, handleUndo, handleRedo, canUndo, canRedo, undoTop, redoTop } = useBoardUndo(ideaId);
  const wsSend = useWsSend();
  const { user } = useAuth();
  const selections = useSelector((state: RootState) =>
    ideaId ? selectIdeaSelections(ideaId)(state) : [],
  );
  const selectedNodeRef = useRef<string | null>(null);

  const getNodeInfos = useCallback((): NodeInfo[] => {
    return nodes.map((n) => {
      const internal = getInternalNode(n.id);
      return {
        id: n.id,
        type: n.type,
        parentId: n.parentId,
        position: n.position,
        absX: internal?.internals.positionAbsolute.x ?? n.position.x,
        absY: internal?.internals.positionAbsolute.y ?? n.position.y,
        width: internal?.measured.width ?? n.width ?? 200,
        height: internal?.measured.height ?? n.height ?? 150,
      };
    });
  }, [nodes, getInternalNode]);

  const getAbsolutePosition = useCallback(
    (node: Node): { x: number; y: number } => {
      const internal = getInternalNode(node.id);
      return {
        x: internal?.internals.positionAbsolute.x ?? node.position.x,
        y: internal?.internals.positionAbsolute.y ?? node.position.y,
      };
    },
    [getInternalNode],
  );

  const onConnect: OnConnect = useCallback(() => {
    // Connection handling will be implemented in later stories
  }, []);

  const selectedCount = useMemo(
    () =>
      nodes.filter((n) => n.selected).length +
      edges.filter((e) => e.selected).length,
    [nodes, edges],
  );

  const handleAddBox = useCallback(
    (position: { x: number; y: number }) => {
      const tempId = crypto.randomUUID();
      const newNode: Node = {
        id: tempId,
        type: "box",
        position,
        data: {
          title: "New Box",
          body: "",
          created_by: "user",
          is_locked: false,
        },
      };
      setNodes((nds) => [...nds, newNode]);

      if (ideaId) {
        createBoardNode(ideaId, {
          node_type: "box",
          title: "New Box",
          body: "",
          position_x: position.x,
          position_y: position.y,
          created_by: "user",
        }).then((saved) => {
          // Replace temp ID with server-assigned ID
          setNodes((nds) =>
            nds.map((n) => (n.id === tempId ? { ...n, id: saved.id } : n)),
          );
        }).catch(() => {
          // Remove the node if persist failed
          setNodes((nds) => nds.filter((n) => n.id !== tempId));
        });
      }
    },
    [ideaId, setNodes],
  );

  const handleDeleteSelected = useCallback(() => {
    setNodes((nds) => nds.filter((n) => !n.selected || n.data?.is_locked));
    setEdges((eds) => eds.filter((e) => !e.selected));
  }, [setNodes, setEdges]);

  const handleToggleLock = useCallback(
    (nodeId: string, newLocked: boolean) => {
      pushUndoAction({
        type: "toggle_lock",
        nodeId,
        data: { is_locked: newLocked },
        previousState: { is_locked: !newLocked },
        source: "user",
      });
      setNodes((nds) =>
        nds.map((n) =>
          n.id === nodeId
            ? { ...n, data: { ...n.data, is_locked: newLocked } }
            : n,
        ),
      );
      if (ideaId) {
        updateBoardNode(ideaId, nodeId, { is_locked: newLocked }).catch(() => {
          // Will be retried on next toggle or sync
        });
      }
    },
    [ideaId, setNodes, pushUndoAction],
  );

  const onNodeDrag = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      const abs = getAbsolutePosition(node);
      const nodeInfos = getNodeInfos();

      setNodes((nds) => {
        const group = findParentGroup(nodeInfos, node.id, abs.x, abs.y);
        const newTargetId = group?.id ?? null;
        const prevTargetId = dropTargetIdRef.current;

        if (newTargetId === prevTargetId) return nds;
        dropTargetIdRef.current = newTargetId;

        return nds.map((n) => {
          if (n.type !== "group") return n;
          const isTarget = n.id === newTargetId;
          const wasTarget = n.id === prevTargetId;
          if (!isTarget && !wasTarget) return n;
          return {
            ...n,
            data: { ...n.data, _dropTarget: isTarget },
          };
        });
      });
    },
    [setNodes, getAbsolutePosition, getNodeInfos],
  );

  const onNodeDragStop = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      // Clear drop target highlight
      dropTargetIdRef.current = null;
      setNodes((nds) =>
        nds.map((n) =>
          n.type === "group" && n.data._dropTarget
            ? { ...n, data: { ...n.data, _dropTarget: false } }
            : n,
        ),
      );

      if (!ideaId) return;

      const abs = getAbsolutePosition(node);
      const nodeInfos = getNodeInfos();

      const oldParentId = node.parentId ?? null;
      const targetGroup = findParentGroup(nodeInfos, node.id, abs.x, abs.y);
      const newParentId = targetGroup?.id ?? null;

      const parentChanged = oldParentId !== newParentId;

      if (parentChanged) {
        // Recalculate position relative to new parent
        let relX = abs.x;
        let relY = abs.y;
        if (targetGroup) {
          relX = abs.x - targetGroup.absX;
          relY = abs.y - targetGroup.absY;
        }

        pushUndoAction({
          type: "move",
          nodeId: node.id,
          data: { position_x: relX, position_y: relY, parent_id: newParentId },
          previousState: { position_x: node.position.x, position_y: node.position.y, parent_id: oldParentId },
          source: "user",
        });

        // Update node in React Flow state
        setNodes((nds) =>
          nds.map((n) =>
            n.id === node.id
              ? {
                  ...n,
                  parentId: newParentId ?? undefined,
                  position: { x: relX, y: relY },
                  expandParent: newParentId ? true : undefined,
                }
              : n,
          ),
        );

        // Persist parent_id + position
        updateBoardNode(ideaId, node.id, {
          parent_id: newParentId,
          position_x: relX,
          position_y: relY,
        }).catch(() => {
          // Will be retried on next drag or sync
        });
      } else {
        // Save previous position before it's updated
        const prevNode = nodes.find((n) => n.id === node.id);
        const prevX = prevNode?.position.x ?? 0;
        const prevY = prevNode?.position.y ?? 0;

        pushUndoAction({
          type: "move",
          nodeId: node.id,
          data: { position_x: node.position.x, position_y: node.position.y },
          previousState: { position_x: prevX, position_y: prevY },
          source: "user",
        });

        // Just persist position (same as US-001)
        updateBoardNode(ideaId, node.id, {
          position_x: node.position.x,
          position_y: node.position.y,
        }).catch(() => {
          // Position will be retried on next drag or sync
        });
      }
    },
    [ideaId, setNodes, getAbsolutePosition, getNodeInfos, pushUndoAction, nodes],
  );

  const onNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      // Send selection event via WebSocket
      if (ideaId && user) {
        selectedNodeRef.current = node.id;
        wsSend({
          type: "board_selection",
          idea_id: ideaId,
          payload: {
            node_id: node.id,
            user: { id: user.id, display_name: user.display_name },
          },
        });
      }

      if (!node.data?.ai_modified_indicator) return;
      // Clear indicator locally
      setNodes((nds) =>
        nds.map((n) =>
          n.id === node.id
            ? { ...n, data: { ...n.data, ai_modified_indicator: false } }
            : n,
        ),
      );
      // Persist to backend
      if (ideaId) {
        updateBoardNode(ideaId, node.id, { ai_modified_indicator: false }).catch(() => {
          // Will be retried on next interaction
        });
      }
    },
    [ideaId, setNodes, wsSend, user],
  );

  const onPaneClick = useCallback(() => {
    if (ideaId && user && selectedNodeRef.current !== null) {
      selectedNodeRef.current = null;
      wsSend({
        type: "board_selection",
        idea_id: ideaId,
        payload: {
          node_id: null,
          user: { id: user.id, display_name: user.display_name },
        },
      });
    }
  }, [ideaId, wsSend, user]);

  const handleTitleChange = useCallback(
    (nodeId: string, newTitle: string) => {
      setNodes((nds) =>
        nds.map((n) =>
          n.id === nodeId ? { ...n, data: { ...n.data, title: newTitle } } : n,
        ),
      );
      if (ideaId) {
        updateBoardNode(ideaId, nodeId, { title: newTitle }).catch(() => {});
      }
    },
    [ideaId, setNodes],
  );

  const handleBodyChange = useCallback(
    (nodeId: string, newBody: string) => {
      setNodes((nds) =>
        nds.map((n) =>
          n.id === nodeId ? { ...n, data: { ...n.data, body: newBody } } : n,
        ),
      );
      if (ideaId) {
        updateBoardNode(ideaId, nodeId, { body: newBody }).catch(() => {});
      }
    },
    [ideaId, setNodes],
  );

  // Inject callbacks and selection info into node data, set draggable based on is_locked
  const processedNodes = useMemo(
    () =>
      nodes.map((n) => {
        const sel = selections.find(
          (s) => s.node_id === n.id && s.user_id !== user?.id,
        );
        return {
          ...n,
          draggable: !n.data?.is_locked && !disabled,
          data: {
            ...n.data,
            onToggleLock: handleToggleLock,
            onTitleChange: handleTitleChange,
            onBodyChange: handleBodyChange,
            _selectedBy: sel ?? null,
          },
        };
      }),
    [nodes, handleToggleLock, handleTitleChange, handleBodyChange, selections, user?.id, disabled],
  );

  // Load initial board data
  useEffect(() => {
    if (!ideaId) return;
    let cancelled = false;

    Promise.all([fetchBoardNodes(ideaId), fetchBoardConnections(ideaId)]).then(
      ([apiNodes, apiConnections]) => {
        if (cancelled) return;
        // Sort so parents come before children for ReactFlow
        const sorted = [...apiNodes].sort((a, b) => {
          if (a.parent_id && !b.parent_id) return 1;
          if (!a.parent_id && b.parent_id) return -1;
          return 0;
        });
        setNodes(sorted.map(apiNodeToReactFlow));
        setEdges(apiConnections.map(apiConnectionToReactFlow));
      },
    );

    return () => {
      cancelled = true;
    };
  }, [ideaId, setNodes, setEdges]);

  // Listen for real-time board updates via WebSocket
  useEffect(() => {
    if (!ideaId) return;

    const handleBoardUpdate = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail.idea_id !== ideaId) return;

      const mutations: Array<Record<string, unknown>> =
        detail.mutations?.length > 0
          ? detail.mutations
          : detail.mutation && Object.keys(detail.mutation).length > 0
            ? [detail.mutation]
            : [];

      for (const mut of mutations) {
        const action = mut.action as string;

        if (action === "create_node") {
          const newNode: Node = {
            id: mut.node_id as string,
            type: (mut.node_type as string) || "box",
            position: {
              x: (mut.position_x as number) ?? 0,
              y: (mut.position_y as number) ?? 0,
            },
            ...(mut.parent_id
              ? { parentId: mut.parent_id as string, expandParent: true }
              : {}),
            data: {
              title: (mut.title as string) ?? "",
              body: (mut.body as string) ?? "",
              created_by: "ai",
              is_locked: false,
              ai_modified_indicator: false,
            },
          };
          setNodes((nds) => {
            if (nds.some((n) => n.id === newNode.id)) return nds;
            return [...nds, newNode];
          });
        } else if (action === "update_node") {
          setNodes((nds) =>
            nds.map((n) => {
              if (n.id !== (mut.node_id as string)) return n;
              const updated = { ...n, data: { ...n.data } };
              if (mut.title != null) updated.data.title = mut.title as string;
              if (mut.body != null) updated.data.body = mut.body as string;
              if (mut.is_locked != null)
                updated.data.is_locked = mut.is_locked as boolean;
              if (mut.position_x != null || mut.position_y != null) {
                updated.position = {
                  x: (mut.position_x as number) ?? n.position.x,
                  y: (mut.position_y as number) ?? n.position.y,
                };
              }
              if (mut.width != null) updated.width = mut.width as number;
              if (mut.height != null) updated.height = mut.height as number;
              if (mut.parent_id !== undefined) {
                updated.parentId = (mut.parent_id as string) || undefined;
                updated.expandParent = !!mut.parent_id;
              }
              return updated;
            }),
          );
        } else if (action === "delete_node") {
          setNodes((nds) => nds.filter((n) => n.id !== (mut.node_id as string)));
        } else if (action === "move_node") {
          setNodes((nds) =>
            nds.map((n) => {
              if (n.id !== (mut.node_id as string)) return n;
              return {
                ...n,
                position: {
                  x: (mut.position_x as number) ?? n.position.x,
                  y: (mut.position_y as number) ?? n.position.y,
                },
                ...(mut.new_parent_id !== undefined
                  ? {
                      parentId: (mut.new_parent_id as string) || undefined,
                      expandParent: !!mut.new_parent_id,
                    }
                  : {}),
              };
            }),
          );
        } else if (action === "create_connection") {
          const newEdge: Edge = {
            id: (mut.connection_id as string) ?? crypto.randomUUID(),
            source: mut.source_node_id as string,
            target: mut.target_node_id as string,
            type: "connection",
            label: (mut.label as string) || undefined,
          };
          setEdges((eds) => {
            if (eds.some((e) => e.id === newEdge.id)) return eds;
            return [...eds, newEdge];
          });
        } else if (action === "delete_connection") {
          setEdges((eds) =>
            eds.filter((e) => e.id !== (mut.connection_id as string)),
          );
        } else if (action === "resize_group") {
          setNodes((nds) =>
            nds.map((n) => {
              if (n.id !== (mut.node_id as string)) return n;
              return {
                ...n,
                width: (mut.width as number) ?? n.width,
                height: (mut.height as number) ?? n.height,
              };
            }),
          );
        }
      }
    };

    window.addEventListener("ws:board_update", handleBoardUpdate);
    return () => window.removeEventListener("ws:board_update", handleBoardUpdate);
  }, [ideaId, setNodes, setEdges]);

  // Track AI processing state to lock the board while AI may modify it
  useEffect(() => {
    if (!ideaId) return;

    const handleAiProcessing = (e: Event) => {
      const { idea_id, state } = (e as CustomEvent).detail;
      if (idea_id !== ideaId) return;
      if (state === "started") {
        setAiProcessing(true);
      } else if (state === "completed" || state === "failed") {
        setAiProcessing(false);
      }
    };

    window.addEventListener("ws:ai_processing", handleAiProcessing);
    return () => window.removeEventListener("ws:ai_processing", handleAiProcessing);
  }, [ideaId]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Delete" || e.key === "Backspace") {
        const tag = (e.target as HTMLElement)?.tagName;
        if (tag === "INPUT" || tag === "TEXTAREA") return;
        handleDeleteSelected();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleDeleteSelected]);

  const proOptions = useMemo(() => ({ hideAttribution: true }), []);

  return (
    <div className="flex flex-col h-full w-full" data-testid="board-canvas">
      {!readOnly && (
        <BoardToolbar
          selectedCount={selectedCount}
          onAddBox={handleAddBox}
          onDeleteSelected={handleDeleteSelected}
          onUndo={handleUndo}
          onRedo={handleRedo}
          canUndo={canUndo}
          canRedo={canRedo}
          undoTopSource={undoTop?.source}
          redoTopSource={redoTop?.source}
        />
      )}
      <div className="relative flex-1 min-h-0">
        {aiProcessing && (
          <AIProcessingOverlay message="AI is updating the board..." />
        )}
        <ReactFlow
          nodes={processedNodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={disabled ? undefined : onConnect}
          onNodeClick={disabled ? undefined : onNodeClick}
          onPaneClick={disabled ? undefined : onPaneClick}
          onNodeDrag={disabled ? undefined : onNodeDrag}
          onNodeDragStop={disabled ? undefined : onNodeDragStop}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          defaultEdgeOptions={defaultEdgeOptions}
          selectionOnDrag={!disabled}
          selectionMode={SelectionMode.Partial}
          selectionKeyCode={disabled ? null : "Control"}
          deleteKeyCode={null}
          nodesDraggable={!disabled}
          nodesConnectable={!disabled}
          elementsSelectable={!disabled}
          minZoom={MIN_ZOOM}
          maxZoom={MAX_ZOOM}
          fitView
          proOptions={proOptions}
        >
          <Background
            variant={BackgroundVariant.Dots}
            gap={GRID_GAP}
            size={1}
            style={{ opacity: 0.2 }}
            color="var(--foreground)"
          />
          <MiniMap
            className="!bottom-2 !right-2 !border !rounded-sm !shadow-sm"
            style={{
              width: 120,
              height: 80,
              backgroundColor: "var(--card)",
            }}
            data-testid="board-minimap"
          />
          <Controls
            className="!bottom-2 !left-2"
            showInteractive={false}
            data-testid="board-zoom-controls"
          />
        </ReactFlow>
      </div>
    </div>
  );
}
