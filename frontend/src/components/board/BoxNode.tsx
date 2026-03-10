import { memo, useCallback } from "react";
import { Handle, Position, type NodeProps, type Node } from "@xyflow/react";
import { Pin, Bot, Lock, Unlock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { UserSelectionHighlight } from "./UserSelectionHighlight";

export interface BoxNodeData {
  title?: string;
  body?: string;
  created_by?: "user" | "ai";
  is_locked?: boolean;
  ai_modified_indicator?: boolean;
  nodeId?: string;
  onToggleLock?: (nodeId: string, newLocked: boolean) => void;
  [key: string]: unknown;
}

export type BoxNodeType = Node<BoxNodeData, "box">;

function BoxNodeComponent({ data, id }: NodeProps<BoxNodeType>) {
  const { title, body, created_by, is_locked, ai_modified_indicator, onToggleLock, _selectedBy } = data;
  const selectedBy = _selectedBy as { user_id: string; display_name: string } | null;

  const handleReference = useCallback(() => {
    const nodeId = data.nodeId ?? id;
    window.dispatchEvent(
      new CustomEvent("board:reference", { detail: `@board[${nodeId}]` }),
    );
  }, [data.nodeId, id]);

  const handleToggleLock = useCallback(() => {
    onToggleLock?.(id, !is_locked);
  }, [id, is_locked, onToggleLock]);

  const bullets = body
    ? body
        .split("\n")
        .map((line) => line.trim())
        .filter(Boolean)
    : [];

  return (
    <UserSelectionHighlight selectedBy={selectedBy}>
      <div
        className="relative rounded-md border border-border bg-card shadow-sm"
        style={{ minWidth: 192, maxWidth: 320 }}
        data-testid="box-node"
      >
        {ai_modified_indicator && (
          <span
            className="absolute -left-1 -top-1 h-2 w-2 rounded-full bg-amber-400 motion-safe:animate-pulse"
            data-testid="ai-modified-dot"
          />
        )}

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
    </UserSelectionHighlight>
  );
}

export const BoxNode = memo(BoxNodeComponent);
