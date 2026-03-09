import type { ChatMessage } from "@/api/chat";
import { cn } from "@/lib/utils";

interface UserMessageBubbleProps {
  message: ChatMessage;
  senderName?: string;
  showSenderName: boolean;
}

export function UserMessageBubble({
  message,
  senderName,
  showSenderName,
}: UserMessageBubbleProps) {
  const timestamp = new Date(message.created_at).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className="flex flex-col items-end" data-testid="user-message-bubble">
      <div
        className={cn(
          "max-w-[70%] rounded-md rounded-tr-sm",
          "bg-secondary text-secondary-foreground",
          "px-3 py-2",
        )}
      >
        <p className="whitespace-pre-wrap break-words">{message.content}</p>
        <span className="block text-right text-[10px] opacity-70 mt-1">
          {timestamp}
        </span>
      </div>
      {showSenderName && senderName && (
        <span className="text-xs text-muted-foreground mt-0.5 mr-1">
          {senderName}
        </span>
      )}
    </div>
  );
}
