import { memo, useState, useCallback, useRef, useEffect } from "react";
import { Handle, Position, type NodeProps, type Node } from "@xyflow/react";

export interface FreeTextNodeData {
  body?: string;
  onBodyChange?: (nodeId: string, body: string) => void;
  [key: string]: unknown;
}

export type FreeTextNodeType = Node<FreeTextNodeData, "free_text">;

function FreeTextNodeComponent({ data, id }: NodeProps<FreeTextNodeType>) {
  const { body } = data;
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

  const handleClick = useCallback(() => {
    setEditing(true);
  }, []);

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
    <div
      className="group relative rounded bg-transparent text-sm text-foreground hover:outline hover:outline-1 hover:outline-dashed hover:outline-border"
      style={{ minWidth: 80 }}
      data-testid="free-text-node"
      onClick={!editing ? handleClick : undefined}
    >
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

      <Handle type="source" position={Position.Bottom} className="!bg-border" />
    </div>
  );
}

export const FreeTextNode = memo(FreeTextNodeComponent);
