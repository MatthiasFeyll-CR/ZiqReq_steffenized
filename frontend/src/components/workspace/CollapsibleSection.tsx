import { ChevronRight } from "lucide-react";
import { useCallback, useId } from "react";

interface CollapsibleSectionProps {
  title: string;
  summary?: string;
  expanded?: boolean;
  onExpandedChange?: (expanded: boolean) => void;
  children: React.ReactNode;
  variant?: "default" | "success";
  /** Label for a CTA button shown on the right side of the header when collapsed */
  collapsedActionLabel?: string;
  /** Callback when the collapsed CTA button is clicked (defaults to expanding) */
  onCollapsedAction?: () => void;
}

export function CollapsibleSection({
  title,
  summary,
  expanded,
  onExpandedChange,
  children,
  variant = "default",
  collapsedActionLabel,
  onCollapsedAction,
}: CollapsibleSectionProps) {
  const id = useId();
  const buttonId = `${id}-button`;
  const contentId = `${id}-content`;

  const toggle = useCallback(() => {
    onExpandedChange?.(!expanded);
  }, [expanded, onExpandedChange]);

  const isOpen = expanded ?? false;

  return (
    <div
      className={`rounded-lg border border-border overflow-hidden ${
        variant === "success" ? "bg-green-500/5" : ""
      }`}
    >
      <button
        type="button"
        id={buttonId}
        onClick={toggle}
        aria-expanded={isOpen}
        aria-controls={contentId}
        className="flex w-full items-center justify-between gap-3 bg-muted/30 px-4 py-3 text-left hover:bg-muted/50 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 cursor-pointer"
      >
        <div className="flex items-center gap-2 min-w-0">
          <ChevronRight
            className={`h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200 ${
              isOpen ? "rotate-90" : ""
            }`}
            aria-hidden="true"
          />
          <span className="text-sm font-medium text-foreground">{title}</span>
          {summary && (
            <span className="text-xs text-muted-foreground truncate" title={summary}>
              {summary}
            </span>
          )}
        </div>
        {!isOpen && collapsedActionLabel && (
          <span
            role="button"
            tabIndex={0}
            onClick={(e) => {
              e.stopPropagation();
              if (onCollapsedAction) {
                onCollapsedAction();
              } else {
                onExpandedChange?.(true);
              }
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                e.stopPropagation();
                if (onCollapsedAction) {
                  onCollapsedAction();
                } else {
                  onExpandedChange?.(true);
                }
              }
            }}
            className="shrink-0 inline-flex items-center rounded-md bg-primary px-3 py-1 text-xs font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            {collapsedActionLabel}
          </span>
        )}
      </button>

      <div
        id={contentId}
        className="collapsible-grid"
        data-expanded={isOpen}
        role="region"
        aria-labelledby={buttonId}
      >
        <div className="collapsible-content">
          <div className="px-4 py-3">{children}</div>
        </div>
      </div>
    </div>
  );
}
