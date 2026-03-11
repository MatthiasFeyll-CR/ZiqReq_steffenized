import { useMemo } from "react";
import { cn } from "@/lib/utils";

interface PDFPreviewProps {
  pdfBlob: Blob | null;
  className?: string;
}

export function PDFPreview({ pdfBlob, className }: PDFPreviewProps) {
  const blobUrl = useMemo(() => {
    if (!pdfBlob) return null;
    return URL.createObjectURL(pdfBlob);
  }, [pdfBlob]);

  // Clean up blob URL on unmount handled by parent or on re-render via useMemo

  if (!blobUrl) return null;

  return (
    <div
      className={cn(
        "bg-white border rounded shadow overflow-auto",
        className,
      )}
      data-testid="pdf-preview-container"
    >
      <object
        data={blobUrl}
        type="application/pdf"
        className="w-full h-full min-h-[600px]"
        data-testid="pdf-preview-object"
      >
        <p className="p-4 text-sm text-muted-foreground">
          Unable to display PDF. Please download instead.
        </p>
      </object>
    </div>
  );
}
