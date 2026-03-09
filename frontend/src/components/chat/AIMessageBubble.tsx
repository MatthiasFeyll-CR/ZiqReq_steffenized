import type { ChatMessage } from "@/api/chat";
import { cn } from "@/lib/utils";
import { Bot } from "lucide-react";

interface AIMessageBubbleProps {
  message: ChatMessage;
}

export function AIMessageBubble({ message }: AIMessageBubbleProps) {
  const timestamp = new Date(message.created_at).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className="flex flex-col items-start" data-testid="ai-message-bubble">
      <div className="flex items-center gap-1 mb-1">
        <Bot className="h-3 w-3 text-muted-foreground" />
        <span className="text-xs text-muted-foreground">AI</span>
      </div>
      <div
        className={cn(
          "max-w-[70%] rounded-md rounded-tl-sm",
          "bg-card border border-border",
          "px-3 py-2",
        )}
      >
        <p className="whitespace-pre-wrap break-words text-card-foreground">
          {message.content}
        </p>
        <span className="block text-right text-[10px] opacity-70 mt-1">
          {timestamp}
        </span>
      </div>
    </div>
  );
}
