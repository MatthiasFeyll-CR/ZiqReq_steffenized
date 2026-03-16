import { Loader2 } from "lucide-react";

interface AIProcessingOverlayProps {
  message?: string;
}

export function AIProcessingOverlay({ message = "AI is processing..." }: AIProcessingOverlayProps) {
  return (
    <div
      className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-card/70 backdrop-blur-[2px]"
      data-testid="ai-processing-overlay"
    >
      <div className="flex items-center gap-3 rounded-lg border border-border bg-card px-5 py-3 shadow-md">
        <Loader2 className="h-5 w-5 animate-spin text-primary" />
        <p className="text-sm font-medium text-foreground">{message}</p>
      </div>
    </div>
  );
}
