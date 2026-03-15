import { useTranslation } from "react-i18next";

interface QuickReplyChipsProps {
  onSelect: (text: string) => void;
  disabled?: boolean;
}

const QUICK_REPLIES = [
  { key: "similarIdea", i18nKey: "chat.quickReplies.similarIdea" },
] as const;

export function QuickReplyChips({ onSelect, disabled }: QuickReplyChipsProps) {
  const { t } = useTranslation();

  return (
    <div className="flex flex-wrap gap-2 px-6 pt-3 pb-1" data-testid="quick-reply-chips">
      {QUICK_REPLIES.map((chip) => (
        <button
          key={chip.key}
          type="button"
          disabled={disabled}
          onClick={() => onSelect(t(chip.i18nKey))}
          className="inline-flex items-center gap-1.5 rounded-full border border-border bg-background px-3 py-1.5 text-sm text-foreground shadow-sm transition-all hover:bg-accent hover:text-accent-foreground hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-1 active:scale-[0.97] disabled:pointer-events-none disabled:opacity-50"
          data-testid={`quick-reply-${chip.key}`}
        >
          <span className="text-muted-foreground text-xs">?</span>
          {t(chip.i18nKey)}
        </button>
      ))}
    </div>
  );
}
