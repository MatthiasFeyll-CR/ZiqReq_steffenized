import { useCallback, useRef } from "react";
import { Lock, LockOpen, RefreshCw, Loader2 } from "lucide-react";

interface SectionFieldProps {
  label: string;
  sectionKey: string;
  value: string;
  locked: boolean;
  readiness?: "ready" | "insufficient";
  allowInformationGaps: boolean;
  regenerating?: boolean;
  onContentChange: (sectionKey: string, value: string) => void;
  onBlur: (sectionKey: string, value: string) => void;
  onToggleLock: (sectionKey: string, locked: boolean) => void;
  onRegenerate: (sectionKey: string) => void;
}

export function SectionField({
  label,
  sectionKey,
  value,
  locked,
  readiness,
  allowInformationGaps,
  regenerating,
  onContentChange,
  onBlur,
  onToggleLock,
  onRegenerate,
}: SectionFieldProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleInput = useCallback(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = `${el.scrollHeight}px`;
    }
  }, []);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      onContentChange(sectionKey, e.target.value);
    },
    [sectionKey, onContentChange],
  );

  const handleBlur = useCallback(() => {
    onBlur(sectionKey, value);
  }, [sectionKey, value, onBlur]);

  const statusDot = !allowInformationGaps && readiness ? (
    <span
      className={`inline-block h-2 w-2 rounded-full ${
        readiness === "ready" ? "bg-green-500" : "bg-gray-300"
      }`}
      data-testid={`status-dot-${sectionKey}`}
    />
  ) : null;

  return (
    <div className="space-y-1" data-testid={`section-field-${sectionKey}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {statusDot}
          <label className="text-sm font-medium text-foreground">{label}</label>
        </div>
        <div className="flex items-center gap-1">
          {!locked && value && (
            <button
              type="button"
              className="p-1 rounded hover:bg-muted text-muted-foreground"
              onClick={() => onRegenerate(sectionKey)}
              disabled={regenerating}
              title="Regenerate section"
              data-testid={`regenerate-${sectionKey}`}
            >
              {regenerating ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4" />
              )}
            </button>
          )}
          <button
            type="button"
            className="p-1 rounded hover:bg-muted text-muted-foreground"
            onClick={() => onToggleLock(sectionKey, !locked)}
            title={locked ? "Unlock section" : "Lock section"}
            data-testid={`lock-toggle-${sectionKey}`}
          >
            {locked ? (
              <Lock className="h-4 w-4" />
            ) : (
              <LockOpen className="h-4 w-4" />
            )}
          </button>
        </div>
      </div>
      <textarea
        ref={textareaRef}
        className="w-full min-h-20 rounded-md border border-border bg-card px-3 py-2 text-base text-foreground resize-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
        value={value}
        onChange={handleChange}
        onInput={handleInput}
        onBlur={handleBlur}
        data-testid={`section-textarea-${sectionKey}`}
      />
    </div>
  );
}
