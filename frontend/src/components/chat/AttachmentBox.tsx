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

export function AttachmentBox({
  attachment,
  projectId,
  clickable,
  onRemove,
  showThumbnail,
  thumbnailUrl,
}: AttachmentBoxProps) {
  const { t } = useTranslation();

  const handleClick = useCallback(() => {
    if (!clickable) {
      toast.info(t("attachment.readOnlyBlocked", "Download not available in read-only mode"));
      return;
    }
    const url = `${env.apiBaseUrl}/projects/${projectId}/attachments/${attachment.id}/download/`;
    window.open(url, "_blank");
  }, [clickable, projectId, attachment.id, t]);

  const isImage = isImageType(attachment.content_type);
  const Icon = isImage ? Image : FileText;

  const isPending =
    attachment.extraction_status === "pending" || attachment.extraction_status === "processing";
  const isFailed = attachment.extraction_status === "failed";

  return (
    <div
      className={cn(
        "relative group flex items-center gap-2 rounded-md border border-border bg-muted/50 px-2 py-1.5 text-sm max-w-[200px]",
        clickable ? "cursor-pointer hover:bg-muted" : "cursor-not-allowed opacity-80",
      )}
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
        <p className="truncate text-xs font-medium" title={attachment.filename}>
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
