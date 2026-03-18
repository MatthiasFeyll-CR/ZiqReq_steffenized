import { useCallback, useState } from "react";
import { useTranslation } from "react-i18next";
import { FileText, Image, X, Loader2 } from "lucide-react";
import { toast } from "react-toastify";
import { getAttachmentUrl } from "@/api/attachments";
import type { Attachment } from "@/api/attachments";
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
  const [loading, setLoading] = useState(false);

  const handleClick = useCallback(async () => {
    if (!clickable) {
      toast.info(t("attachment.readOnlyBlocked", "Download not available in read-only mode"));
      return;
    }
    if (loading) return;
    setLoading(true);
    try {
      const url = await getAttachmentUrl(projectId, attachment.id);
      window.open(url, "_blank");
    } catch {
      toast.error(t("attachment.downloadFailed", "Download failed"));
    } finally {
      setLoading(false);
    }
  }, [clickable, loading, projectId, attachment.id, t]);

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
      {loading && <Loader2 className="h-3 w-3 animate-spin text-muted-foreground" />}
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
