import { Eye } from "lucide-react";

export function ReadOnlyBanner() {
  return (
    <div
      className="border-b bg-primary/5 px-4 py-3 border-l-4 border-primary flex items-center gap-2"
      data-testid="read-only-banner"
    >
      <Eye className="h-4 w-4 text-primary" />
      <span className="text-sm text-muted-foreground">
        Viewing shared idea (read-only)
      </span>
    </div>
  );
}
