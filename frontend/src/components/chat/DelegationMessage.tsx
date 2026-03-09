import type { ChatMessage } from "@/api/chat";
import { Bot } from "lucide-react";

interface DelegationMessageProps {
  message: ChatMessage;
}

export function DelegationMessage({ message }: DelegationMessageProps) {
  const timestamp = new Date(message.created_at).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div
      className="flex flex-col items-start opacity-60"
      data-testid="delegation-message"
    >
      <div className="flex items-center gap-1 mb-1">
        <Bot className="h-3 w-3 text-muted-foreground" />
        <span className="text-xs text-muted-foreground">AI</span>
      </div>
      <div className="max-w-[70%] px-3 py-2 border border-border/50 rounded-md rounded-tl-sm">
        <p className="whitespace-pre-wrap break-words text-sm italic text-card-foreground">
          {message.content}
        </p>
        <span className="block text-right text-[10px] opacity-70 mt-1">
          {timestamp}
        </span>
      </div>
    </div>
  );
}
