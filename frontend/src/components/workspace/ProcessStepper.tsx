import { useCallback, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { Check, Lock } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

export type ProcessStep = "brainstorm" | "structure" | "review";

const STEPS: ProcessStep[] = ["brainstorm", "structure", "review"];

interface ProcessStepperProps {
  activeStep: ProcessStep;
  onStepChange: (step: ProcessStep) => void;
  canAccessStructure: boolean;
  canAccessReview: boolean;
  structureGateMessage?: string;
  reviewGateMessage?: string;
}

export function ProcessStepper({
  activeStep,
  onStepChange,
  canAccessStructure,
  canAccessReview,
  structureGateMessage,
  reviewGateMessage,
}: ProcessStepperProps) {
  const { t } = useTranslation();

  const stepConfig = {
    brainstorm: {
      label: t("process.brainstorm", "Define"),
      description: t("process.brainstormDesc", "Chat with AI to define your project"),
    },
    structure: {
      label: t("process.structure", "Structure"),
      description: t("process.structureDesc", "Review & refine your requirements"),
    },
    review: {
      label: t("process.review", "Review"),
      description: t("process.reviewDesc", "Submit for approval"),
    },
  };

  const activeIndex = STEPS.indexOf(activeStep);

  return (
    <TooltipProvider delayDuration={200}>
      <nav
        className="flex items-center gap-0 w-full"
        aria-label={t("process.stepper", "Process steps")}
        data-testid="process-stepper"
      >
        {STEPS.map((step, index) => {
          const config = stepConfig[step];
          const isActive = step === activeStep;
          const isCompleted = index < activeIndex;
          const isGated =
            (step === "structure" && !canAccessStructure) ||
            (step === "review" && !canAccessReview);
          const gateMessage =
            step === "structure"
              ? structureGateMessage
              : step === "review"
                ? reviewGateMessage
                : undefined;

          return (
            <StepItem
              key={step}
              step={step}
              index={index}
              label={config.label}
              description={config.description}
              isActive={isActive}
              isCompleted={isCompleted}
              isGated={isGated}
              gateMessage={gateMessage}
              isLast={index === STEPS.length - 1}
              onStepChange={onStepChange}
            />
          );
        })}
      </nav>
    </TooltipProvider>
  );
}

interface StepItemProps {
  step: ProcessStep;
  index: number;
  label: string;
  description: string;
  isActive: boolean;
  isCompleted: boolean;
  isGated: boolean;
  gateMessage?: string;
  isLast: boolean;
  onStepChange: (step: ProcessStep) => void;
}

function StepItem({
  step,
  index,
  label,
  description,
  isActive,
  isCompleted,
  isGated,
  gateMessage,
  isLast,
  onStepChange,
}: StepItemProps) {
  const [shaking, setShaking] = useState(false);
  const shakeTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleClick = useCallback(() => {
    if (isGated) {
      if (shakeTimeoutRef.current) clearTimeout(shakeTimeoutRef.current);
      setShaking(true);
      shakeTimeoutRef.current = setTimeout(() => setShaking(false), 500);
      return;
    }
    onStepChange(step);
  }, [isGated, onStepChange, step]);

  const stepNumber = index + 1;

  const content = (
    <button
      type="button"
      onClick={handleClick}
      className={cn(
        "group flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-all duration-150 min-w-0",
        isActive && "bg-secondary/10 dark:bg-primary/10",
        !isActive && !isGated && "hover:bg-muted/50",
        isGated && "cursor-not-allowed opacity-60",
        shaking && "animate-[shake_0.5s_ease-in-out]",
      )}
      aria-current={isActive ? "step" : undefined}
      data-testid={`step-${step}`}
    >
      {/* Step number circle */}
      <div
        className={cn(
          "shrink-0 flex items-center justify-center w-8 h-8 rounded-full text-sm font-semibold transition-colors duration-150",
          isActive && "bg-secondary text-white dark:bg-primary dark:text-primary-foreground",
          isCompleted && !isActive && "bg-green-500 text-white dark:bg-green-600",
          !isActive && !isCompleted && !isGated && "bg-muted text-muted-foreground border border-border",
          isGated && "bg-muted text-muted-foreground/50 border border-border/50",
        )}
      >
        {isCompleted && !isActive ? (
          <Check className="h-4 w-4" />
        ) : isGated ? (
          <Lock className="h-3.5 w-3.5" />
        ) : (
          stepNumber
        )}
      </div>

      {/* Label + description */}
      <div className="min-w-0 hidden sm:block">
        <div
          className={cn(
            "text-sm font-medium leading-tight truncate",
            isActive && "text-foreground",
            isCompleted && !isActive && "text-green-700 dark:text-green-400",
            !isActive && !isCompleted && !isGated && "text-muted-foreground group-hover:text-foreground",
            isGated && "text-muted-foreground/50",
          )}
        >
          {label}
        </div>
        <div
          className={cn(
            "text-xs leading-tight truncate mt-0.5",
            isActive && "text-muted-foreground",
            isCompleted && !isActive && "text-green-600/70 dark:text-green-500/70",
            !isActive && !isCompleted && "text-muted-foreground/60",
            isGated && "text-muted-foreground/40",
          )}
        >
          {description}
        </div>
      </div>
    </button>
  );

  return (
    <>
      {isGated && gateMessage ? (
        <Tooltip>
          <TooltipTrigger asChild>{content}</TooltipTrigger>
          <TooltipContent side="bottom" className="max-w-[240px] text-center">
            <p>{gateMessage}</p>
          </TooltipContent>
        </Tooltip>
      ) : (
        content
      )}
      {/* Connector line */}
      {!isLast && (
        <div className="flex-1 flex items-center px-1 min-w-4 max-w-12">
          <div
            className={cn(
              "h-0.5 w-full rounded-full transition-colors duration-300",
              isCompleted ? "bg-green-400 dark:bg-green-600" : "bg-border",
            )}
          />
        </div>
      )}
    </>
  );
}
