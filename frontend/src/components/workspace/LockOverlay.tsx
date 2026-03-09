import { Lock } from "lucide-react";

interface LockOverlayProps {
  reason: string;
}

export function LockOverlay({ reason }: LockOverlayProps) {
  return (
    <div
      className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-3 bg-card/80"
      data-testid="lock-overlay"
    >
      <Lock className="h-8 w-8 text-muted-foreground" />
      <p className="text-sm text-muted-foreground text-center max-w-xs">
        {reason}
      </p>
    </div>
  );
}
