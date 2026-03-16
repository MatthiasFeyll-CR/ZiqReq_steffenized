import { useCallback, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { MessageSquare, FileText, CheckCircle, Check } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

export type ProcessStep = "brainstorm" | "document" | "review";

const STEPS: ProcessStep[] = ["brainstorm", "document", "review"];

interface ProcessStepperProps {
  activeStep: ProcessStep;
  onStepChange: (step: ProcessStep) => void;
  canAccessDocument: boolean;
  canAccessReview: boolean;
  documentGateMessage?: string;
  reviewGateMessage?: string;
}

export function ProcessStepper({
  activeStep,
  onStepChange,
  canAccessDocument,
  canAccessReview,
  documentGateMessage,
  reviewGateMessage,
}: ProcessStepperProps) {
  const { t } = useTranslation();

  const stepConfig = {
    brainstorm: {
      icon: MessageSquare,
      label: t("process.brainstorm", "Brainstorm"),
    },
    document: {
      icon: FileText,
      label: t("process.document", "Document"),
    },
    review: {
      icon: CheckCircle,
      label: t("process.review", "Review"),
    },
  };

  const activeIndex = STEPS.indexOf(activeStep);

  return (
    <TooltipProvider delayDuration={200}>
    <nav
      className="flex items-center gap-1"
      aria-label={t("process.stepper", "Process steps")}
      data-testid="process-stepper"
    >
      {STEPS.map((step, index) => {
        const config = stepConfig[step];
        const Icon = config.icon;
        const isActive = step === activeStep;
        const isCompleted = index < activeIndex;
        const isGated =
          (step === "document" && !canAccessDocument) ||
          (step === "review" && !canAccessReview);
        const gateMessage =
          step === "document"
            ? documentGateMessage
            : step === "review"
              ? reviewGateMessage
              : undefined;

        return (
          <StepItem
            key={step}
            step={step}
            index={index}
            icon={Icon}
            label={config.label}
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
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  isActive: boolean;
  isCompleted: boolean;
  isGated: boolean;
  gateMessage?: string;
  isLast: boolean;
  onStepChange: (step: ProcessStep) => void;
}

function StepItem({
  step,
  icon: Icon,
  label,
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
      // Trigger shake animation
      if (shakeTimeoutRef.current) clearTimeout(shakeTimeoutRef.current);
      setShaking(true);
      shakeTimeoutRef.current = setTimeout(() => setShaking(false), 500);
      return;
    }
    onStepChange(step);
  }, [isGated, onStepChange, step]);

  const button = (
    <button
      type="button"
      onClick={handleClick}
      className={cn(
        "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-150",
        isActive &&
          "bg-secondary text-white dark:bg-primary dark:text-primary-foreground shadow-sm",
        isCompleted &&
          !isActive &&
          "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 hover:bg-green-200 dark:hover:bg-green-900/50",
        !isActive &&
          !isCompleted &&
          !isGated &&
          "text-muted-foreground hover:bg-muted hover:text-foreground",
        isGated &&
          "text-muted-foreground/50 cursor-not-allowed",
        shaking && "animate-[shake_0.5s_ease-in-out]"
      )}
      aria-current={isActive ? "step" : undefined}
      data-testid={`step-${step}`}
    >
      {isCompleted && !isActive ? (
        <Check className="h-4 w-4" />
      ) : (
        <Icon className="h-4 w-4" />
      )}
      <span className="hidden sm:inline">{label}</span>
    </button>
  );

  return (
    <>
      {isGated && gateMessage ? (
        <Tooltip>
          <TooltipTrigger asChild>{button}</TooltipTrigger>
          <TooltipContent side="bottom" className="max-w-[240px] text-center">
            <p>{gateMessage}</p>
          </TooltipContent>
        </Tooltip>
      ) : (
        button
      )}
      {!isLast && (
        <div
          className={cn(
            "w-6 h-px",
            isCompleted ? "bg-green-400 dark:bg-green-600" : "bg-border"
          )}
        />
      )}
    </>
  );
}
