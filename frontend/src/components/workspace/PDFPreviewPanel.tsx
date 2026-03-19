import { useCallback, useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Download, FileText, Loader2 } from "lucide-react";
import { toast } from "react-toastify";
import { Button } from "@/components/ui/button";
import { fetchBrdPreviewPdf, fetchBrdPdf } from "@/api/brd";

interface PDFPreviewPanelProps {
  projectId: string;
  selectedAttachmentIds?: Set<string>;
}

export function PDFPreviewPanel({ projectId, selectedAttachmentIds }: PDFPreviewPanelProps) {
  const { t } = useTranslation();
  const [pdfBlob, setPdfBlob] = useState<Blob | null>(null);
  const [loading, setLoading] = useState(false);

  const blobUrl = useMemo(() => {
    if (!pdfBlob) return null;
    return URL.createObjectURL(pdfBlob);
  }, [pdfBlob]);

  useEffect(() => {
    return () => {
      if (blobUrl) URL.revokeObjectURL(blobUrl);
    };
  }, [blobUrl]);

  // Serialize selectedAttachmentIds to a stable string for dependency tracking
  const attachmentIdsKey = selectedAttachmentIds ? [...selectedAttachmentIds].sort().join(",") : "";

  // Fetch preview on mount and when attachment selection changes
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    const attachmentIds = attachmentIdsKey ? attachmentIdsKey.split(",") : undefined;
    fetchBrdPreviewPdf(projectId, attachmentIds)
      .then((blob) => {
        if (!cancelled) setPdfBlob(blob);
      })
      .catch(() => {
        // No preview available yet — that's OK
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [projectId, attachmentIdsKey]);

  // Listen for brd_ready WebSocket events to refresh preview
  useEffect(() => {
    const handler = async (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail?.project_id === projectId) {
        try {
          const attachmentIds = selectedAttachmentIds ? [...selectedAttachmentIds] : undefined;
          const blob = await fetchBrdPreviewPdf(projectId, attachmentIds);
          setPdfBlob(blob);
        } catch {
          // Ignore preview fetch failure
        }
      }
    };
    window.addEventListener("ws:brd_ready", handler);
    return () => window.removeEventListener("ws:brd_ready", handler);
  }, [projectId]);

  const handleDownload = useCallback(async () => {
    try {
      const attachmentIds = selectedAttachmentIds ? [...selectedAttachmentIds] : undefined;
      const blob = await fetchBrdPdf(projectId, attachmentIds);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `requirements-${projectId}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      toast.error(
        (error as Error).message ||
          t("review.downloadError", "Failed to download PDF"),
      );
    }
  }, [projectId, selectedAttachmentIds, t]);

  return (
    <div
      className="flex flex-col h-full"
      data-testid="pdf-preview-panel"
    >
      <div className="flex justify-between items-center mb-3 shrink-0">
        <h3 className="text-sm font-semibold text-foreground">
          {t("structure.pdfPreview", "Document Preview")}
        </h3>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleDownload}
          disabled={!pdfBlob}
          data-testid="download-pdf-button"
        >
          <Download className="h-4 w-4 mr-1" />
          {t("review.downloadPdf", "Download PDF")}
        </Button>
      </div>

      <div className="flex-1 bg-white dark:bg-muted/20 rounded-lg border border-border overflow-auto min-h-0">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : blobUrl ? (
          <object
            data={blobUrl}
            type="application/pdf"
            className="w-full h-full min-h-[600px]"
            data-testid="pdf-preview-object"
          >
            <p className="p-4 text-sm text-muted-foreground">
              {t(
                "structure.pdfFallback",
                "Unable to display PDF. Please download instead.",
              )}
            </p>
          </object>
        ) : (
          <div className="flex flex-col items-center justify-center h-full gap-3 p-6">
            <FileText className="h-12 w-12 text-muted-foreground/40" />
            <p className="text-sm text-muted-foreground text-center">
              {t(
                "structure.pdfPlaceholder",
                "PDF preview will appear here after generation.",
              )}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
