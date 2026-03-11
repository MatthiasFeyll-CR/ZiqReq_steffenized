import { useTranslation } from "react-i18next";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const SECTION_KEYS = [
  "title",
  "short_description",
  "current_workflow",
  "affected_department",
  "core_capabilities",
  "success_criteria",
] as const;

const SECTION_LABELS: Record<string, string> = {
  title: "Title",
  short_description: "Short Description",
  current_workflow: "Current Workflow & Pain Points",
  affected_department: "Affected Department",
  core_capabilities: "Core Capabilities",
  success_criteria: "Success Criteria",
};

interface ProgressIndicatorProps {
  readinessEvaluation: Record<string, "ready" | "insufficient">;
  allowInformationGaps: boolean;
  loading?: boolean;
}

export function ProgressIndicator({
  readinessEvaluation,
  allowInformationGaps,
  loading,
}: ProgressIndicatorProps) {
  const { t } = useTranslation();

  const readyCount = allowInformationGaps
    ? 0
    : SECTION_KEYS.filter((k) => readinessEvaluation[k] === "ready").length;

  const label = allowInformationGaps
    ? t("brd.gapsAllowed", "Gaps allowed")
    : t("brd.sectionsReady", "{{count}}/6 sections ready", { count: readyCount });

  return (
    <div data-testid="progress-indicator">
      <TooltipProvider delayDuration={200}>
        <div className="flex gap-0.5" data-testid="progress-bar">
          {SECTION_KEYS.map((key) => {
            const isReady = !allowInformationGaps && readinessEvaluation[key] === "ready";
            const statusText = allowInformationGaps
              ? "Gaps allowed"
              : readinessEvaluation[key] === "ready"
                ? "Ready"
                : "Insufficient";
            const tooltipText = `${SECTION_LABELS[key]}: ${statusText}`;
            return (
              <Tooltip key={key}>
                <TooltipTrigger asChild>
                  <div
                    className={`h-2 flex-1 rounded-full ${
                      loading
                        ? "bg-muted animate-pulse"
                        : isReady
                          ? "bg-green-500"
                          : "bg-gray-300"
                    }`}
                    data-testid={`progress-segment-${key}`}
                    data-tooltip={tooltipText}
                  />
                </TooltipTrigger>
                <TooltipContent>
                  <p>{tooltipText}</p>
                </TooltipContent>
              </Tooltip>
            );
          })}
        </div>
      </TooltipProvider>
      <p className="text-xs text-muted-foreground mt-1" data-testid="progress-label">
        {loading ? t("brd.evaluating", "Evaluating...") : label}
      </p>
    </div>
  );
}

export { SECTION_KEYS, SECTION_LABELS };
