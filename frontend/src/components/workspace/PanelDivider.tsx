import { useCallback, useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

interface PanelDividerProps {
  onDrag: (ratio: number) => void;
  onDoubleClick: () => void;
}

export function PanelDivider({ onDrag, onDoubleClick }: PanelDividerProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const dividerRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();
      setIsDragging(true);
    },
    [],
  );

  useEffect(() => {
    if (!isDragging) return;

    const handleMouseMove = (e: MouseEvent) => {
      const container = dividerRef.current?.parentElement;
      if (!container) return;
      const rect = container.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const ratio = x / rect.width;
      onDrag(ratio);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);

    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isDragging, onDrag]);

  const active = isDragging || isHovered;

  return (
    <div
      ref={dividerRef}
      data-testid="panel-divider"
      className={cn(
        "relative flex-shrink-0 cursor-col-resize select-none",
        "w-[4px]",
      )}
      style={{ padding: "0 4px" }}
      onMouseDown={handleMouseDown}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onDoubleClick={onDoubleClick}
    >
      <div
        className={cn(
          "h-full w-[4px] transition-colors duration-150",
          active ? "bg-primary shadow-[0_0_6px_var(--color-primary)]" : "bg-border",
        )}
      />
    </div>
  );
}
