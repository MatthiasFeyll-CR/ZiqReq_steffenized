import { useCallback, useEffect, useRef, useState, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { Upload } from "lucide-react";

interface ChatDropZoneProps {
  onFiles: (files: FileList) => void;
  disabled?: boolean;
  children: ReactNode;
}

export function ChatDropZone({ onFiles, disabled, children }: ChatDropZoneProps) {
  const { t } = useTranslation();
  const [active, setActive] = useState(false);
  const [zoneHover, setZoneHover] = useState(false);
  const zoneRef = useRef<HTMLDivElement>(null);

  // Use refs for the state that the window listeners need,
  // so the effect doesn't re-register on every render.
  const activeRef = useRef(false);
  const windowCounterRef = useRef(0);
  const zoneCounterRef = useRef(0);

  useEffect(() => {
    if (disabled) return;

    const hasFiles = (e: globalThis.DragEvent) =>
      e.dataTransfer?.types?.includes("Files") ?? false;

    const onDragEnter = (e: globalThis.DragEvent) => {
      if (!hasFiles(e)) return;
      windowCounterRef.current++;
      if (!activeRef.current) {
        activeRef.current = true;
        setActive(true);
      }

      // Track zone hover via the zone ref
      if (zoneRef.current?.contains(e.target as Node)) {
        zoneCounterRef.current++;
        setZoneHover(true);
      }
    };

    const onDragLeave = (e: globalThis.DragEvent) => {
      // Zone hover tracking
      if (zoneRef.current?.contains(e.target as Node)) {
        zoneCounterRef.current--;
        if (zoneCounterRef.current <= 0) {
          zoneCounterRef.current = 0;
          setZoneHover(false);
        }
      }

      windowCounterRef.current--;
      if (windowCounterRef.current <= 0) {
        windowCounterRef.current = 0;
        activeRef.current = false;
        setActive(false);
        setZoneHover(false);
        zoneCounterRef.current = 0;
      }
    };

    const onDragOver = (e: globalThis.DragEvent) => {
      if (hasFiles(e)) e.preventDefault();
    };

    const onDrop = (e: globalThis.DragEvent) => {
      // Don't prevent default here — let the zone handler do it
      if (!zoneRef.current?.contains(e.target as Node)) {
        e.preventDefault();
      }
      windowCounterRef.current = 0;
      zoneCounterRef.current = 0;
      activeRef.current = false;
      setActive(false);
      setZoneHover(false);
    };

    window.addEventListener("dragenter", onDragEnter);
    window.addEventListener("dragleave", onDragLeave);
    window.addEventListener("dragover", onDragOver);
    window.addEventListener("drop", onDrop);

    return () => {
      window.removeEventListener("dragenter", onDragEnter);
      window.removeEventListener("dragleave", onDragLeave);
      window.removeEventListener("dragover", onDragOver);
      window.removeEventListener("drop", onDrop);
    };
  }, [disabled]);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      windowCounterRef.current = 0;
      zoneCounterRef.current = 0;
      activeRef.current = false;
      setActive(false);
      setZoneHover(false);
      if (disabled) return;
      if (e.dataTransfer.files.length > 0) {
        onFiles(e.dataTransfer.files);
      }
    },
    [disabled, onFiles],
  );

  const showOverlay = active && !disabled;

  return (
    <div
      ref={zoneRef}
      className="relative flex-1 flex flex-col min-h-0"
      onDrop={handleDrop}
      onDragOver={(e) => { e.preventDefault(); e.stopPropagation(); }}
      data-testid="chat-drop-zone"
    >
      {children}
      <div
        className={`absolute inset-0 z-50 pointer-events-none flex flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed transition-opacity duration-150 ${
          showOverlay
            ? zoneHover
              ? "opacity-100 border-primary bg-primary/15 backdrop-blur-sm"
              : "opacity-100 border-primary/50 bg-primary/5 backdrop-blur-[2px]"
            : "opacity-0 border-transparent"
        }`}
        data-testid="drop-overlay"
      >
        <div
          className={`rounded-full p-3 transition-colors ${
            zoneHover ? "bg-primary/20" : "bg-primary/10"
          }`}
        >
          <Upload
            className={`h-8 w-8 transition-colors ${
              zoneHover ? "text-primary" : "text-primary/70"
            }`}
          />
        </div>
        <p
          className={`text-lg font-medium transition-colors ${
            zoneHover ? "text-primary" : "text-primary/70"
          }`}
        >
          {t("attachment.dragDrop", "Drop files here")}
        </p>
        <p className="text-sm text-muted-foreground">
          {t("attachment.dragDropHint", "PNG, JPEG, WebP, or PDF — max 100 MB")}
        </p>
      </div>
    </div>
  );
}
