import { useCallback, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "react-toastify";
import { uploadAttachment, deleteAttachment, type Attachment } from "@/api/attachments";

const ALLOWED_TYPES = new Set([
  "image/png",
  "image/jpeg",
  "image/webp",
  "application/pdf",
]);
const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100 MB
const MAX_PER_MESSAGE = 3;
const MAX_PER_PROJECT = 10;

export interface PendingUpload {
  id: string;
  file: File;
  progress: number;
  status: "uploading" | "done" | "error";
  attachment?: Attachment;
}

export function useAttachmentUpload(
  projectId: string,
  projectAttachmentCount: number,
  ensureProject?: () => Promise<string>,
) {
  const { t } = useTranslation();
  const [pending, setPending] = useState<PendingUpload[]>([]);
  const nextId = useRef(0);

  const stagedAttachmentIds = pending
    .filter((p) => p.status === "done" && p.attachment)
    .map((p) => p.attachment!.id);

  const isUploading = pending.some((p) => p.status === "uploading");

  const addFiles = useCallback(
    async (files: FileList | File[]) => {
      const fileArr = Array.from(files);

      // Check staging limit
      const currentStaged = pending.filter((p) => p.status !== "error").length;
      if (currentStaged + fileArr.length > MAX_PER_MESSAGE) {
        toast.error(t("attachment.limitPerMessage", "Maximum 3 attachments per message"));
        return;
      }

      // Check project limit
      if (projectAttachmentCount + fileArr.length > MAX_PER_PROJECT) {
        toast.error(t("attachment.limitPerProject", "Maximum 10 attachments per project"));
        return;
      }

      // Ensure the project is persisted before uploading
      let realProjectId = projectId;
      if (ensureProject) {
        try {
          realProjectId = await ensureProject();
        } catch {
          toast.error(t("attachment.uploadFailed", "Upload failed: could not create project"));
          return;
        }
      }

      for (const file of fileArr) {
        if (!ALLOWED_TYPES.has(file.type)) {
          toast.error(
            t("attachment.typeError", "File type not allowed: {{name}}", { name: file.name }),
          );
          continue;
        }
        if (file.size > MAX_FILE_SIZE) {
          toast.error(
            t("attachment.sizeError", "File too large: {{name}} (max 100 MB)", { name: file.name }),
          );
          continue;
        }

        const uploadId = String(nextId.current++);
        const entry: PendingUpload = { id: uploadId, file, progress: 0, status: "uploading" };
        setPending((prev) => [...prev, entry]);

        uploadAttachment(realProjectId, file, (progress) => {
          setPending((prev) =>
            prev.map((p) => (p.id === uploadId ? { ...p, progress } : p)),
          );
        })
          .then((attachment) => {
            setPending((prev) =>
              prev.map((p) =>
                p.id === uploadId ? { ...p, progress: 100, status: "done", attachment } : p,
              ),
            );
          })
          .catch(() => {
            toast.error(t("attachment.uploadFailed", "Upload failed: {{name}}", { name: file.name }));
            setPending((prev) => prev.filter((p) => p.id !== uploadId));
          });
      }
    },
    [projectId, pending, projectAttachmentCount, t, ensureProject],
  );

  const removeAttachment = useCallback(
    (id: string) => {
      const item = pending.find((p) => p.id === id);
      if (item?.attachment) {
        deleteAttachment(projectId, item.attachment.id).catch(() => {
          // best-effort deletion
        });
      }
      setPending((prev) => prev.filter((p) => p.id !== id));
    },
    [pending, projectId],
  );

  const clearStaged = useCallback(() => {
    setPending([]);
  }, []);

  return {
    pending,
    addFiles,
    removeAttachment,
    stagedAttachmentIds,
    clearStaged,
    isUploading,
  };
}
