import { useEffect, useRef } from "react";
import { Bot } from "lucide-react";
import { cn } from "@/lib/utils";

export interface MentionItem {
  id: string;
  display_name: string;
  isAi?: boolean;
}

interface MentionDropdownProps {
  items: MentionItem[];
  activeIndex: number;
  onSelect: (item: MentionItem) => void;
  position: { bottom: number; left: number };
}

export function MentionDropdown({
  items,
  activeIndex,
  onSelect,
  position,
}: MentionDropdownProps) {
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const active = listRef.current?.children[activeIndex] as HTMLElement | undefined;
    active?.scrollIntoView({ block: "nearest" });
  }, [activeIndex]);

  if (items.length === 0) return null;

  return (
    <div
      ref={listRef}
      className="absolute z-50 max-h-48 overflow-y-auto rounded-md border bg-popover shadow-lg"
      role="listbox"
      aria-label="Mentions"
      style={{ bottom: position.bottom, left: position.left }}
      data-testid="mention-dropdown"
    >
      {items.map((item, index) => (
        <button
          key={item.id}
          type="button"
          role="option"
          aria-selected={index === activeIndex}
          className={cn(
            "flex w-full items-center gap-2 px-3 py-2 text-sm text-popover-foreground",
            index === activeIndex && "bg-muted",
          )}
          onMouseDown={(e) => {
            e.preventDefault();
            onSelect(item);
          }}
          data-testid={`mention-item-${item.id}`}
        >
          {item.isAi ? (
            <Bot className="h-4 w-4 flex-shrink-0" />
          ) : (
            <span className="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-secondary text-[10px] text-secondary-foreground">
              {item.display_name
                .split(" ")
                .map((w) => w[0])
                .join("")
                .slice(0, 2)
                .toUpperCase()}
            </span>
          )}
          <span>{item.display_name}</span>
        </button>
      ))}
    </div>
  );
}
