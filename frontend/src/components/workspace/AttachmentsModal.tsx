import { useCallback, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Check, ExternalLink, FileText, Image, Info, Loader2, Paperclip, Trash2 } from "lucide-react";
import { toast } from "react-toastify";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import {
  type Attachment,
  listAttachmentsIncludeDeleted,
  deleteAttachment,
  restoreAttachment,
} from "@/api/attachments";
import { cn } from "@/lib/utils";

const DEFAULT_TTL_HOURS = 96;

interface AttachmentsModalProps {
  projectId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" })
    + " " + d.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function hoursUntilDelete(deletedAt: string, ttlHours: number): { hours: number; minutes: number } {
  const deadline = new Date(deletedAt).getTime() + ttlHours * 60 * 60 * 1000;
  const remaining = Math.max(0, deadline - Date.now());
  return {
    hours: Math.floor(remaining / (60 * 60 * 1000)),
    minutes: Math.floor((remaining % (60 * 60 * 1000)) / (60 * 1000)),
  };
}

function isImageType(contentType: string): boolean {
  return contentType.startsWith("image/");
}

function AttachmentListItem({
  attachment,
  projectId,
  onDelete,
}: {
  attachment: Attachment;
  projectId: string;
  onDelete: (id: string) => void;
}) {
  const { t } = useTranslation();
  const [confirmDelete, setConfirmDelete] = useState(false);
  const Icon = isImageType(attachment.content_type) ? Image : FileText;

  const handleOpen = useCallback(() => {
    const url = `${window.location.origin}/api/projects/${projectId}/attachments/${attachment.id}/download/`;
    window.open(url, "_blank");
  }, [projectId, attachment.id]);

  return (
    <div className="flex items-center justify-between gap-3 rounded-md border border-border bg-background p-3">
      <div className="flex items-center gap-3 min-w-0 flex-1">
        <Icon className="h-5 w-5 flex-shrink-0 text-muted-foreground" />
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium text-foreground" title={attachment.filename}>
            {attachment.filename}
          </p>
          <p className="text-xs text-muted-foreground">
            {formatSize(attachment.size_bytes)} &middot; {formatDate(attachment.created_at)}
          </p>
        </div>
      </div>
      <div className="flex items-center gap-1 shrink-0">
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={handleOpen}
          aria-label={t("attachments.open", "Open attachment")}
        >
          <ExternalLink className="h-4 w-4" />
        </Button>
        {confirmDelete ? (
          <Button
            variant="destructive"
            size="sm"
            onClick={() => { onDelete(attachment.id); setConfirmDelete(false); }}
          >
            {t("common.confirm", "Confirm")}
          </Button>
        ) : (
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={() => setConfirmDelete(true)}
            aria-label={t("attachments.delete", "Delete attachment")}
          >
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        )}
      </div>
    </div>
  );
}

function DeletedAttachmentListItem({
  attachment,
  ttlHours,
  onRestore,
  restoring,
}: {
  attachment: Attachment;
  ttlHours: number;
  onRestore: (id: string) => void;
  restoring: boolean;
}) {
  const { t } = useTranslation();
  const Icon = isImageType(attachment.content_type) ? Image : FileText;
  const countdown = hoursUntilDelete(attachment.deleted_at!, ttlHours);

  return (
    <div className="flex items-center justify-between gap-3 rounded-md border border-border bg-background p-3 opacity-60">
      <div className="flex items-center gap-3 min-w-0 flex-1">
        <Icon className="h-5 w-5 flex-shrink-0 text-muted-foreground" />
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium line-through text-muted-foreground" title={attachment.filename}>
            {attachment.filename}
          </p>
          <p className="text-xs text-muted-foreground">
            {t("attachments.permanentDeleteIn", "Permanently deleted in {{hours}}h {{minutes}}m", {
              hours: countdown.hours,
              minutes: countdown.minutes,
            })}
          </p>
        </div>
      </div>
      <Button
        variant="outline"
        size="sm"
        onClick={() => onRestore(attachment.id)}
        disabled={restoring}
        className="shrink-0"
      >
        {restoring ? <Loader2 className="h-4 w-4 animate-spin" /> : t("attachments.restore", "Restore")}
      </Button>
    </div>
  );
}

function EmptyState({ icon: IconComp, message }: { icon: React.ElementType; message: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-6 text-muted-foreground">
      <IconComp className="h-8 w-8 mb-2 opacity-40" />
      <p className="text-sm">{message}</p>
    </div>
  );
}

export function AttachmentsModal({ projectId, open, onOpenChange }: AttachmentsModalProps) {
  const { t } = useTranslation();
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [loading, setLoading] = useState(false);
  const [restoringId, setRestoringId] = useState<string | null>(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const list = await listAttachmentsIncludeDeleted(projectId);
      setAttachments(list);
    } catch {
      toast.error(t("common.error", "An error occurred"));
    } finally {
      setLoading(false);
    }
  }, [projectId, t]);

  useEffect(() => {
    if (open) {
      fetchAll();
    }
  }, [open, fetchAll]);

  // Listen for WS events to refresh
  useEffect(() => {
    if (!open) return;
    const refresh = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail.project_id === projectId) fetchAll();
    };
    window.addEventListener("ws:attachment_deleted", refresh);
    window.addEventListener("ws:attachment_restored", refresh);
    return () => {
      window.removeEventListener("ws:attachment_deleted", refresh);
      window.removeEventListener("ws:attachment_restored", refresh);
    };
  }, [open, projectId, fetchAll]);

  const activeAttachments = attachments
    .filter((a) => !a.deleted_at)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

  const deletedAttachments = attachments
    .filter((a) => !!a.deleted_at)
    .sort((a, b) => new Date(b.deleted_at!).getTime() - new Date(a.deleted_at!).getTime());

  const handleDelete = useCallback(
    async (attachmentId: string) => {
      try {
        await deleteAttachment(projectId, attachmentId);
        setAttachments((prev) =>
          prev.map((a) => (a.id === attachmentId ? { ...a, deleted_at: new Date().toISOString() } : a)),
        );
        toast.success(t("attachments.deleteSuccess", "Attachment deleted"));
      } catch (err) {
        toast.error((err as Error).message);
      }
    },
    [projectId, t],
  );

  const handleRestore = useCallback(
    async (attachmentId: string) => {
      setRestoringId(attachmentId);
      try {
        const restored = await restoreAttachment(projectId, attachmentId);
        setAttachments((prev) => prev.map((a) => (a.id === attachmentId ? restored : a)));
        toast.success(t("attachments.restoreSuccess", "Attachment restored"));
      } catch (err) {
        toast.error((err as Error).message);
      } finally {
        setRestoringId(null);
      }
    },
    [projectId, t],
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className={cn("max-w-2xl max-h-[80vh] overflow-y-auto")}>
        <DialogHeader>
          <DialogTitle>{t("attachments.modalTitle", "Project Attachments")}</DialogTitle>
        </DialogHeader>

        {loading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <>
            {/* Active Attachments */}
            <div>
              <h4 className="text-sm font-medium text-foreground mb-3">
                {t("attachments.active", "Active")} ({activeAttachments.length})
              </h4>
              {activeAttachments.length === 0 ? (
                <EmptyState icon={Paperclip} message={t("attachments.noActive", "No active attachments")} />
              ) : (
                <div className="space-y-2">
                  {activeAttachments.map((att) => (
                    <AttachmentListItem
                      key={att.id}
                      attachment={att}
                      projectId={projectId}
                      onDelete={handleDelete}
                    />
                  ))}
                </div>
              )}
            </div>

            <hr className="border-border" />

            {/* Deleted Attachments */}
            <div>
              <h4 className="text-sm font-medium text-foreground mb-2">
                {t("attachments.deleted", "Deleted")} ({deletedAttachments.length})
              </h4>
              <div className="bg-muted/30 border border-border rounded-md p-3 mb-3 flex items-start gap-2">
                <Info className="h-4 w-4 text-muted-foreground mt-0.5 shrink-0" />
                <p className="text-sm text-muted-foreground">
                  {t("attachments.deleteNote", "Deleted attachments are permanently removed after {{hours}} hours.", {
                    hours: DEFAULT_TTL_HOURS,
                  })}
                </p>
              </div>
              {deletedAttachments.length === 0 ? (
                <EmptyState icon={Check} message={t("attachments.noDeleted", "No deleted attachments")} />
              ) : (
                <div className="space-y-2">
                  {deletedAttachments.map((att) => (
                    <DeletedAttachmentListItem
                      key={att.id}
                      attachment={att}
                      ttlHours={DEFAULT_TTL_HOURS}
                      onRestore={handleRestore}
                      restoring={restoringId === att.id}
                    />
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
