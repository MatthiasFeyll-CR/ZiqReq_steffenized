import { useEffect, useState } from "react";

interface AIProcessingIndicatorProps {
  ideaId: string;
}

export function AIProcessingIndicator({ ideaId }: AIProcessingIndicatorProps) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const handler = (e: Event) => {
      const { idea_id, state } = (e as CustomEvent).detail;
      if (idea_id !== ideaId) return;
      if (state === "started") {
        setVisible(true);
      } else if (state === "completed" || state === "failed") {
        setVisible(false);
      }
    };
    window.addEventListener("ws:ai_processing", handler);
    return () => window.removeEventListener("ws:ai_processing", handler);
  }, [ideaId]);

  if (!visible) return null;

  return (
    <div
      className="flex items-center justify-center py-2 text-sm text-muted-foreground"
      data-testid="ai-processing-indicator"
    >
      <span>AI is processing</span>
      <span className="inline-flex ml-0.5" aria-hidden="true">
        <span className="motion-safe:animate-bounce [animation-delay:0ms]">.</span>
        <span className="motion-safe:animate-bounce [animation-delay:150ms]">.</span>
        <span className="motion-safe:animate-bounce [animation-delay:300ms]">.</span>
      </span>
    </div>
  );
}
