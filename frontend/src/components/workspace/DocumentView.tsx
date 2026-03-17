import { useCallback, useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { CheckCircle, Download, FileText, Loader2 } from "lucide-react";
import { toast } from "react-toastify";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/common/EmptyState";
import { PDFPreview } from "@/components/brd/PDFPreview";
import { SectionField } from "@/components/brd/SectionField";
import { ProgressIndicator, SECTION_KEYS } from "@/components/brd/ProgressIndicator";
import { SubmitArea } from "@/components/review/SubmitArea";
import { AIProcessingOverlay } from "./AIProcessingOverlay";
import {
  fetchBrdDraft,
  triggerBrdGeneration,
  fetchBrdPdf,
  fetchBrdPreviewPdf,
  patchBrdDraft,
} from "@/api/brd";
import type { BrdDraft } from "@/api/brd";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { ProcessStep } from "./ProcessStepper";

const TODO_MARKER = "/TODO";

const SECTION_FIELD_KEYS = [
  "section_title",
  "section_short_description",
  "section_current_workflow",
  "section_affected_department",
  "section_core_capabilities",
  "section_success_criteria",
] as const;

type SectionFieldKey = (typeof SECTION_FIELD_KEYS)[number];

const LABELS: Record<string, string> = {
  title: "1. Title",
  short_description: "2. Short Description",
  current_workflow: "3. Current Workflow & Pain Points",
  affected_department: "4. Affected Department",
  core_capabilities: "5. Core Capabilities",
  success_criteria: "6. Success Criteria",
};

function sectionKeyToFieldKey(sectionKey: string): SectionFieldKey {
  return `section_${sectionKey}` as SectionFieldKey;
}

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

interface DocumentViewProps {
  projectId: string;
  projectState?: string;
  disabled?: boolean;
  onStepChange: (step: ProcessStep) => void;
  onSubmitted?: () => void;
}

export function DocumentView({
  projectId,
  projectState,
  disabled,
  onStepChange,
  onSubmitted,
}: DocumentViewProps) {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const [pdfBlob, setPdfBlob] = useState<Blob | null>(null);
  const [todoWarningOpen, setTodoWarningOpen] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [regeneratingSection, setRegeneratingSection] = useState<string | null>(null);
  const debounceTimers = useRef<Record<string, ReturnType<typeof setTimeout>>>({});
  const [localSections, setLocalSections] = useState<Record<string, string>>({});

  const {
    data: brdDraft,
    isLoading: isDraftLoading,
  } = useQuery({
    queryKey: ["brd", projectId],
    queryFn: () => fetchBrdDraft(projectId),
  });

  // Sync local sections when brdDraft changes
  useEffect(() => {
    if (!brdDraft) return;
    const sections: Record<string, string> = {};
    for (const key of SECTION_KEYS) {
      sections[key] = brdDraft[sectionKeyToFieldKey(key)] ?? "";
    }
    setLocalSections(sections);
  }, [brdDraft]);

  // Auto-generate BRD on first visit when sections are empty
  const autoGenerateTriggered = useRef(false);
  useEffect(() => {
    if (isDraftLoading || disabled || autoGenerateTriggered.current) return;
    const hasContent = brdDraft && (
      brdDraft.section_title ||
      brdDraft.section_short_description ||
      brdDraft.section_current_workflow ||
      brdDraft.section_affected_department ||
      brdDraft.section_core_capabilities ||
      brdDraft.section_success_criteria
    );
    if (!hasContent) {
      autoGenerateTriggered.current = true;
      generateMutation.mutate();
    }
  }, [isDraftLoading, brdDraft, disabled]); // eslint-disable-line react-hooks/exhaustive-deps

  const generateMutation = useMutation({
    mutationFn: () => triggerBrdGeneration(projectId, "full_generation"),
    onSuccess: () => {
      setIsGenerating(true);
      queryClient.invalidateQueries({ queryKey: ["brd", projectId] });
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

  const patchMutation = useMutation({
    mutationFn: (data: Parameters<typeof patchBrdDraft>[1]) =>
      patchBrdDraft(projectId, data),
    onSuccess: (updated) => {
      queryClient.setQueryData(["brd", projectId], updated);
    },
    onError: (error: Error) => {
      toast.error(error.message || t("brd.saveError", "Failed to save changes"));
    },
  });

  // Listen for brd_generating WebSocket events (multi-user: another user triggered generation)
  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail?.project_id === projectId) {
        setIsGenerating(true);
      }
    };
    window.addEventListener("ws:brd_generating", handler);
    return () => window.removeEventListener("ws:brd_generating", handler);
  }, [projectId]);

  // Listen for brd_ready WebSocket events
  useEffect(() => {
    const handler = async (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail?.project_id === projectId) {
        setIsGenerating(false);
        queryClient.invalidateQueries({ queryKey: ["brd", projectId] });
        try {
          const blob = await fetchBrdPreviewPdf(projectId);
          setPdfBlob(blob);
        } catch (error) {
          console.warn("PDF preview fetch failed", error);
        }
      }
    };
    window.addEventListener("ws:brd_ready", handler);
    return () => window.removeEventListener("ws:brd_ready", handler);
  }, [projectId, queryClient]);

  // Cleanup debounce timers on unmount
  useEffect(() => {
    const timers = debounceTimers.current;
    return () => {
      Object.values(timers).forEach(clearTimeout);
    };
  }, []);

  const hasBrdContent = brdDraft && (
    brdDraft.section_title ||
    brdDraft.section_short_description ||
    brdDraft.section_current_workflow ||
    brdDraft.section_affected_department ||
    brdDraft.section_core_capabilities ||
    brdDraft.section_success_criteria
  );

  const handleContentChange = useCallback(
    (sectionKey: string, value: string) => {
      setLocalSections((prev) => ({ ...prev, [sectionKey]: value }));

      if (brdDraft && !brdDraft.section_locks[sectionKey]) {
        const newLocks = { ...brdDraft.section_locks, [sectionKey]: true };
        queryClient.setQueryData(["brd", projectId], {
          ...brdDraft,
          section_locks: newLocks,
        });
      }

      if (debounceTimers.current[sectionKey]) {
        clearTimeout(debounceTimers.current[sectionKey]);
      }
      debounceTimers.current[sectionKey] = setTimeout(() => {
        const fieldKey = sectionKeyToFieldKey(sectionKey);
        patchMutation.mutate({ [fieldKey]: value });
      }, 300);
    },
    [brdDraft, projectId, queryClient, patchMutation],
  );

  const handleBlur = useCallback(
    (sectionKey: string, value: string) => {
      if (debounceTimers.current[sectionKey]) {
        clearTimeout(debounceTimers.current[sectionKey]);
        delete debounceTimers.current[sectionKey];
      }
      const fieldKey = sectionKeyToFieldKey(sectionKey);
      patchMutation.mutate({ [fieldKey]: value });
    },
    [patchMutation],
  );

  const handleToggleLock = useCallback(
    (sectionKey: string, locked: boolean) => {
      if (!brdDraft) return;
      const newLocks = { ...brdDraft.section_locks, [sectionKey]: locked };
      patchMutation.mutate({ section_locks: newLocks });
    },
    [brdDraft, patchMutation],
  );

  const handleRegenerate = useCallback(
    async (sectionKey: string) => {
      try {
        setRegeneratingSection(sectionKey);
        await triggerBrdGeneration(projectId, "section_regeneration", sectionKey);
        queryClient.invalidateQueries({ queryKey: ["brd", projectId] });
      } catch (error) {
        toast.error(
          (error as Error).message ||
            t("brd.regenerateError", "Failed to regenerate section"),
        );
      } finally {
        setRegeneratingSection(null);
      }
    },
    [projectId, queryClient, t],
  );

  const handleGapsToggle = useCallback(
    (checked: boolean) => {
      patchMutation.mutate({ allow_information_gaps: checked });
    },
    [patchMutation],
  );

  const doDownload = useCallback(async () => {
    try {
      const blob = await fetchBrdPdf(projectId);
      setPdfBlob(blob);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `brd-${projectId}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      toast.error(
        (error as Error).message || t("review.downloadError", "Failed to download PDF"),
      );
    }
  }, [projectId, t]);

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

  const handleSubmitted = useCallback(() => {
    onSubmitted?.();
    onStepChange("review");
  }, [onSubmitted, onStepChange]);

  if (isDraftLoading) {
    return (
      <div className="flex flex-1 min-h-0 gap-6" data-testid="document-view-loading">
        <div className="flex-1 space-y-4">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
        <div className="w-[360px] shrink-0">
          <Skeleton className="h-full w-full" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-1 min-h-0 gap-6" data-testid="document-view">
      {/* Left: BRD Sections Editor */}
      <div className="flex-1 min-w-0 overflow-y-auto space-y-6">
        {/* Progress + Gaps + Action Buttons */}
        <div className="space-y-3">
          <div className="flex items-center justify-between gap-4">
            <h2 className="text-lg font-semibold text-foreground">
              {t("document.title", "Business Requirements Document")}
            </h2>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleDownload}
                disabled={!hasBrdContent || disabled}
                data-testid="download-pdf-button"
              >
                <Download className="h-4 w-4 mr-1" />
                {t("review.downloadPdf", "Download PDF")}
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={handleGenerate}
                disabled={generateMutation.isPending || isGenerating || disabled}
                data-testid="generate-brd-button"
              >
                {(generateMutation.isPending || isGenerating) && (
                  <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                )}
                {isGenerating
                  ? t("review.generating", "Generating BRD...")
                  : hasBrdContent
                    ? t("review.regenerate", "Regenerate")
                    : t("review.generate", "Generate")}
              </Button>
            </div>
          </div>

          {brdDraft && (
            <>
              <ProgressIndicator
                readinessEvaluation={brdDraft.readiness_evaluation}
                allowInformationGaps={brdDraft.allow_information_gaps}
              />
              <div className="flex items-center gap-2">
                <Switch
                  checked={brdDraft.allow_information_gaps}
                  onCheckedChange={handleGapsToggle}
                  data-testid="gaps-toggle"
                />
                <label className="text-sm text-muted-foreground">
                  {t("brd.allowGaps", "Allow information gaps")}
                </label>
              </div>
            </>
          )}
        </div>

        {/* Section Fields */}
        {brdDraft ? (
          <div className="relative space-y-5">
            {isGenerating && (
              <AIProcessingOverlay message={t("review.generating", "Generating BRD...")} />
            )}
            {SECTION_KEYS.map((key) => (
              <SectionField
                key={key}
                label={LABELS[key] ?? key}
                sectionKey={key}
                value={localSections[key] ?? ""}
                locked={!!brdDraft.section_locks[key]}
                readiness={brdDraft.readiness_evaluation[key]}
                allowInformationGaps={brdDraft.allow_information_gaps}
                regenerating={regeneratingSection === key}
                onContentChange={handleContentChange}
                onBlur={handleBlur}
                onToggleLock={handleToggleLock}
                onRegenerate={handleRegenerate}
              />
            ))}
          </div>
        ) : isGenerating || generateMutation.isPending ? (
          <div className="flex flex-col items-center justify-center py-16 gap-3">
            <Loader2 className="h-8 w-8 motion-safe:animate-spin text-muted-foreground" />
            <p className="text-sm text-muted-foreground">
              {t("review.generating", "Generating BRD...")}
            </p>
          </div>
        ) : (
          <EmptyState
            icon={FileText}
            message={t("review.emptyTitle", "No BRD generated yet")}
            description={t(
              "review.emptyDescription",
              "Click Generate to create your first BRD.",
            )}
          />
        )}

        {/* Submit Area — prominent placement */}
        {projectState && (projectState === "open" || projectState === "rejected") && hasBrdContent && (
          <div className="mt-6 p-5 rounded-lg border-2 border-dashed border-secondary/40 dark:border-primary/30 bg-secondary/5 dark:bg-primary/5">
            <div className="flex items-start gap-3 mb-3">
              <div className="shrink-0 flex items-center justify-center w-8 h-8 rounded-full bg-secondary/10 dark:bg-primary/10">
                <CheckCircle className="h-4 w-4 text-secondary dark:text-primary" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-foreground">
                  {t("submit.readyTitle", "Ready to submit?")}
                </h3>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {t("submit.readyDescription", "Once submitted, your project will be sent to reviewers for evaluation.")}
                </p>
              </div>
            </div>
            <SubmitArea projectId={projectId} projectState={projectState} onSubmitted={handleSubmitted} />
          </div>
        )}
        {projectState && projectState !== "open" && projectState !== "rejected" && (
          <SubmitArea projectId={projectId} projectState={projectState} onSubmitted={handleSubmitted} />
        )}
      </div>

      {/* Right: PDF Preview */}
      <div className="w-[360px] shrink-0 rounded-lg border border-border bg-muted/30 p-4 overflow-y-auto hidden lg:block">
        {pdfBlob ? (
          <PDFPreview pdfBlob={pdfBlob} className="h-full" />
        ) : hasBrdContent ? (
          <div className="flex flex-col items-center justify-center h-full gap-3">
            <FileText className="h-12 w-12 text-muted-foreground" />
            <p className="text-sm text-muted-foreground text-center">
              {t("review.brdReady", "BRD generated. Click Download to view the PDF.")}
            </p>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full gap-3">
            <FileText className="h-12 w-12 text-muted-foreground/40" />
            <p className="text-sm text-muted-foreground text-center">
              {t("document.pdfPlaceholder", "PDF preview will appear here after generation.")}
            </p>
          </div>
        )}
      </div>

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
