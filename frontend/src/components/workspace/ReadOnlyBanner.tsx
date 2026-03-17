import { Eye } from "lucide-react";

export function ReadOnlyBanner() {
  return (
    <div
      className="shrink-0 border-b border-l-4 border-l-primary bg-primary/5 px-6 py-3 flex items-center gap-3"
      role="status"
      aria-live="polite"
      data-testid="read-only-banner"
    >
      <Eye className="h-4 w-4 text-primary" />
      <span className="text-sm text-muted-foreground">
        Viewing shared project (read-only)
      </span>
    </div>
  );
}
