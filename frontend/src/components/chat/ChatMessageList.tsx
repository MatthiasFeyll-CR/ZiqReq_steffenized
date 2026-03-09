import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { Lightbulb } from "lucide-react";
import { fetchChatMessages, type ChatMessage } from "@/api/chat";
import { useAuth } from "@/hooks/use-auth";
import type { Idea } from "@/api/ideas";
import { EmptyState } from "@/components/common/EmptyState";
import { UserMessageBubble } from "./UserMessageBubble";
import { AIMessageBubble } from "./AIMessageBubble";
import { DelegationMessage } from "./DelegationMessage";

interface ChatMessageListProps {
  idea: Idea;
}

export function ChatMessageList({ idea }: ChatMessageListProps) {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);
  const prevMessageCountRef = useRef(0);

  const isMultiUser = idea.collaborators.length > 0;

  useEffect(() => {
    let cancelled = false;

    fetchChatMessages(idea.id)
      .then((data) => {
        if (!cancelled) {
          setMessages(data.messages);
          setLoading(false);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [idea.id]);

  useEffect(() => {
    if (messages.length > 0 && messages.length !== prevMessageCountRef.current) {
      bottomRef.current?.scrollIntoView({ behavior: prevMessageCountRef.current === 0 ? "instant" : "smooth" });
    }
    prevMessageCountRef.current = messages.length;
  }, [messages]);

  const getSenderName = (senderId: string | null): string | undefined => {
    if (!senderId) return undefined;
    const collab = idea.collaborators.find((c) => c.user_id === senderId);
    if (collab) return collab.display_name;
    return undefined;
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="motion-safe:animate-spin h-6 w-6 border-2 border-primary border-t-transparent rounded-full" />
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center" data-testid="chat-empty-state">
        <EmptyState
          icon={Lightbulb}
          message={t("chat.emptyState", "Start brainstorming...")}
        />
      </div>
    );
  }

  return (
    <div
      className="flex-1 overflow-y-auto px-4 py-3 space-y-3"
      data-testid="chat-message-list"
    >
      {messages.map((msg) => {
        if (msg.message_type === "delegation") {
          return <DelegationMessage key={msg.id} message={msg} />;
        }
        if (msg.sender_type === "ai") {
          return <AIMessageBubble key={msg.id} message={msg} />;
        }
        return (
          <UserMessageBubble
            key={msg.id}
            message={msg}
            senderName={getSenderName(msg.sender_id)}
            showSenderName={isMultiUser && msg.sender_id !== user?.id}
          />
        );
      })}
      <div ref={bottomRef} />
    </div>
  );
}
