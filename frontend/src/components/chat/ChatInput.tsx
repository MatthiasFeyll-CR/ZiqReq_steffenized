import { useCallback, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { ArrowRight, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { sendChatMessage, type ChatMessage } from "@/api/chat";

interface ChatInputProps {
  ideaId: string;
  onMessageSent: (message: ChatMessage) => void;
  disabled?: boolean;
}

export function ChatInput({ ideaId, onMessageSent, disabled }: ChatInputProps) {
  const { t } = useTranslation();
  const [value, setValue] = useState("");
  const [sending, setSending] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const canSend = value.trim().length > 0 && !sending && !disabled;

  const resetHeight = useCallback(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
    }
  }, []);

  const handleInput = useCallback(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = `${el.scrollHeight}px`;
    }
  }, []);

  const handleSend = useCallback(async () => {
    const content = value.trim();
    if (!content || sending || disabled) return;

    setSending(true);
    try {
      const message = await sendChatMessage(ideaId, content);
      setValue("");
      resetHeight();
      onMessageSent(message);
    } catch {
      // Error handling will be enhanced in future stories
    } finally {
      setSending(false);
      textareaRef.current?.focus();
    }
  }, [value, sending, disabled, ideaId, onMessageSent, resetHeight]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        if (canSend) {
          void handleSend();
        }
      }
    },
    [canSend, handleSend],
  );

  return (
    <div className="border-t bg-card p-3 flex items-end gap-2" data-testid="chat-input">
      <div
        className="w-5 h-5 rounded-full border border-muted-foreground flex-shrink-0 mb-1.5"
        title={t("chat.contextPlaceholder", "Context tracking (M7)")}
      />
      <textarea
        ref={textareaRef}
        className="flex-1 min-h-10 max-h-40 rounded-md border border-border bg-background px-3 py-2 text-base text-foreground placeholder:text-text-secondary resize-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
        rows={1}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onInput={handleInput}
        onKeyDown={handleKeyDown}
        placeholder={t("chat.inputPlaceholder", "Type a message...")}
        disabled={sending || disabled}
        data-testid="chat-input-textarea"
      />
      <Button
        variant="primary"
        size="icon"
        onClick={() => void handleSend()}
        disabled={!canSend}
        aria-label={t("chat.send", "Send")}
        data-testid="chat-send-button"
        className="flex-shrink-0"
      >
        {sending ? (
          <Loader2 className="h-4 w-4 motion-safe:animate-spin" />
        ) : (
          <ArrowRight className="h-4 w-4" />
        )}
      </Button>
    </div>
  );
}
