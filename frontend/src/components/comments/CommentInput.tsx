import { useCallback, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send } from "lucide-react";
import { searchIdeasForReference } from "@/api/comments";
import { cn } from "@/lib/utils";

interface CommentInputProps {
  ideaId: string;
  onSubmit: (content: string) => Promise<void>;
  placeholder?: string;
}

export function CommentInput({
  onSubmit,
  placeholder,
}: CommentInputProps) {
  const [value, setValue] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Autocomplete state
  const [autocomplete, setAutocomplete] = useState<{
    type: "mention" | "idea_ref";
    query: string;
    startPos: number;
    results: Array<{ id: string; display: string }>;
  } | null>(null);
  const [selectedIndex, setSelectedIndex] = useState(0);

  const handleSubmit = useCallback(async () => {
    const trimmed = value.trim();
    if (!trimmed) return;
    setSubmitting(true);
    try {
      await onSubmit(trimmed);
      setValue("");
      setAutocomplete(null);
    } catch {
      // stay with content
    } finally {
      setSubmitting(false);
    }
  }, [value, onSubmit]);

  const applyAutocomplete = useCallback(
    (item: { id: string; display: string }) => {
      if (!autocomplete) return;
      const before = value.slice(0, autocomplete.startPos);
      const after = value.slice(
        autocomplete.startPos + autocomplete.query.length + 1 // +1 for @ or #
      );

      let insertion: string;
      if (autocomplete.type === "mention") {
        insertion = `@${item.display} `;
      } else {
        insertion = `[#${item.display}](idea:${item.id}) `;
      }

      setValue(before + insertion + after);
      setAutocomplete(null);
    },
    [autocomplete, value]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (autocomplete && autocomplete.results.length > 0) {
        if (e.key === "ArrowDown") {
          e.preventDefault();
          setSelectedIndex((i) => Math.min(i + 1, autocomplete.results.length - 1));
          return;
        }
        if (e.key === "ArrowUp") {
          e.preventDefault();
          setSelectedIndex((i) => Math.max(i - 1, 0));
          return;
        }
        if (e.key === "Enter" || e.key === "Tab") {
          e.preventDefault();
          const item = autocomplete.results[selectedIndex];
          if (item) applyAutocomplete(item);
          return;
        }
        if (e.key === "Escape") {
          e.preventDefault();
          setAutocomplete(null);
          return;
        }
      }

      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [autocomplete, selectedIndex, handleSubmit, applyAutocomplete]
  );

  // Detect @mention and #reference triggers on change
  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      const newValue = e.target.value;
      setValue(newValue);

      const cursorPos = e.target.selectionStart || 0;
      const textBefore = newValue.slice(0, cursorPos);

      // Check for @ trigger
      const mentionMatch = textBefore.match(/@(\w[\w.\-]*)$/);
      if (mentionMatch && mentionMatch[1]) {
        const query = mentionMatch[1];
        const startPos = cursorPos - query.length - 1;
        setAutocomplete({
          type: "mention",
          query,
          startPos,
          results: [], // @mentions typed as-is; no user search endpoint exposed
        });
        setSelectedIndex(0);
        return;
      }

      // Check for # trigger
      const hashMatch = textBefore.match(/#([\w\s]{2,})$/);
      if (hashMatch && hashMatch[1]) {
        const query = hashMatch[1];
        const startPos = cursorPos - query.length - 1;
        searchIdeasForReference(query.trim()).then((results) => {
          setAutocomplete({
            type: "idea_ref",
            query,
            startPos,
            results: results.map((r) => ({ id: r.id, display: r.title })),
          });
          setSelectedIndex(0);
        });
        return;
      }

      setAutocomplete(null);
    },
    []
  );

  return (
    <div className="relative">
      {/* Autocomplete dropdown */}
      {autocomplete && autocomplete.results.length > 0 && (
        <div className="absolute bottom-full left-0 right-0 mb-1 bg-surface border border-border rounded-md shadow-lg max-h-40 overflow-y-auto z-50">
          {autocomplete.results.map((item, i) => (
            <button
              key={item.id}
              className={cn(
                "w-full text-left px-3 py-2 text-sm hover:bg-muted transition-colors",
                i === selectedIndex && "bg-muted"
              )}
              onMouseDown={(e) => {
                e.preventDefault();
                applyAutocomplete(item);
              }}
            >
              {autocomplete.type === "idea_ref" ? "#" : "@"}
              {item.display}
            </button>
          ))}
        </div>
      )}

      <div className="flex gap-2 items-end">
        <Textarea
          ref={textareaRef}
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="min-h-[40px] max-h-[120px] text-sm resize-none"
          rows={1}
          disabled={submitting}
          data-testid="comment-input"
        />
        <Button
          size="icon-sm"
          onClick={handleSubmit}
          disabled={!value.trim() || submitting}
          data-testid="comment-submit"
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
