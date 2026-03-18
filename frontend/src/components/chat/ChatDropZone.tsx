import { useCallback, useState, type ReactNode, type DragEvent } from "react";
import { useTranslation } from "react-i18next";

interface ChatDropZoneProps {
  onFiles: (files: FileList) => void;
  disabled?: boolean;
  children: ReactNode;
}

export function ChatDropZone({ onFiles, disabled, children }: ChatDropZoneProps) {
  const { t } = useTranslation();
  const [dragOver, setDragOver] = useState(false);
  const dragCounter = useState(0);

  const handleDragEnter = useCallback(
    (e: DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      if (disabled) return;
      dragCounter[1]((c) => {
        const next = c + 1;
        if (next === 1) setDragOver(true);
        return next;
      });
    },
    [disabled, dragCounter],
  );

  const handleDragLeave = useCallback(
    (e: DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      dragCounter[1]((c) => {
        const next = c - 1;
        if (next <= 0) {
          setDragOver(false);
          return 0;
        }
        return next;
      });
    },
    [dragCounter],
  );

  const handleDragOver = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback(
    (e: DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragOver(false);
      dragCounter[1](0);
      if (disabled) return;
      if (e.dataTransfer.files.length > 0) {
        onFiles(e.dataTransfer.files);
      }
    },
    [disabled, onFiles, dragCounter],
  );

  return (
    <div
      className="relative flex-1 flex flex-col min-h-0"
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      data-testid="chat-drop-zone"
    >
      {children}
      {dragOver && (
        <div
          className="absolute inset-0 z-50 flex items-center justify-center rounded-lg border-2 border-dashed border-primary bg-primary/10 backdrop-blur-sm"
          data-testid="drop-overlay"
        >
          <p className="text-lg font-medium text-primary">
            {t("attachment.dragDrop", "Drop files here")}
          </p>
        </div>
      )}
    </div>
  );
}
