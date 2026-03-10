import { memo, useCallback } from "react";
import { Handle, Position, NodeResizer, type NodeProps, type Node } from "@xyflow/react";
import { Lock, Unlock } from "lucide-react";
import { Button } from "@/components/ui/button";

export interface GroupNodeData {
  title?: string;
  is_locked?: boolean;
  onToggleLock?: (nodeId: string, newLocked: boolean) => void;
  _dropTarget?: boolean;
  [key: string]: unknown;
}

export type GroupNodeType = Node<GroupNodeData, "group">;

function GroupNodeComponent({ data, id }: NodeProps<GroupNodeType>) {
  const { title, is_locked, onToggleLock, _dropTarget } = data;

  const handleToggleLock = useCallback(() => {
    onToggleLock?.(id, !is_locked);
  }, [id, is_locked, onToggleLock]);

  return (
    <div
      className="relative h-full w-full rounded-lg"
      style={{
        border: _dropTarget
          ? "2px solid var(--primary)"
          : "2px dashed var(--border-strong)",
        backgroundColor: _dropTarget
          ? "color-mix(in srgb, var(--primary) 10%, transparent)"
          : "color-mix(in srgb, var(--muted) 30%, transparent)",
        transition: "border-color 150ms, background-color 150ms",
      }}
      data-testid="group-node"
      data-drop-target={_dropTarget ? "true" : undefined}
    >
      <NodeResizer
        minWidth={200}
        minHeight={150}
        lineClassName="!border-transparent"
        handleClassName="!h-2.5 !w-2.5 !rounded-sm !border-2 !border-border"
        isVisible={!is_locked}
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

      {/* Lock toggle button */}
      <div className="absolute bottom-1 right-1">
        <Button
          variant="ghost"
          size="icon-sm"
          className="h-6 w-6"
          onClick={handleToggleLock}
          aria-label={is_locked ? "Unlock node" : "Lock node"}
          data-testid="lock-toggle"
        >
          {is_locked ? (
            <Lock className="h-3.5 w-3.5 text-muted-foreground" data-testid="lock-icon" />
          ) : (
            <Unlock className="h-3.5 w-3.5 text-muted-foreground" data-testid="unlock-icon" />
          )}
        </Button>
      </div>

      <Handle type="source" position={Position.Bottom} className="!bg-border" />
    </div>
  );
}

export const GroupNode = memo(GroupNodeComponent);
