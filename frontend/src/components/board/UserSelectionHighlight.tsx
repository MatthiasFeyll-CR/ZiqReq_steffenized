import type { ReactNode } from "react";
import { getUserColor } from "@/store/selections-slice";

interface UserSelectionHighlightProps {
  selectedBy: { user_id: string; display_name: string } | null;
  children: ReactNode;
}

export function UserSelectionHighlight({
  selectedBy,
  children,
}: UserSelectionHighlightProps) {
  if (!selectedBy) return <>{children}</>;

  const color = getUserColor(selectedBy.user_id);

  return (
    <div className="relative" data-testid="user-selection-highlight">
      {/* Name label above node */}
      <div
        className="absolute -top-5 left-0 z-10 whitespace-nowrap rounded px-1 py-0.5 text-[10px] font-medium leading-none text-white"
        style={{ backgroundColor: color }}
        data-testid="selection-user-label"
      >
        {selectedBy.display_name}
      </div>
      {/* Colored border wrapper */}
      <div
        className="rounded-md"
        style={{
          boxShadow: `0 0 0 2px ${color}`,
        }}
      >
        {children}
      </div>
    </div>
  );
}
