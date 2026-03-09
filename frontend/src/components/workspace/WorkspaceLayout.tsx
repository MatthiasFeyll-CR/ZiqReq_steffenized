import { useCallback, useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { PanelDivider } from "./PanelDivider";

const STORAGE_KEY = "workspace-panel-split";
const DEFAULT_RATIO = 0.4;
const MIN_CHAT_PX = 280;
const MIN_BOARD_PX = 320;

function clampRatio(ratio: number, containerWidth: number): number {
  if (containerWidth <= 0) return DEFAULT_RATIO;
  const minChatRatio = MIN_CHAT_PX / containerWidth;
  const maxChatRatio = (containerWidth - MIN_BOARD_PX) / containerWidth;
  return Math.min(Math.max(ratio, minChatRatio), maxChatRatio);
}

function loadRatio(): number {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored !== null) {
      const val = parseFloat(stored);
      if (!isNaN(val) && val > 0 && val < 1) return val;
    }
  } catch {
    // localStorage unavailable
  }
  return DEFAULT_RATIO;
}

function saveRatio(ratio: number) {
  try {
    localStorage.setItem(STORAGE_KEY, String(ratio));
  } catch {
    // localStorage unavailable
  }
}

interface WorkspaceLayoutProps {
  chatPanel?: React.ReactNode;
  reviewVisible?: boolean;
}

export function WorkspaceLayout({ chatPanel, reviewVisible = true }: WorkspaceLayoutProps) {
  const { t } = useTranslation();
  const containerRef = useRef<HTMLDivElement>(null);
  const [ratio, setRatio] = useState(loadRatio);
  const [isTransitioning, setIsTransitioning] = useState(false);

  const handleDrag = useCallback((newRatio: number) => {
    const container = containerRef.current;
    if (!container) return;
    const clamped = clampRatio(newRatio, container.offsetWidth);
    setRatio(clamped);
    saveRatio(clamped);
  }, []);

  const handleDoubleClick = useCallback(() => {
    const container = containerRef.current;
    if (!container) return;
    const clamped = clampRatio(DEFAULT_RATIO, container.offsetWidth);
    setIsTransitioning(true);
    setRatio(clamped);
    saveRatio(clamped);
    setTimeout(() => setIsTransitioning(false), 200);
  }, []);

  // Re-clamp on window resize
  useEffect(() => {
    const handleResize = () => {
      const container = containerRef.current;
      if (!container) return;
      setRatio((prev) => clampRatio(prev, container.offsetWidth));
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const chatWidth = `${ratio * 100}%`;
  const boardWidth = `${(1 - ratio) * 100}%`;
  const transition = isTransitioning ? "width 200ms ease" : undefined;

  return (
    <div
      ref={containerRef}
      className="flex flex-1 overflow-hidden"
      data-testid="workspace-layout"
    >
      {/* Chat Panel */}
      <div
        className="flex flex-col overflow-hidden"
        style={{ width: chatWidth, transition }}
        data-testid="chat-panel"
      >
        {chatPanel ?? (
          <div className="flex-1 flex items-center justify-center text-muted-foreground">
            {t("workspace.chatPlaceholder", "Chat")}
          </div>
        )}
      </div>

      <PanelDivider onDrag={handleDrag} onDoubleClick={handleDoubleClick} />

      {/* Context Panel (Board/Review tabs) */}
      <div
        className="flex flex-col overflow-hidden"
        style={{ width: boardWidth, transition }}
        data-testid="context-panel"
      >
        <Tabs defaultValue="board" className="flex flex-col h-full">
          <TabsList className="shrink-0">
            <TabsTrigger value="board" data-testid="tab-board">
              {t("workspace.boardTab", "Board")}
            </TabsTrigger>
            {reviewVisible && (
              <TabsTrigger value="review" data-testid="tab-review">
                {t("workspace.reviewTab", "Review")}
              </TabsTrigger>
            )}
          </TabsList>
          <TabsContent value="board" className="flex-1 overflow-auto" data-testid="board-content">
            <div className="flex items-center justify-center h-full text-muted-foreground">
              {t("workspace.boardPlaceholder", "Board canvas (M4)")}
            </div>
          </TabsContent>
          {reviewVisible && (
            <TabsContent value="review" className="flex-1 overflow-auto" data-testid="review-content">
              <div className="flex items-center justify-center h-full text-muted-foreground">
                {t("workspace.reviewPlaceholder", "Review (M9)")}
              </div>
            </TabsContent>
          )}
        </Tabs>
      </div>
    </div>
  );
}
