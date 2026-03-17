import { useEffect, useState } from "react";

interface AIProcessingIndicatorProps {
  projectId: string;
}

export function AIProcessingIndicator({ projectId }: AIProcessingIndicatorProps) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const handler = (e: Event) => {
      const { project_id, state } = (e as CustomEvent).detail;
      if (project_id !== projectId) return;
      if (state === "started") {
        setVisible(true);
      } else if (state === "completed" || state === "failed") {
        setVisible(false);
      }
    };
    window.addEventListener("ws:ai_processing", handler);
    return () => window.removeEventListener("ws:ai_processing", handler);
  }, [projectId]);

  if (!visible) return null;

  return (
    <div
      className="flex items-center gap-2 px-6 py-2"
      role="status"
      aria-live="polite"
      data-testid="ai-processing-indicator"
    >
      <div className="flex items-end gap-1 rounded-full bg-muted px-3 py-2" aria-hidden="true">
        <span className="typing-dot h-1.5 w-1.5 rounded-full bg-muted-foreground" style={{ animationDelay: "0ms" }} />
        <span className="typing-dot h-1.5 w-1.5 rounded-full bg-muted-foreground" style={{ animationDelay: "150ms" }} />
        <span className="typing-dot h-1.5 w-1.5 rounded-full bg-muted-foreground" style={{ animationDelay: "300ms" }} />
      </div>
      <span className="text-xs text-muted-foreground">thinking</span>
    </div>
  );
}
