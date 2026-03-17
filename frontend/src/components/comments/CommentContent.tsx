import { useMemo } from "react";
import { Link } from "react-router-dom";

interface CommentContentProps {
  content: string;
}

/**
 * Renders comment content with markdown-style bold/italic,
 * @mentions highlighted, and #project-references as clickable links.
 *
 * Reference format in content: [#ProjectTitle](project:uuid)
 * Mention format: @username
 */
export function CommentContent({ content }: CommentContentProps) {
  const parts = useMemo(() => parseContent(content), [content]);

  return (
    <div className="text-sm text-foreground whitespace-pre-wrap break-words leading-relaxed">
      {parts.map((part, i) => {
        switch (part.type) {
          case "text":
            return <span key={i}>{part.value}</span>;
          case "bold":
            return <strong key={i}>{part.value}</strong>;
          case "italic":
            return <em key={i}>{part.value}</em>;
          case "mention":
            return (
              <span
                key={i}
                className="text-primary font-medium bg-primary/10 rounded px-0.5"
              >
                @{part.value}
              </span>
            );
          case "project_ref":
            return (
              <Link
                key={i}
                to={`/project/${part.meta}`}
                className="text-primary font-medium hover:underline"
              >
                #{part.value}
              </Link>
            );
          default:
            return <span key={i}>{part.value}</span>;
        }
      })}
    </div>
  );
}

interface ContentPart {
  type: "text" | "bold" | "italic" | "mention" | "project_ref";
  value: string;
  meta?: string;
}

function parseContent(content: string): ContentPart[] {
  const parts: ContentPart[] = [];
  // Combined regex for bold, italic, project refs, and mentions
  const regex =
    /\*\*(.+?)\*\*|_(.+?)_|\[#(.+?)\]\(project:([0-9a-f-]+)\)|@(\w[\w.\-]*)/g;

  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(content)) !== null) {
    // Text before this match
    if (match.index > lastIndex) {
      parts.push({ type: "text", value: content.slice(lastIndex, match.index) });
    }

    if (match[1] !== undefined) {
      parts.push({ type: "bold", value: match[1] });
    } else if (match[2] !== undefined) {
      parts.push({ type: "italic", value: match[2] });
    } else if (match[3] !== undefined && match[4] !== undefined) {
      parts.push({ type: "project_ref", value: match[3], meta: match[4] });
    } else if (match[5] !== undefined) {
      parts.push({ type: "mention", value: match[5] });
    }

    lastIndex = match.index + match[0].length;
  }

  // Trailing text
  if (lastIndex < content.length) {
    parts.push({ type: "text", value: content.slice(lastIndex) });
  }

  return parts;
}
