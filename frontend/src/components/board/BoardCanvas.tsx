import { useCallback, useMemo, useRef } from "react";
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
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { BoxNode } from "./BoxNode";
import { GroupNode } from "./GroupNode";
import { FreeTextNode } from "./FreeTextNode";
import { ConnectionEdge } from "./ConnectionEdge";
import { BoardToolbar } from "./BoardToolbar";
import { updateBoardNode } from "@/api/board";

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

interface BoardCanvasProps {
  ideaId?: string;
}

export function BoardCanvas({ ideaId }: BoardCanvasProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(defaultNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(defaultEdges);
  const dropTargetIdRef = useRef<string | null>(null);
  const { getInternalNode } = useReactFlow();

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
      const id = crypto.randomUUID();
      const newNode: Node = {
        id,
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
    },
    [setNodes],
  );

  const handleDeleteSelected = useCallback(() => {
    setNodes((nds) => nds.filter((n) => !n.selected || n.data?.is_locked));
    setEdges((eds) => eds.filter((e) => !e.selected));
  }, [setNodes, setEdges]);

  const handleToggleLock = useCallback(
    (nodeId: string, newLocked: boolean) => {
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
    [ideaId, setNodes],
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
        // Just persist position (same as US-001)
        updateBoardNode(ideaId, node.id, {
          position_x: node.position.x,
          position_y: node.position.y,
        }).catch(() => {
          // Position will be retried on next drag or sync
        });
      }
    },
    [ideaId, setNodes, getAbsolutePosition, getNodeInfos],
  );

  // Inject onToggleLock into node data and set draggable based on is_locked
  const processedNodes = useMemo(
    () =>
      nodes.map((n) => ({
        ...n,
        draggable: !n.data?.is_locked,
        data: { ...n.data, onToggleLock: handleToggleLock },
      })),
    [nodes, handleToggleLock],
  );

  const proOptions = useMemo(() => ({ hideAttribution: true }), []);

  return (
    <div className="flex flex-col h-full w-full" data-testid="board-canvas">
      <BoardToolbar
        selectedCount={selectedCount}
        onAddBox={handleAddBox}
        onDeleteSelected={handleDeleteSelected}
      />
      <div className="flex-1 min-h-0">
        <ReactFlow
          nodes={processedNodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeDrag={onNodeDrag}
          onNodeDragStop={onNodeDragStop}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          defaultEdgeOptions={defaultEdgeOptions}
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
