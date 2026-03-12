import { memo, useCallback, useState, useRef, useEffect } from "react";
import { Handle, Position, NodeResizer, type NodeProps, type Node } from "@xyflow/react";
import { Lock, Unlock } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { getUserColor } from "@/store/selections-slice";

export interface GroupNodeData {
  title?: string;
  is_locked?: boolean;
  ai_modified_indicator?: boolean;
  onToggleLock?: (nodeId: string, newLocked: boolean) => void;
  onTitleChange?: (nodeId: string, title: string) => void;
  _dropTarget?: boolean;
  [key: string]: unknown;
}

export type GroupNodeType = Node<GroupNodeData, "group">;

function GroupNodeComponent({ data, id }: NodeProps<GroupNodeType>) {
  const { title, is_locked, ai_modified_indicator, onToggleLock, _dropTarget, _selectedBy } = data;
  const selectedBy = _selectedBy as { user_id: string; display_name: string } | null;
  const { t } = useTranslation();

  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState(title ?? "");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => setValue(title ?? ""), [title]);

  useEffect(() => {
    if (editing && inputRef.current) inputRef.current.focus();
  }, [editing]);

  const handleToggleLock = useCallback(() => {
    onToggleLock?.(id, !is_locked);
  }, [id, is_locked, onToggleLock]);

  const handleDoubleClick = useCallback(() => {
    if (is_locked) return;
    setEditing(true);
  }, [is_locked]);

  const handleBlur = useCallback(() => {
    setEditing(false);
    if (data.onTitleChange && value !== title) {
      data.onTitleChange(id, value);
    }
  }, [data, id, value, title]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter") {
        e.preventDefault();
        (e.target as HTMLInputElement).blur();
      } else if (e.key === "Escape") {
        setValue(title ?? "");
        setEditing(false);
      }
    },
    [title],
  );

  const selectionColor = selectedBy ? getUserColor(selectedBy.user_id) : null;

  return (
    <div
      className="relative h-full w-full rounded-lg"
      style={{
        border: _dropTarget
          ? "2px solid var(--primary)"
          : selectedBy
            ? `2px solid ${selectionColor}`
            : "2px dashed var(--border-strong)",
        backgroundColor: _dropTarget
          ? "color-mix(in srgb, var(--primary) 10%, transparent)"
          : "color-mix(in srgb, var(--muted) 30%, transparent)",
        transition: "border-color 150ms, background-color 150ms",
      }}
      data-testid="group-node"
      data-drop-target={_dropTarget ? "true" : undefined}
    >
      {selectedBy && selectionColor && (
        <div
          className="absolute -top-5 left-0 z-10 whitespace-nowrap rounded px-1 py-0.5 text-[10px] font-medium leading-none text-white"
          style={{ backgroundColor: selectionColor }}
          data-testid="selection-user-label"
        >
          {selectedBy.display_name}
        </div>
      )}
      {ai_modified_indicator && (
        <span
          className="absolute -left-1 -top-1 z-10 h-2 w-2 rounded-full bg-amber-400 motion-safe:animate-pulse"
          data-testid="ai-modified-dot"
        />
      )}

      <NodeResizer
        minWidth={200}
        minHeight={150}
        lineClassName="!border-transparent"
        handleClassName="!h-2.5 !w-2.5 !rounded-sm !border-2 !border-border"
        isVisible={!is_locked}
      />

      <Handle type="target" position={Position.Top} className="!bg-border" />

      {/* Label badge */}
      <div className="absolute left-2 top-2">
        {editing ? (
          <input
            ref={inputRef}
            className="rounded bg-muted px-2 py-0.5 text-xs font-medium outline-none"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onBlur={handleBlur}
            onKeyDown={handleKeyDown}
            data-testid="group-title-input"
          />
        ) : (
          <span
            className="rounded bg-muted px-2 py-0.5 text-xs font-medium cursor-text"
            onDoubleClick={handleDoubleClick}
            data-testid="group-label"
          >
            {value || (is_locked ? "\u00A0" : "Double-click to name")}
          </span>
        )}
      </div>

      {/* Lock toggle button */}
      <div className="absolute bottom-1 right-1">
        <Button
          variant="ghost"
          size="icon-sm"
          className="h-6 w-6"
          onClick={handleToggleLock}
          aria-label={is_locked ? t("board.unlockNode") : t("board.lockNode")}
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
