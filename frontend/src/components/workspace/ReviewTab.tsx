import { useCallback, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Download, FileText, Loader2, Pencil } from "lucide-react";
import { toast } from "react-toastify";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { EmptyState } from "@/components/common/EmptyState";
import { PDFPreview } from "@/components/brd/PDFPreview";
import { BRDSectionEditor } from "@/components/brd/BRDSectionEditor";
import { fetchBrdDraft, triggerBrdGeneration, fetchBrdPdf } from "@/api/brd";
import type { BrdDraft } from "@/api/brd";

const TODO_MARKER = "/TODO";

function hasTodoMarkers(draft: BrdDraft): boolean {
  const fields = [
    draft.section_title,
    draft.section_short_description,
    draft.section_current_workflow,
    draft.section_affected_department,
    draft.section_core_capabilities,
    draft.section_success_criteria,
  ];
  return fields.some((f) => f && f.includes(TODO_MARKER));
}

interface ReviewTabProps {
  ideaId: string;
  disabled?: boolean;
}

export function ReviewTab({ ideaId, disabled }: ReviewTabProps) {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const [pdfBlob, setPdfBlob] = useState<Blob | null>(null);
  const [editorOpen, setEditorOpen] = useState(false);
  const [todoWarningOpen, setTodoWarningOpen] = useState(false);

  const {
    data: brdDraft,
    isLoading: isDraftLoading,
  } = useQuery({
    queryKey: ["brd", ideaId],
    queryFn: () => fetchBrdDraft(ideaId),
  });

  const generateMutation = useMutation({
    mutationFn: () => triggerBrdGeneration(ideaId, "full_generation"),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["brd", ideaId] });
    },
    onError: (error: Error) => {
      toast.error(
        <div className="flex items-center justify-between gap-4">
          <span>{error.message || t("review.generateError", "Failed to generate BRD")}</span>
          <button
            className="shrink-0 font-medium text-primary underline"
            onClick={() => generateMutation.mutate()}
          >
            {t("common.retry", "Retry")}
          </button>
        </div>,
      );
    },
  });

  // Listen for brd_ready WebSocket events to invalidate cache
  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail?.idea_id === ideaId) {
        queryClient.invalidateQueries({ queryKey: ["brd", ideaId] });
      }
    };
    window.addEventListener("ws:brd_ready", handler);
    return () => window.removeEventListener("ws:brd_ready", handler);
  }, [ideaId, queryClient]);

  const hasBrdContent = brdDraft && (
    brdDraft.section_title ||
    brdDraft.section_short_description ||
    brdDraft.section_current_workflow ||
    brdDraft.section_affected_department ||
    brdDraft.section_core_capabilities ||
    brdDraft.section_success_criteria
  );

  const doDownload = useCallback(async () => {
    try {
      const blob = await fetchBrdPdf(ideaId);
      setPdfBlob(blob);

      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `brd-${ideaId}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      toast.error(
        (error as Error).message || t("review.downloadError", "Failed to download PDF"),
      );
    }
  }, [ideaId, t]);

  const handleDownload = useCallback(() => {
    if (brdDraft && hasTodoMarkers(brdDraft)) {
      setTodoWarningOpen(true);
      return;
    }
    doDownload();
  }, [brdDraft, doDownload]);

  const handleGenerate = useCallback(() => {
    generateMutation.mutate();
  }, [generateMutation]);

  if (isDraftLoading) {
    return (
      <div className="flex flex-col h-full p-4 gap-4" data-testid="review-tab-loading">
        <Skeleton className="flex-1 w-full" />
        <div className="flex gap-2">
          <Skeleton className="h-10 w-32" />
          <Skeleton className="h-10 w-32" />
        </div>
      </div>
    );
  }

  return (
    <div className="relative flex flex-col h-full p-4 gap-4" data-testid="review-tab">
      {/* PDF Preview or Empty State */}
      <div className="flex-1 min-h-0">
        {hasBrdContent ? (
          pdfBlob ? (
            <PDFPreview pdfBlob={pdfBlob} className="h-full" />
          ) : (
            <div
              className="flex flex-col items-center justify-center h-full bg-white border rounded shadow"
              data-testid="brd-content-preview"
            >
              <FileText className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-sm text-muted-foreground">
                {t("review.brdReady", "BRD generated. Click Download to view the PDF.")}
              </p>
            </div>
          )
        ) : generateMutation.isPending ? (
          <div
            className="flex flex-col items-center justify-center h-full gap-3"
            data-testid="review-tab-generating"
          >
            <Skeleton className="h-64 w-full" />
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              {t("review.generating", "Generating BRD...")}
            </div>
          </div>
        ) : (
          <EmptyState
            icon={FileText}
            message={t(
              "review.emptyTitle",
              "No BRD generated yet",
            )}
            description={t(
              "review.emptyDescription",
              "Click Generate to create your first BRD.",
            )}
            className="h-full"
          />
        )}
      </div>

      {/* Action Bar */}
      <div className="flex gap-2 shrink-0" data-testid="review-action-bar">
        <Button
          variant="ghost"
          onClick={handleDownload}
          disabled={!hasBrdContent || disabled}
          data-testid="download-pdf-button"
        >
          <Download className="h-4 w-4 mr-2" />
          {t("review.downloadPdf", "Download PDF")}
        </Button>
        <Button
          variant="primary"
          onClick={handleGenerate}
          disabled={generateMutation.isPending || disabled}
          data-testid="generate-brd-button"
        >
          {generateMutation.isPending && (
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          )}
          {t("review.generate", "Generate")}
        </Button>
        {hasBrdContent && (
          <Button
            variant="ghost"
            onClick={() => setEditorOpen(true)}
            disabled={disabled}
            data-testid="edit-document-button"
          >
            <Pencil className="h-4 w-4 mr-2" />
            {t("review.editDocument", "Edit Document")}
          </Button>
        )}
      </div>

      {/* Slide-in Editor */}
      {brdDraft && (
        <BRDSectionEditor
          ideaId={ideaId}
          brdDraft={brdDraft}
          open={editorOpen}
          onClose={() => setEditorOpen(false)}
        />
      )}

      {/* /TODO Warning Dialog */}
      <Dialog open={todoWarningOpen} onOpenChange={setTodoWarningOpen}>
        <DialogContent data-testid="todo-warning-dialog">
          <DialogHeader>
            <DialogTitle>
              {t("review.todoWarningTitle", "Sections contain /TODO markers")}
            </DialogTitle>
            <DialogDescription>
              {t(
                "review.todoWarningDescription",
                "Cannot generate PDF: sections contain /TODO markers. Please complete or disable information gaps.",
              )}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="ghost"
              onClick={() => setTodoWarningOpen(false)}
              data-testid="todo-warning-close"
            >
              {t("common.ok", "OK")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
