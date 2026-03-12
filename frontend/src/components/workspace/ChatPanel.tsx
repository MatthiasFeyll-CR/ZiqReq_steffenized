import { useCallback, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
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
  const { t } = useTranslation();
  const [newMessages, setNewMessages] = useState<ChatMessage[]>([]);
  const { isLimited } = useRateLimit(idea.id);

  const handleMessageSent = useCallback((message: ChatMessage) => {
    setNewMessages((prev) => [...prev, message]);
  }, []);

  // Listen for incoming AI chat messages via WebSocket
  // User messages are already added from the POST response, so only append AI messages.
  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail.idea_id !== idea.id) return;
      const msg = detail.message as ChatMessage;
      if (msg.sender_type !== "ai") return;
      setNewMessages((prev) => {
        if (prev.some((m) => m.id === msg.id)) return prev;
        return [...prev, msg];
      });
    };
    window.addEventListener("ws:chat_message", handler);
    return () => window.removeEventListener("ws:chat_message", handler);
  }, [idea.id]);

  const isDisabled = locked || isLimited;
  const overlayReason = locked
    ? lockReason
    : isLimited
      ? t("chat.rateLimited")
      : null;

  return (
    <div className="relative flex flex-col flex-1 min-h-0" data-testid="chat-panel-inner">
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
