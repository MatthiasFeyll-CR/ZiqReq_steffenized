import { useCallback, useEffect, useRef, useState } from "react";

const STORAGE_KEY = "workspacePanelRatio";
const DEFAULT_RATIO = 0.4;
const MIN_CHAT_PX = 280;
const MIN_REQUIREMENTS_PX = 320;

interface WorkspaceLayoutProps {
  chatPanel?: React.ReactNode;
  requirementsPanel?: React.ReactNode;
}

export function WorkspaceLayout({
  chatPanel,
  requirementsPanel,
}: WorkspaceLayoutProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [ratio, setRatio] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const val = parseFloat(stored);
        if (!isNaN(val) && val >= 0.1 && val <= 0.9) return val;
      }
    } catch {
      // ignore
    }
    return DEFAULT_RATIO;
  });

  const isDraggingRef = useRef(false);

  const handleMouseDown = useCallback(() => {
    isDraggingRef.current = true;

    const onMouseMove = (e: MouseEvent) => {
      if (!isDraggingRef.current || !containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const totalWidth = rect.width;
      let newRatio = (e.clientX - rect.left) / totalWidth;

      // Enforce min widths
      const minChatRatio = MIN_CHAT_PX / totalWidth;
      const maxChatRatio = 1 - MIN_REQUIREMENTS_PX / totalWidth;
      newRatio = Math.max(minChatRatio, Math.min(maxChatRatio, newRatio));

      setRatio(newRatio);
    };

    const onMouseUp = () => {
      isDraggingRef.current = false;
      document.removeEventListener("mousemove", onMouseMove);
      document.removeEventListener("mouseup", onMouseUp);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };

    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseup", onMouseUp);
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
  }, []);

  const handleDoubleClick = useCallback(() => {
    setRatio(DEFAULT_RATIO);
  }, []);

  // Persist ratio
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, ratio.toString());
    } catch {
      // ignore
    }
  }, [ratio]);

  // If no requirements panel, render single panel
  if (!requirementsPanel) {
    return (
      <div
        className="flex flex-1 overflow-hidden"
        data-testid="workspace-layout"
      >
        <div
          className="flex flex-col h-full w-full overflow-hidden"
          data-testid="chat-panel"
        >
          {chatPanel ?? (
            <div className="flex-1 flex items-center justify-center text-muted-foreground">
              Chat
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="flex flex-1 overflow-hidden"
      data-testid="workspace-layout"
    >
      {/* Chat panel */}
      <div
        className="flex flex-col h-full overflow-hidden"
        style={{ width: `${ratio * 100}%` }}
        data-testid="chat-panel"
      >
        {chatPanel ?? (
          <div className="flex-1 flex items-center justify-center text-muted-foreground">
            Chat
          </div>
        )}
      </div>

      {/* Draggable divider */}
      <div
        className="relative shrink-0 cursor-col-resize px-1 group"
        onMouseDown={handleMouseDown}
        onDoubleClick={handleDoubleClick}
        data-testid="workspace-divider"
      >
        <div className="h-full w-px bg-border group-hover:bg-primary group-active:bg-primary transition-colors" />
      </div>

      {/* Requirements panel */}
      <div
        className="flex flex-col h-full overflow-hidden flex-1"
        data-testid="requirements-panel-container"
      >
        {requirementsPanel}
      </div>
    </div>
  );
}
