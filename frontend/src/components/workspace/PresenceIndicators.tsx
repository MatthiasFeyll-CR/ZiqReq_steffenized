import { useSelector } from "react-redux";
import {
  selectProjectPresence,
  type PresenceUser,
} from "@/store/presence-slice";
import {
  Avatar,
  AvatarFallback,
  getInitials,
} from "@/components/ui/avatar";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

const MAX_VISIBLE = 4;

function statusLabel(state: PresenceUser["state"]): string {
  if (state === "online") return "Online";
  if (state === "idle") return "Idle";
  return "Offline";
}

function StatusBadge({ state }: { state: PresenceUser["state"] }) {
  return (
    <span
      className={cn(
        "absolute bottom-0 right-0 block h-2 w-2 rounded-full ring-2 ring-card",
        state === "online" && "bg-success",
        state === "idle" && "bg-warning",
        state === "offline" && "bg-muted",
      )}
    />
  );
}

function PresenceAvatar({
  user,
  className,
}: {
  user: PresenceUser;
  className?: string;
}) {
  const initials = getInitials(
    user.display_name.split(" ")[0],
    user.display_name.split(" ")[1],
  );

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className={cn("relative", className)}>
            <Avatar
              size="sm"
              className={cn(
                "border-2 border-card",
                user.state === "idle" && "opacity-50 grayscale",
              )}
            >
              <AvatarFallback userId={user.user_id}>{initials}</AvatarFallback>
            </Avatar>
            <StatusBadge state={user.state} />
          </div>
        </TooltipTrigger>
        <TooltipContent>
          <p>
            {user.display_name} &middot; {statusLabel(user.state)}
          </p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

interface PresenceIndicatorsProps {
  projectId: string;
}

export function PresenceIndicators({ projectId }: PresenceIndicatorsProps) {
  const presence = useSelector(selectProjectPresence(projectId));

  if (presence.length === 0) return null;

  const visible = presence.slice(0, MAX_VISIBLE);
  const overflow = presence.length - MAX_VISIBLE;

  return (
    <div
      className="shrink-0 flex items-center"
      role="group"
      aria-label="Active users"
      data-testid="presence-indicators"
    >
      {visible.map((user, i) => (
        <PresenceAvatar
          key={user.user_id}
          user={user}
          className={i > 0 ? "-ml-2" : undefined}
        />
      ))}
      {overflow > 0 && (
        <div
          className="-ml-2 flex h-8 w-8 items-center justify-center rounded-full bg-muted text-muted-foreground text-xs border-2 border-card"
          data-testid="presence-overflow"
        >
          +{overflow}
        </div>
      )}
    </div>
  );
}
