import { useCallback, useEffect, useState } from "react";
import { fetchContextWindow, type ContextWindowData } from "@/api/projects";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const POLL_INTERVAL = 30_000;
const SIZE = 20;
const STROKE_WIDTH = 2.5;
const RADIUS = (SIZE - STROKE_WIDTH) / 2;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

interface ContextWindowIndicatorProps {
  projectId: string;
  projectState: string;
}

export function ContextWindowIndicator({ projectId, projectState }: ContextWindowIndicatorProps) {
  const [data, setData] = useState<ContextWindowData | null>(null);

  const load = useCallback(async () => {
    try {
      const result = await fetchContextWindow(projectId);
      setData(result);
    } catch {
      // Silently fail — indicator just won't update
    }
  }, [projectId]);

  useEffect(() => {
    if (projectState !== "open" || projectId === "new") return;

    void load();
    const interval = setInterval(() => void load(), POLL_INTERVAL);
    return () => clearInterval(interval);
  }, [projectState, projectId, load]);

  if (projectState !== "open") return null;

  const usage = data?.usage_percentage ?? 0;
  const isWarning = usage >= 80;
  const offset = CIRCUMFERENCE - (usage / 100) * CIRCUMFERENCE;

  const tooltipLines = [
    `Context: ${usage}% used, ${data?.message_count ?? 0} messages, ${data?.compression_iterations ?? 0} compressions`,
  ];
  if (data && data.compression_iterations > 0) {
    tooltipLines.push("Older messages compressed");
  }

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div
            className="flex-shrink-0 mb-1.5 cursor-default"
            data-testid="context-window-indicator"
          >
            <svg
              width={SIZE}
              height={SIZE}
              viewBox={`0 0 ${SIZE} ${SIZE}`}
              className="block"
            >
              {/* Background ring */}
              <circle
                cx={SIZE / 2}
                cy={SIZE / 2}
                r={RADIUS}
                fill="none"
                stroke="currentColor"
                strokeWidth={STROKE_WIDTH}
                className="text-muted-foreground opacity-30"
              />
              {/* Progress ring */}
              <circle
                cx={SIZE / 2}
                cy={SIZE / 2}
                r={RADIUS}
                fill="none"
                stroke="currentColor"
                strokeWidth={STROKE_WIDTH}
                strokeDasharray={CIRCUMFERENCE}
                strokeDashoffset={offset}
                strokeLinecap="round"
                transform={`rotate(-90 ${SIZE / 2} ${SIZE / 2})`}
                className={isWarning ? "text-amber-500" : "text-primary"}
                data-testid="context-progress-ring"
              />
            </svg>
          </div>
        </TooltipTrigger>
        <TooltipContent side="top" data-testid="context-window-tooltip">
          {tooltipLines.map((line, i) => (
            <div key={i}>{line}</div>
          ))}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
