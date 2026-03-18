import { useCallback } from "react";
import { useTranslation } from "react-i18next";
import { FileText, Image, Loader2, X } from "lucide-react";
import { toast } from "react-toastify";
import type { Attachment } from "@/api/attachments";
import { env } from "@/config/env";
import { cn } from "@/lib/utils";

interface AttachmentBoxProps {
  attachment: Attachment;
  projectId: string;
  clickable: boolean;
  onRemove?: () => void;
  showThumbnail?: boolean;
  thumbnailUrl?: string;
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function isImageType(contentType: string): boolean {
  return contentType.startsWith("image/");
}

const DEFAULT_TTL_HOURS = 96;

export function AttachmentBox({
  attachment,
  projectId,
  clickable,
  onRemove,
  showThumbnail,
  thumbnailUrl,
}: AttachmentBoxProps) {
  const { t } = useTranslation();
  const isDeleted = !!attachment.deleted_at;

  const hoursUntilPermanentDelete = (() => {
    if (!attachment.deleted_at) return 0;
    const deadline = new Date(attachment.deleted_at).getTime() + DEFAULT_TTL_HOURS * 60 * 60 * 1000;
    return Math.max(0, Math.round((deadline - Date.now()) / (60 * 60 * 1000)));
  })();

  const handleClick = useCallback(() => {
    if (isDeleted) {
      toast.info(
        t(
          "attachment.deletedClickPrompt",
          "This attachment has been deleted. Restore it in the attachment modal. Permanently deleted in {{hours}} hours.",
          { hours: hoursUntilPermanentDelete },
        ),
      );
      return;
    }
    if (!clickable) {
      toast.info(t("attachment.readOnlyBlocked", "Download not available in read-only mode"));
      return;
    }
    const url = `${env.apiBaseUrl}/projects/${projectId}/attachments/${attachment.id}/download/`;
    window.open(url, "_blank");
  }, [isDeleted, clickable, projectId, attachment.id, t, hoursUntilPermanentDelete]);

  const isImage = isImageType(attachment.content_type);
  const Icon = isImage ? Image : FileText;

  const isPending =
    attachment.extraction_status === "pending" || attachment.extraction_status === "processing";
  const isFailed = attachment.extraction_status === "failed";

  return (
    <div
      className={cn(
        "relative group flex items-center gap-2 rounded-md border px-2 py-1.5 text-sm max-w-[200px]",
        isDeleted
          ? "border-red-300 bg-red-50 dark:border-red-800 dark:bg-red-950/30 cursor-pointer"
          : clickable
            ? "border-border bg-muted/50 cursor-pointer hover:bg-muted"
            : "border-border bg-muted/50 cursor-not-allowed opacity-80",
      )}
      title={isDeleted ? t("attachment.deletedTitle", "Deleted — permanently removed in {{hours}}h", { hours: hoursUntilPermanentDelete }) : undefined}
      onClick={handleClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          void handleClick();
        }
      }}
      data-testid="attachment-box"
    >
      {showThumbnail && isImage && thumbnailUrl ? (
        <img
          src={thumbnailUrl}
          alt={attachment.filename}
          className="h-12 w-12 rounded object-cover flex-shrink-0"
          data-testid="attachment-thumbnail"
        />
      ) : (
        <Icon className="h-4 w-4 flex-shrink-0 text-muted-foreground" />
      )}
      <div className="min-w-0 flex-1">
        <p className={cn("truncate text-xs font-medium", isDeleted && "line-through text-red-700 dark:text-red-400")} title={attachment.filename}>
          {attachment.filename}
        </p>
        <div className="flex items-center gap-1">
          <span className="text-[10px] text-muted-foreground">{formatSize(attachment.size_bytes)}</span>
          {isPending && (
            <span className="flex items-center gap-0.5 text-[10px] text-muted-foreground animate-pulse" data-testid="attachment-processing">
              <Loader2 className="h-2.5 w-2.5 animate-spin" />
              {t("attachment.processing", "Processing...")}
            </span>
          )}
          {isFailed && (
            <span className="text-[10px] text-muted-foreground/60" data-testid="attachment-failed">
              {t("attachment.extractionFailed", "Extraction failed")}
            </span>
          )}
        </div>
      </div>
      {onRemove && (
        <button
          type="button"
          className="absolute -top-1.5 -right-1.5 rounded-full bg-destructive text-destructive-foreground p-0.5 opacity-0 group-hover:opacity-100 transition-opacity"
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          aria-label={t("attachment.remove", "Remove attachment")}
          data-testid="attachment-remove"
        >
          <X className="h-3 w-3" />
        </button>
      )}
    </div>
  );
}
