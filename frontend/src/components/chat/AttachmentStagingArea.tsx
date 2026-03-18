import { useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import { X, FileText } from "lucide-react";
import type { PendingUpload } from "@/hooks/use-attachment-upload";

interface AttachmentStagingAreaProps {
  items: PendingUpload[];
  onRemove: (id: string) => void;
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function StagedItem({ item, onRemove }: { item: PendingUpload; onRemove: () => void }) {
  const { t } = useTranslation();
  const objectUrlRef = useRef<string | null>(null);
  const isImage = item.file.type.startsWith("image/");

  useEffect(() => {
    if (isImage) {
      objectUrlRef.current = URL.createObjectURL(item.file);
    }
    return () => {
      if (objectUrlRef.current) {
        URL.revokeObjectURL(objectUrlRef.current);
        objectUrlRef.current = null;
      }
    };
  }, [item.file, isImage]);

  return (
    <div
      className="relative flex items-center gap-2 rounded-md border border-border bg-muted/50 px-3 py-2 text-sm"
      data-testid="staged-attachment"
    >
      {isImage && objectUrlRef.current ? (
        <img
          src={objectUrlRef.current}
          alt={item.file.name}
          className="h-12 w-12 rounded object-cover flex-shrink-0"
        />
      ) : (
        <FileText className="h-5 w-5 flex-shrink-0 text-muted-foreground" />
      )}
      {!isImage && !objectUrlRef.current && null}
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium">{item.file.name}</p>
        <p className="text-xs text-muted-foreground">{formatSize(item.file.size)}</p>
        {item.status === "uploading" && (
          <div className="mt-1 h-1 w-full rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-primary transition-all"
              style={{ width: `${item.progress}%` }}
              role="progressbar"
              aria-valuenow={item.progress}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label={t("attachment.uploading", "Uploading...")}
            />
          </div>
        )}
      </div>
      <button
        type="button"
        onClick={onRemove}
        className="flex-shrink-0 rounded-full p-0.5 text-muted-foreground hover:bg-muted hover:text-foreground"
        aria-label={t("attachment.remove", "Remove attachment")}
        data-testid="remove-staged-attachment"
      >
        <X className="h-3.5 w-3.5" />
      </button>
    </div>
  );
}

export function AttachmentStagingArea({ items, onRemove }: AttachmentStagingAreaProps) {
  if (items.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 px-6 pt-3" data-testid="attachment-staging-area">
      {items.map((item) => (
        <StagedItem key={item.id} item={item} onRemove={() => onRemove(item.id)} />
      ))}
    </div>
  );
}
