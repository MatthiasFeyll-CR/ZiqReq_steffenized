import { useCallback, useMemo } from "react";
import {
  ReactFlow,
  Background,
  BackgroundVariant,
  MiniMap,
  Controls,
  MarkerType,
  useNodesState,
  useEdgesState,
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

export function BoardCanvas() {
  const [nodes, setNodes, onNodesChange] = useNodesState(defaultNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(defaultEdges);

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
    setNodes((nds) => nds.filter((n) => !n.selected));
    setEdges((eds) => eds.filter((e) => !e.selected));
  }, [setNodes, setEdges]);

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
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
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
