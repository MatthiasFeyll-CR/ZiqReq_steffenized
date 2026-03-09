import { useTranslation } from "react-i18next";
import { LockOverlay } from "./LockOverlay";

interface ChatPanelProps {
  locked: boolean;
  lockReason: string | null;
}

export function ChatPanel({ locked, lockReason }: ChatPanelProps) {
  const { t } = useTranslation();

  return (
    <div className="relative flex flex-col flex-1" data-testid="chat-panel-inner">
      <div className="flex-1 flex items-center justify-center text-muted-foreground">
        {t("workspace.chatPlaceholder", "Chat")}
      </div>
      {locked && lockReason && <LockOverlay reason={lockReason} />}
    </div>
  );
}
