import { LockOverlay } from "./LockOverlay";
import { ChatMessageList } from "@/components/chat/ChatMessageList";
import type { Idea } from "@/api/ideas";

interface ChatPanelProps {
  idea: Idea;
  locked: boolean;
  lockReason: string | null;
}

export function ChatPanel({ idea, locked, lockReason }: ChatPanelProps) {
  return (
    <div className="relative flex flex-col flex-1" data-testid="chat-panel-inner">
      <ChatMessageList idea={idea} />
      {locked && lockReason && <LockOverlay reason={lockReason} />}
    </div>
  );
}
