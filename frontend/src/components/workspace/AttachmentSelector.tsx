import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { FileText, Image, File, Loader2 } from "lucide-react";
import { listAttachments, type Attachment } from "@/api/attachments";

interface AttachmentSelectorProps {
  projectId: string;
  selectedIds: Set<string>;
  onSelectionChange: (ids: Set<string>) => void;
  onAttachmentsLoaded?: (attachments: Attachment[]) => void;
}

function fileIcon(contentType: string) {
  if (contentType.startsWith("image/")) return Image;
  if (contentType === "application/pdf") return FileText;
  return File;
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function AttachmentSelector({
  projectId,
  selectedIds,
  onSelectionChange,
  onAttachmentsLoaded,
}: AttachmentSelectorProps) {
  const { t } = useTranslation();
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    listAttachments(projectId)
      .then((data) => {
        if (cancelled) return;
        setAttachments(data);
        onAttachmentsLoaded?.(data);
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId]);

  const allSelected =
    attachments.length > 0 && selectedIds.size === attachments.length;

  const handleToggleAll = () => {
    if (allSelected) {
      onSelectionChange(new Set());
    } else {
      onSelectionChange(new Set(attachments.map((a) => a.id)));
    }
  };

  const handleToggle = (id: string) => {
    const next = new Set(selectedIds);
    if (next.has(id)) {
      next.delete(id);
    } else {
      next.add(id);
    }
    onSelectionChange(next);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-6">
        <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (attachments.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-6 gap-2">
        <FileText className="h-8 w-8 text-muted-foreground/40" />
        <p className="text-xs text-muted-foreground">
          {t(
            "structure.noAttachments",
            "No attachments uploaded for this project.",
          )}
        </p>
      </div>
    );
  }

  return (
    <div>
      <label className="flex items-center gap-2 px-1 py-1 cursor-pointer text-sm font-medium text-foreground">
        <input
          type="checkbox"
          checked={allSelected}
          onChange={handleToggleAll}
          className="rounded border-input"
          aria-label={t("structure.selectAll", "Select All")}
        />
        {t("structure.selectAll", "Select All")}
        <span className="text-xs text-muted-foreground font-normal">
          ({selectedIds.size} {t("structure.selected", "selected")})
        </span>
      </label>

      <div className="mt-1 max-h-[200px] overflow-y-auto space-y-0.5">
        {attachments.map((att) => {
          const Icon = fileIcon(att.content_type);
          return (
            <label
              key={att.id}
              className="flex items-center gap-3 p-2 rounded hover:bg-accent cursor-pointer"
            >
              <input
                type="checkbox"
                checked={selectedIds.has(att.id)}
                onChange={() => handleToggle(att.id)}
                className="rounded border-input"
                aria-label={att.filename}
              />
              <Icon className="h-4 w-4 shrink-0 text-muted-foreground" />
              <span className="text-sm truncate min-w-0 flex-1 text-foreground">
                {att.filename}
              </span>
              <span className="text-xs text-muted-foreground shrink-0">
                {formatSize(att.size_bytes)}
              </span>
            </label>
          );
        })}
      </div>
    </div>
  );
}
