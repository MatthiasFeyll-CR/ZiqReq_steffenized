import { useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { Lightbulb } from "lucide-react";
import { fetchChatMessages, type ChatMessage } from "@/api/chat";
import { useAuth } from "@/hooks/use-auth";
import type { Project } from "@/api/projects";
import { EmptyState } from "@/components/common/EmptyState";
import { UserMessageBubble } from "./UserMessageBubble";
import { AIMessageBubble } from "./AIMessageBubble";
import { DelegationMessage } from "./DelegationMessage";

interface ChatMessageListProps {
  project: Project;
  appendedMessages?: ChatMessage[];
}

export function ChatMessageList({ project, appendedMessages = [] }: ChatMessageListProps) {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [fetchedMessages, setFetchedMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);
  const prevMessageCountRef = useRef(0);

  const isMultiUser = project.collaborators.length > 0;

  const allMessages = useMemo(() => {
    const fetchedIds = new Set(fetchedMessages.map((m) => m.id));
    const deduped = appendedMessages.filter((m) => !fetchedIds.has(m.id));
    return [...fetchedMessages, ...deduped];
  }, [fetchedMessages, appendedMessages]);

  useEffect(() => {
    let cancelled = false;

    fetchChatMessages(project.id)
      .then((data) => {
        if (!cancelled) {
          setFetchedMessages(data.messages);
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
  }, [project.id]);

  useEffect(() => {
    if (allMessages.length > 0 && allMessages.length !== prevMessageCountRef.current) {
      bottomRef.current?.scrollIntoView({ behavior: prevMessageCountRef.current === 0 ? "instant" : "smooth" });
    }
    prevMessageCountRef.current = allMessages.length;
  }, [allMessages]);

  const getSenderName = (senderId: string | null): string | undefined => {
    if (!senderId) return undefined;
    if (senderId === user?.id) return user.display_name;
    const collab = project.collaborators.find((c) => c.user_id === senderId);
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

  if (allMessages.length === 0) {
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
      className="flex-1 min-h-0 overflow-y-auto px-6 py-3 space-y-3"
      role="log"
      aria-label={t("chat.messageList", "Chat messages")}
      data-testid="chat-message-list"
    >
      {allMessages.map((msg) => {
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
            showSenderName={isMultiUser}
            projectId={project.id}
            isOwnMessage={msg.sender_id === user?.id}
          />
        );
      })}
      <div ref={bottomRef} />
    </div>
  );
}
