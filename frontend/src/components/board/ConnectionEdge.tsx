import { useState, useCallback, useRef, useEffect } from "react";
import {
  BaseEdge,
  getSmoothStepPath,
  EdgeLabelRenderer,
  type EdgeProps,
  type Edge,
} from "@xyflow/react";

type ConnectionEdgeData = {
  label?: string;
};

export type ConnectionEdge = Edge<ConnectionEdgeData, "connection">;

export function ConnectionEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  selected,
  data,
  markerEnd,
}: EdgeProps<ConnectionEdge>) {
  const [isEditing, setIsEditing] = useState(false);
  const [labelText, setLabelText] = useState(data?.label ?? "");
  const inputRef = useRef<HTMLInputElement>(null);

  const [edgePath, labelX, labelY] = getSmoothStepPath({
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
  });

  const handleDoubleClick = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      setIsEditing(true);
    },
    [],
  );

  const commitLabel = useCallback(() => {
    setIsEditing(false);
  }, []);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter" || e.key === "Escape") {
        commitLabel();
      }
    },
    [commitLabel],
  );

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const strokeColor = selected ? "var(--primary)" : "gray";
  const strokeWidth = selected ? 2.5 : 1.5;

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        markerEnd={markerEnd}
        style={{
          stroke: strokeColor,
          strokeWidth,
          transition: "stroke 0.15s, stroke-width 0.15s",
        }}
        className="connection-edge"
      />
      {(labelText || isEditing) && (
        <EdgeLabelRenderer>
          <div
            className="nodrag nopan"
            style={{
              position: "absolute",
              transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
              pointerEvents: "all",
            }}
            onDoubleClick={handleDoubleClick}
            data-testid={`edge-label-${id}`}
          >
            {isEditing ? (
              <input
                ref={inputRef}
                value={labelText}
                onChange={(e) => setLabelText(e.target.value)}
                onBlur={commitLabel}
                onKeyDown={handleKeyDown}
                className="rounded-sm border bg-card px-1.5 py-0.5 text-xs outline-none"
                style={{ minWidth: 60 }}
              />
            ) : (
              <span className="rounded-sm border bg-card px-1.5 py-0.5 text-xs">
                {labelText}
              </span>
            )}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
}
