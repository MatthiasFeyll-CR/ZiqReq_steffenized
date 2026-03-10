import { memo, useCallback } from "react";
import { Handle, Position, type NodeProps, type Node } from "@xyflow/react";
import { Pin, Bot, Lock } from "lucide-react";
import { Button } from "@/components/ui/button";

export interface BoxNodeData {
  title?: string;
  body?: string;
  created_by?: "user" | "ai";
  is_locked?: boolean;
  nodeId?: string;
  [key: string]: unknown;
}

export type BoxNodeType = Node<BoxNodeData, "box">;

function BoxNodeComponent({ data, id }: NodeProps<BoxNodeType>) {
  const { title, body, created_by, is_locked } = data;

  const handleReference = useCallback(() => {
    const nodeId = data.nodeId ?? id;
    window.dispatchEvent(
      new CustomEvent("board:reference", { detail: `@board[${nodeId}]` }),
    );
  }, [data.nodeId, id]);

  const bullets = body
    ? body
        .split("\n")
        .map((line) => line.trim())
        .filter(Boolean)
    : [];

  return (
    <div
      className="relative rounded-md border border-border bg-card shadow-sm"
      style={{ minWidth: 192, maxWidth: 320 }}
      data-testid="box-node"
    >
      <Handle type="target" position={Position.Top} className="!bg-border" />

      {/* Title bar */}
      <div className="flex items-center gap-1 border-b px-3 py-2">
        {created_by === "ai" && (
          <Bot className="h-3.5 w-3.5 shrink-0 text-muted-foreground" data-testid="ai-badge" />
        )}
        <span className="flex-1 truncate text-sm font-medium">{title}</span>
        <Button
          variant="ghost"
          size="icon-sm"
          className="h-6 w-6 shrink-0"
          onClick={handleReference}
          aria-label="Reference node"
          data-testid="reference-button"
        >
          <Pin className="h-3.5 w-3.5" />
        </Button>
      </div>

      {/* Body */}
      {bullets.length > 0 && (
        <ul className="px-3 py-2 text-sm list-disc list-inside space-y-0.5">
          {bullets.map((bullet, i) => (
            <li key={i}>{bullet}</li>
          ))}
        </ul>
      )}

      {/* Lock icon */}
      {is_locked && (
        <div className="absolute bottom-1 right-1" data-testid="lock-icon">
          <Lock className="h-3.5 w-3.5 text-muted-foreground" />
        </div>
      )}

      <Handle type="source" position={Position.Bottom} className="!bg-border" />
    </div>
  );
}

export const BoxNode = memo(BoxNodeComponent);
