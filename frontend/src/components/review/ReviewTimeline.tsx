import { ArrowRight, MessageCircle, RefreshCw, User } from "lucide-react";
import type { TimelineEntry } from "@/api/review";

function formatState(state: string): string {
  return state
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleString();
}

function StateChangeDot({ state }: { state: string | null }) {
  const colorMap: Record<string, string> = {
    in_review: "bg-amber-400",
    accepted: "bg-green-500",
    rejected: "bg-orange-500",
    dropped: "bg-gray-400",
  };
  return (
    <div
      className={`w-2 h-2 mt-2 rounded-full shrink-0 ${colorMap[state ?? ""] ?? "bg-muted-foreground"}`}
    />
  );
}

function StateChangeEntry({ entry }: { entry: TimelineEntry }) {
  return (
    <div className="flex items-start gap-3">
      <StateChangeDot state={entry.new_state} />
      <div>
        <p className="text-sm text-muted-foreground italic">
          {entry.content ||
            `${formatState(entry.old_state || "")} → ${formatState(entry.new_state || "")}`}
        </p>
        {entry.author && (
          <span className="text-xs text-muted-foreground">
            by {entry.author.display_name}
          </span>
        )}
        <time className="block text-xs text-muted-foreground">
          {formatTime(entry.created_at)}
        </time>
      </div>
    </div>
  );
}

function CommentEntry({ entry }: { entry: TimelineEntry }) {
  return (
    <div className="flex items-start gap-3">
      <div className="w-2 h-2 mt-2 rounded-full bg-sky-400 shrink-0" />
      <div className="flex-1 rounded border bg-card p-3">
        <div className="flex items-center gap-2 mb-1">
          <User className="h-3 w-3 text-muted-foreground" />
          <span className="text-sm font-medium">
            {entry.author?.display_name ?? "System"}
          </span>
          <time className="text-xs text-muted-foreground">
            {formatTime(entry.created_at)}
          </time>
        </div>
        <p className="text-sm">{entry.content}</p>
      </div>
    </div>
  );
}

function ResubmissionEntry({ entry }: { entry: TimelineEntry }) {
  return (
    <div className="flex items-start gap-3">
      <div className="w-2 h-2 mt-2 rounded-full bg-primary shrink-0" />
      <div>
        <div className="flex items-center gap-2 text-sm">
          <RefreshCw className="h-3 w-3 text-muted-foreground" />
          <span>Resubmitted</span>
          {entry.old_version_id && entry.new_version_id && (
            <span className="text-muted-foreground flex items-center gap-1">
              <ArrowRight className="h-3 w-3" />
              new version
            </span>
          )}
        </div>
        {entry.author && (
          <span className="text-xs text-muted-foreground">
            by {entry.author.display_name}
          </span>
        )}
        <time className="block text-xs text-muted-foreground">
          {formatTime(entry.created_at)}
        </time>
      </div>
    </div>
  );
}

function TimelineEntryItem({ entry }: { entry: TimelineEntry }) {
  const isNested = !!entry.parent_entry_id;
  const style = isNested ? { marginLeft: 24 } : undefined;

  return (
    <div style={style} data-testid={`timeline-entry-${entry.entry_type}`}>
      {entry.entry_type === "state_change" && <StateChangeEntry entry={entry} />}
      {entry.entry_type === "comment" && <CommentEntry entry={entry} />}
      {entry.entry_type === "resubmission" && <ResubmissionEntry entry={entry} />}
    </div>
  );
}

interface ReviewTimelineProps {
  entries: TimelineEntry[];
}

export function ReviewTimeline({ entries }: ReviewTimelineProps) {
  if (entries.length === 0) {
    return (
      <div className="flex items-center justify-center py-8 text-sm text-muted-foreground" data-testid="timeline-empty">
        <MessageCircle className="h-4 w-4 mr-2" />
        No timeline entries yet
      </div>
    );
  }

  return (
    <div className="relative pl-4 border-l-2 border-border space-y-4" data-testid="review-timeline">
      {entries.map((entry) => (
        <TimelineEntryItem key={entry.id} entry={entry} />
      ))}
    </div>
  );
}
