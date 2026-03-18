import { useCallback, useId } from "react";
import { ChevronRight } from "lucide-react";

interface CollapsibleSectionProps {
  title: string;
  summary?: string;
  expanded?: boolean;
  onExpandedChange?: (expanded: boolean) => void;
  children: React.ReactNode;
  variant?: "default" | "success";
}

export function CollapsibleSection({
  title,
  summary,
  expanded,
  onExpandedChange,
  children,
  variant = "default",
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
