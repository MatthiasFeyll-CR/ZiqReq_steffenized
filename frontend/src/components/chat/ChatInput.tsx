import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { ArrowRight, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { sendChatMessage, type ChatMessage } from "@/api/chat";
import { MentionDropdown, type MentionItem } from "./MentionDropdown";
import { ContextWindowIndicator } from "./ContextWindowIndicator";
import { QuickReplyChips } from "./QuickReplyChips";
import type { Idea } from "@/api/ideas";

interface ChatInputProps {
  ideaId: string;
  idea?: Idea;
  onMessageSent: (message: ChatMessage) => void;
  disabled?: boolean;
}

export function ChatInput({ ideaId, idea, onMessageSent, disabled }: ChatInputProps) {
  const { t } = useTranslation();
  const [value, setValue] = useState("");
  const [sending, setSending] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Mention state
  const [mentionOpen, setMentionOpen] = useState(false);
  const [mentionQuery, setMentionQuery] = useState("");
  const [mentionAtPos, setMentionAtPos] = useState(-1);
  const [mentionActiveIndex, setMentionActiveIndex] = useState(0);

  const canSend = value.trim().length > 0 && !sending && !disabled;

  // Build mention items: @ai first, then collaborators alphabetically
  const allMentionItems: MentionItem[] = useMemo(() => {
    const aiItem: MentionItem = { id: "ai", display_name: "ai", isAi: true };
    const collaborators: MentionItem[] = (idea?.collaborators ?? [])
      .slice()
      .sort((a, b) => a.display_name.localeCompare(b.display_name))
      .map((c) => ({ id: c.user_id, display_name: c.display_name }));
    return [aiItem, ...collaborators];
  }, [idea?.collaborators]);

  const filteredMentionItems = useMemo(() => {
    if (!mentionQuery) return allMentionItems;
    const q = mentionQuery.toLowerCase();
    return allMentionItems.filter((item) =>
      item.display_name.toLowerCase().includes(q),
    );
  }, [allMentionItems, mentionQuery]);

  // Reset active index when filtered items change
  useEffect(() => {
    setMentionActiveIndex(0);
  }, [filteredMentionItems.length]);

  const closeMention = useCallback(() => {
    setMentionOpen(false);
    setMentionQuery("");
    setMentionAtPos(-1);
    setMentionActiveIndex(0);
  }, []);

  const insertMention = useCallback(
    (item: MentionItem) => {
      const el = textareaRef.current;
      if (!el || mentionAtPos < 0) return;

      const before = value.slice(0, mentionAtPos);
      const after = value.slice(mentionAtPos + 1 + mentionQuery.length);
      const mention = `@${item.display_name} `;
      const newValue = before + mention + after;
      setValue(newValue);
      closeMention();

      // Set cursor after inserted mention
      requestAnimationFrame(() => {
        const cursorPos = before.length + mention.length;
        el.setSelectionRange(cursorPos, cursorPos);
        el.focus();
      });
    },
    [value, mentionAtPos, mentionQuery, closeMention],
  );

  const resetHeight = useCallback(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.overflowY = "hidden";
    }
  }, []);

  const MAX_TEXTAREA_HEIGHT = 168; // ~7 rows

  const handleInput = useCallback(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      const newHeight = Math.min(el.scrollHeight, MAX_TEXTAREA_HEIGHT);
      el.style.height = `${newHeight}px`;
      el.style.overflowY = el.scrollHeight > MAX_TEXTAREA_HEIGHT ? "auto" : "hidden";
    }
  }, []);

  const handleSend = useCallback(async () => {
    const content = value.trim();
    if (!content || sending || disabled) return;

    closeMention();
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
  }, [value, sending, disabled, ideaId, onMessageSent, resetHeight, closeMention]);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      const newValue = e.target.value;
      setValue(newValue);

      const el = e.target;
      const cursorPos = el.selectionStart;

      // Check for @ trigger: find the last @ before cursor that starts a word
      const textBeforeCursor = newValue.slice(0, cursorPos);
      const atMatch = textBeforeCursor.match(/(^|[\s])@([^\s]*)$/);

      if (atMatch) {
        const atIndex = textBeforeCursor.lastIndexOf("@");
        setMentionAtPos(atIndex);
        setMentionQuery(atMatch[2] ?? "");
        setMentionOpen(true);
      } else {
        if (mentionOpen) closeMention();
      }
    },
    [mentionOpen, closeMention],
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (mentionOpen && filteredMentionItems.length > 0) {
        if (e.key === "ArrowDown") {
          e.preventDefault();
          setMentionActiveIndex((prev) =>
            prev < filteredMentionItems.length - 1 ? prev + 1 : 0,
          );
          return;
        }
        if (e.key === "ArrowUp") {
          e.preventDefault();
          setMentionActiveIndex((prev) =>
            prev > 0 ? prev - 1 : filteredMentionItems.length - 1,
          );
          return;
        }
        if (e.key === "Enter") {
          e.preventDefault();
          const selected = filteredMentionItems[mentionActiveIndex];
          if (selected) insertMention(selected);
          return;
        }
        if (e.key === "Escape") {
          e.preventDefault();
          closeMention();
          return;
        }
      }

      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        if (canSend) {
          void handleSend();
        }
      }
    },
    [
      mentionOpen,
      filteredMentionItems,
      mentionActiveIndex,
      insertMention,
      closeMention,
      canSend,
      handleSend,
    ],
  );

  const handleQuickReply = useCallback(
    (text: string) => {
      setValue(text);
      // Auto-resize textarea after setting value
      requestAnimationFrame(() => {
        handleInput();
        textareaRef.current?.focus();
      });
    },
    [handleInput],
  );

  // Close mention on click outside
  useEffect(() => {
    if (!mentionOpen) return;
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        closeMention();
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [mentionOpen, closeMention]);

  // Calculate dropdown position
  const dropdownPosition = useMemo(() => {
    // Position above the input area
    return { bottom: 4, left: 32 };
  }, []);

  return (
    <div ref={containerRef} className="relative border-t bg-card" data-testid="chat-input">
      {!disabled && value.trim().length === 0 && (
        <QuickReplyChips onSelect={handleQuickReply} disabled={disabled} />
      )}
      <div className="flex items-end gap-2 px-6 py-4">
      <ContextWindowIndicator ideaId={ideaId} ideaState={idea?.state ?? "open"} />
      <div className="relative flex-1">
        {mentionOpen && (
          <MentionDropdown
            items={filteredMentionItems}
            activeIndex={mentionActiveIndex}
            onSelect={insertMention}
            position={dropdownPosition}
          />
        )}
        <textarea
          ref={textareaRef}
          className="w-full min-h-10 max-h-[10.5rem] overflow-y-auto rounded-md border border-border bg-background px-3 py-2 text-base text-foreground placeholder:text-text-secondary resize-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          rows={1}
          value={value}
          onChange={handleChange}
          onInput={handleInput}
          onKeyDown={handleKeyDown}
          placeholder={t("chat.inputPlaceholder", "Type a message...")}
          aria-label={t("chat.inputPlaceholder", "Type a message...")}
          disabled={sending || disabled}
          data-testid="chat-input-textarea"
        />
      </div>
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
    </div>
  );
}
