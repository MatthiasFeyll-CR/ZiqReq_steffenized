import { memo } from "react";
import { Handle, Position, NodeResizer, type NodeProps, type Node } from "@xyflow/react";

export interface GroupNodeData {
  title?: string;
  [key: string]: unknown;
}

export type GroupNodeType = Node<GroupNodeData, "group">;

function GroupNodeComponent({ data }: NodeProps<GroupNodeType>) {
  const { title } = data;

  return (
    <div
      className="relative h-full w-full rounded-lg"
      style={{
        border: "2px dashed var(--border-strong)",
        backgroundColor: "color-mix(in srgb, var(--muted) 30%, transparent)",
      }}
      data-testid="group-node"
    >
      <NodeResizer
        minWidth={200}
        minHeight={150}
        lineClassName="!border-transparent"
        handleClassName="!h-2.5 !w-2.5 !rounded-sm !border-2 !border-border"
      />

      <Handle type="target" position={Position.Top} className="!bg-border" />

      {/* Label badge */}
      {title && (
        <div className="absolute left-2 top-2">
          <span
            className="rounded bg-muted px-2 py-0.5 text-xs font-medium"
            data-testid="group-label"
          >
            {title}
          </span>
        </div>
      )}

      <Handle type="source" position={Position.Bottom} className="!bg-border" />
    </div>
  );
}

export const GroupNode = memo(GroupNodeComponent);
