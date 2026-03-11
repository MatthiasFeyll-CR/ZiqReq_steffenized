import { useState } from "react";
import { Send, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface CommentInputProps {
  onSubmit: (content: string) => void;
  isPending?: boolean;
  placeholder?: string;
  autoFocus?: boolean;
  onCancel?: () => void;
}

export function CommentInput({
  onSubmit,
  isPending,
  placeholder = "Add a comment...",
  autoFocus,
  onCancel,
}: CommentInputProps) {
  const [content, setContent] = useState("");

  const handleSubmit = () => {
    const trimmed = content.trim();
    if (!trimmed) return;
    onSubmit(trimmed);
    setContent("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmit();
    }
    if (e.key === "Escape" && onCancel) {
      onCancel();
    }
  };

  return (
    <div className="flex gap-2 items-end" data-testid="comment-input">
      <Textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        autoFocus={autoFocus}
        className="min-h-[60px] resize-none"
        disabled={isPending}
        data-testid="comment-textarea"
      />
      <div className="flex flex-col gap-1">
        <Button
          size="icon"
          variant="primary"
          onClick={handleSubmit}
          disabled={!content.trim() || isPending}
          data-testid="comment-send-button"
        >
          {isPending ? (
            <Loader2 className="h-4 w-4 motion-safe:animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}
        </Button>
        {onCancel && (
          <Button
            size="icon"
            variant="ghost"
            onClick={onCancel}
            disabled={isPending}
            data-testid="comment-cancel-button"
          >
            &times;
          </Button>
        )}
      </div>
    </div>
  );
}
