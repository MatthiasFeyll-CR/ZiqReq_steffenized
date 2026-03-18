import type { ChatMessage } from "@/api/chat";
import { cn } from "@/lib/utils";
import { ReactionChips } from "./ReactionChips";
import { AttachmentBox } from "./AttachmentBox";

interface UserMessageBubbleProps {
  message: ChatMessage;
  senderName?: string;
  showSenderName: boolean;
  projectId: string;
  isOwnMessage: boolean;
  isReadOnly?: boolean;
}

export function UserMessageBubble({
  message,
  senderName,
  showSenderName,
  projectId,
  isOwnMessage,
  isReadOnly,
}: UserMessageBubbleProps) {
  const timestamp = new Date(message.created_at).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  const attachments = message.attachments ?? [];

  return (
    <div
      className={cn("group flex flex-col", isOwnMessage ? "items-end" : "items-start")}
      data-testid="user-message-bubble"
    >
      {showSenderName && senderName && !isOwnMessage && (
        <span className="text-xs text-muted-foreground mb-0.5 ml-1">
          {senderName}
        </span>
      )}
      <div
        className={cn(
          "max-w-[70%] rounded-md px-3 py-2",
          isOwnMessage
            ? "rounded-tr-sm bg-secondary text-secondary-foreground"
            : "rounded-tl-sm bg-card border border-border text-card-foreground",
        )}
      >
        <p className="whitespace-pre-wrap break-words">{message.content}</p>
        {attachments.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2" data-testid="message-attachments">
            {attachments.map((att) => (
              <AttachmentBox
                key={att.id}
                attachment={att}
                projectId={projectId}
                clickable={!isReadOnly}
                showThumbnail={att.content_type.startsWith("image/")}
              />
            ))}
          </div>
        )}
        <span className="block text-right text-[10px] opacity-70 mt-1">
          {timestamp}
        </span>
      </div>
      {showSenderName && senderName && isOwnMessage && (
        <span className="text-xs text-muted-foreground mt-0.5 mr-1">
          {senderName}
        </span>
      )}
      {!isOwnMessage && (
        <ReactionChips projectId={projectId} messageId={message.id} />
      )}
    </div>
  );
}
