import { useCallback, useState } from "react";
import { LockOverlay } from "./LockOverlay";
import { ChatMessageList } from "@/components/chat/ChatMessageList";
import { ChatInput } from "@/components/chat/ChatInput";
import { AIProcessingIndicator } from "@/components/chat/AIProcessingIndicator";
import { useRateLimit } from "@/hooks/useRateLimit";
import type { Idea } from "@/api/ideas";
import type { ChatMessage } from "@/api/chat";

interface ChatPanelProps {
  idea: Idea;
  locked: boolean;
  lockReason: string | null;
  readOnly?: boolean;
}

export function ChatPanel({ idea, locked, lockReason, readOnly }: ChatPanelProps) {
  const [newMessages, setNewMessages] = useState<ChatMessage[]>([]);
  const { isLimited } = useRateLimit(idea.id);

  const handleMessageSent = useCallback((message: ChatMessage) => {
    setNewMessages((prev) => [...prev, message]);
  }, []);

  const isDisabled = locked || isLimited;
  const overlayReason = locked
    ? lockReason
    : isLimited
      ? "Chat locked"
      : null;

  return (
    <div className="relative flex flex-col flex-1" data-testid="chat-panel-inner">
      <ChatMessageList idea={idea} appendedMessages={newMessages} />
      <AIProcessingIndicator ideaId={idea.id} />
      {readOnly ? (
        <div className="px-4 py-3 text-sm text-muted-foreground border-t text-center" data-testid="chat-read-only-notice">
          Viewing shared idea — chat is read-only
        </div>
      ) : (
        <ChatInput
          ideaId={idea.id}
          idea={idea}
          onMessageSent={handleMessageSent}
          disabled={isDisabled}
        />
      )}
      {!readOnly && isDisabled && overlayReason && <LockOverlay reason={overlayReason} />}
    </div>
  );
}
