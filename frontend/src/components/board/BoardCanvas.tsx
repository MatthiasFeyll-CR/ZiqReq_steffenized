import { useCallback, useMemo } from "react";
import {
  ReactFlow,
  Background,
  BackgroundVariant,
  MiniMap,
  Controls,
  useNodesState,
  useEdgesState,
  type OnConnect,
  type Node,
  type Edge,
  type NodeTypes,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { BoxNode } from "./BoxNode";
import { GroupNode } from "./GroupNode";

const MIN_ZOOM = 0.25;
const MAX_ZOOM = 2;
const GRID_GAP = 20;

const nodeTypes: NodeTypes = {
  box: BoxNode,
  group: GroupNode,
};

const defaultNodes: Node[] = [];
const defaultEdges: Edge[] = [];

export function BoardCanvas() {
  const [nodes, , onNodesChange] = useNodesState(defaultNodes);
  const [edges, , onEdgesChange] = useEdgesState(defaultEdges);

  const onConnect: OnConnect = useCallback(() => {
    // Connection handling will be implemented in later stories
  }, []);

  const proOptions = useMemo(() => ({ hideAttribution: true }), []);

  return (
    <div className="h-full w-full" data-testid="board-canvas">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
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
  );
}
