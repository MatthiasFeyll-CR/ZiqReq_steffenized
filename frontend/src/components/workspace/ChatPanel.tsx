import { useCallback, useState } from "react";
import { LockOverlay } from "./LockOverlay";
import { ChatMessageList } from "@/components/chat/ChatMessageList";
import { ChatInput } from "@/components/chat/ChatInput";
import type { Idea } from "@/api/ideas";
import type { ChatMessage } from "@/api/chat";

interface ChatPanelProps {
  idea: Idea;
  locked: boolean;
  lockReason: string | null;
}

export function ChatPanel({ idea, locked, lockReason }: ChatPanelProps) {
  const [newMessages, setNewMessages] = useState<ChatMessage[]>([]);

  const handleMessageSent = useCallback((message: ChatMessage) => {
    setNewMessages((prev) => [...prev, message]);
  }, []);

  return (
    <div className="relative flex flex-col flex-1" data-testid="chat-panel-inner">
      <ChatMessageList idea={idea} appendedMessages={newMessages} />
      <ChatInput
        ideaId={idea.id}
        onMessageSent={handleMessageSent}
        disabled={locked}
      />
      {locked && lockReason && <LockOverlay reason={lockReason} />}
    </div>
  );
}
