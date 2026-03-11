import { memo, useState, useCallback, useRef, useEffect } from "react";
import { Handle, Position, type NodeProps, type Node } from "@xyflow/react";
import { Lock, Unlock } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { UserSelectionHighlight } from "./UserSelectionHighlight";

export interface FreeTextNodeData {
  body?: string;
  is_locked?: boolean;
  ai_modified_indicator?: boolean;
  onToggleLock?: (nodeId: string, newLocked: boolean) => void;
  onBodyChange?: (nodeId: string, body: string) => void;
  [key: string]: unknown;
}

export type FreeTextNodeType = Node<FreeTextNodeData, "free_text">;

function FreeTextNodeComponent({ data, id }: NodeProps<FreeTextNodeType>) {
  const { body, is_locked, ai_modified_indicator, onToggleLock, _selectedBy } = data;
  const selectedBy = _selectedBy as { user_id: string; display_name: string } | null;
  const { t } = useTranslation();
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState(body ?? "");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    setValue(body ?? "");
  }, [body]);

  useEffect(() => {
    if (editing && textareaRef.current) {
      textareaRef.current.focus();
      autoGrow(textareaRef.current);
    }
  }, [editing]);

  const autoGrow = useCallback((el: HTMLTextAreaElement) => {
    el.style.height = "auto";
    el.style.height = `${el.scrollHeight}px`;
  }, []);

  const handleToggleLock = useCallback(() => {
    onToggleLock?.(id, !is_locked);
  }, [id, is_locked, onToggleLock]);

  const handleClick = useCallback(() => {
    if (is_locked) return;
    setEditing(true);
  }, [is_locked]);

  const handleBlur = useCallback(() => {
    setEditing(false);
    if (data.onBodyChange) {
      data.onBodyChange(id, value);
    }
  }, [data, id, value]);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      setValue(e.target.value);
      autoGrow(e.target);
    },
    [autoGrow],
  );

  const handleInput = useCallback(
    (e: React.FormEvent<HTMLTextAreaElement>) => {
      autoGrow(e.currentTarget);
    },
    [autoGrow],
  );

  return (
    <UserSelectionHighlight selectedBy={selectedBy}>
    <div
      className="group relative rounded bg-transparent text-sm text-foreground hover:outline hover:outline-1 hover:outline-dashed hover:outline-border"
      style={{ minWidth: 80 }}
      data-testid="free-text-node"
      onClick={!editing ? handleClick : undefined}
    >
      {ai_modified_indicator && (
        <span
          className="absolute -left-1 -top-1 z-10 h-2 w-2 rounded-full bg-amber-400 motion-safe:animate-pulse"
          data-testid="ai-modified-dot"
        />
      )}

      <Handle type="target" position={Position.Top} className="!bg-border" />

      {editing ? (
        <textarea
          ref={textareaRef}
          className="w-full resize-none bg-transparent p-1 text-sm text-foreground outline-none"
          value={value}
          onChange={handleChange}
          onInput={handleInput}
          onBlur={handleBlur}
          style={{ minHeight: 24 }}
          data-testid="free-text-textarea"
        />
      ) : (
        <div className="whitespace-pre-wrap p-1" data-testid="free-text-display">
          {body || "\u00A0"}
        </div>
      )}

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
    </UserSelectionHighlight>
  );
}

export const FreeTextNode = memo(FreeTextNodeComponent);
