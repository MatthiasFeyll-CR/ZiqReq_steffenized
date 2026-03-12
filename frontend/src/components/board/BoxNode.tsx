import { memo, useCallback, useState, useRef, useEffect } from "react";
import { Handle, Position, type NodeProps, type Node } from "@xyflow/react";
import { Pin, Bot, Lock, Unlock } from "lucide-react";
import { useTranslation } from "react-i18next";
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
  onTitleChange?: (nodeId: string, title: string) => void;
  onBodyChange?: (nodeId: string, body: string) => void;
  [key: string]: unknown;
}

export type BoxNodeType = Node<BoxNodeData, "box">;

function BoxNodeComponent({ data, id }: NodeProps<BoxNodeType>) {
  const { title, body, created_by, is_locked, ai_modified_indicator, onToggleLock, _selectedBy } = data;
  const selectedBy = _selectedBy as { user_id: string; display_name: string } | null;
  const { t } = useTranslation();

  const [editingTitle, setEditingTitle] = useState(false);
  const [editingBody, setEditingBody] = useState(false);
  const [titleValue, setTitleValue] = useState(title ?? "");
  const [bodyValue, setBodyValue] = useState(body ?? "");
  const titleRef = useRef<HTMLInputElement>(null);
  const bodyRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => setTitleValue(title ?? ""), [title]);
  useEffect(() => setBodyValue(body ?? ""), [body]);

  useEffect(() => {
    if (editingTitle && titleRef.current) titleRef.current.focus();
  }, [editingTitle]);

  useEffect(() => {
    if (editingBody && bodyRef.current) {
      bodyRef.current.focus();
      autoGrow(bodyRef.current);
    }
  }, [editingBody]);

  const autoGrow = useCallback((el: HTMLTextAreaElement) => {
    el.style.height = "auto";
    el.style.height = `${el.scrollHeight}px`;
  }, []);

  const handleReference = useCallback(() => {
    const nodeId = data.nodeId ?? id;
    window.dispatchEvent(
      new CustomEvent("board:reference", { detail: `@board[${nodeId}]` }),
    );
  }, [data.nodeId, id]);

  const handleToggleLock = useCallback(() => {
    onToggleLock?.(id, !is_locked);
  }, [id, is_locked, onToggleLock]);

  const handleTitleDoubleClick = useCallback(() => {
    if (is_locked) return;
    setEditingTitle(true);
  }, [is_locked]);

  const handleTitleBlur = useCallback(() => {
    setEditingTitle(false);
    if (data.onTitleChange && titleValue !== title) {
      data.onTitleChange(id, titleValue);
    }
  }, [data, id, titleValue, title]);

  const handleTitleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter") {
        e.preventDefault();
        (e.target as HTMLInputElement).blur();
      } else if (e.key === "Escape") {
        setTitleValue(title ?? "");
        setEditingTitle(false);
      }
    },
    [title],
  );

  const handleBodyDoubleClick = useCallback(() => {
    if (is_locked) return;
    setEditingBody(true);
  }, [is_locked]);

  const handleBodyBlur = useCallback(() => {
    setEditingBody(false);
    if (data.onBodyChange && bodyValue !== body) {
      data.onBodyChange(id, bodyValue);
    }
  }, [data, id, bodyValue, body]);

  const handleBodyKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Escape") {
        setBodyValue(body ?? "");
        setEditingBody(false);
      }
    },
    [body],
  );

  const bullets = bodyValue
    ? bodyValue
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
          {editingTitle ? (
            <input
              ref={titleRef}
              className="flex-1 bg-transparent text-sm font-medium outline-none"
              value={titleValue}
              onChange={(e) => setTitleValue(e.target.value)}
              onBlur={handleTitleBlur}
              onKeyDown={handleTitleKeyDown}
              data-testid="box-title-input"
            />
          ) : (
            <span
              className="flex-1 truncate text-sm font-medium cursor-text"
              onDoubleClick={handleTitleDoubleClick}
            >
              {titleValue || "\u00A0"}
            </span>
          )}
          <Button
            variant="ghost"
            size="icon-sm"
            className="h-6 w-6 shrink-0"
            onClick={handleReference}
            aria-label={t("board.referenceNode")}
            data-testid="reference-button"
          >
            <Pin className="h-3.5 w-3.5" />
          </Button>
        </div>

        {/* Body */}
        {editingBody ? (
          <textarea
            ref={bodyRef}
            className="w-full resize-none bg-transparent px-3 py-2 text-sm outline-none"
            value={bodyValue}
            onChange={(e) => {
              setBodyValue(e.target.value);
              autoGrow(e.target);
            }}
            onInput={(e) => autoGrow(e.currentTarget)}
            onBlur={handleBodyBlur}
            onKeyDown={handleBodyKeyDown}
            style={{ minHeight: 32 }}
            data-testid="box-body-textarea"
          />
        ) : (
          <div
            className="px-3 py-2 text-sm cursor-text min-h-[32px]"
            onDoubleClick={handleBodyDoubleClick}
          >
            {bullets.length > 0 ? (
              <ul className="list-disc list-inside space-y-0.5">
                {bullets.map((bullet, i) => (
                  <li key={i}>{bullet}</li>
                ))}
              </ul>
            ) : (
              <span className="text-muted-foreground text-xs">{is_locked ? "" : "Double-click to edit"}</span>
            )}
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

export const BoxNode = memo(BoxNodeComponent);
