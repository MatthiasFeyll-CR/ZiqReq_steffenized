import type { Attachment } from "@/api/attachments";
import {
  fetchRequirements,
  generateRequirements,
  patchRequirements,
  type ProjectType,
  type RequirementsDraft,
} from "@/api/projects";
import { SubmitArea } from "@/components/review/SubmitArea";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { AttachmentSelector } from "@/components/workspace/AttachmentSelector";
import { CollapsibleSection } from "@/components/workspace/CollapsibleSection";
import { PDFPreviewPanel } from "@/components/workspace/PDFPreviewPanel";
import type { ProcessStep } from "@/components/workspace/ProcessStepper";
import { RequirementsPanel } from "@/components/workspace/RequirementsPanel";
import { CheckCircle, Loader2, Lock, Unlock } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "react-toastify";

interface StructureStepViewProps {
  projectId: string;
  projectType: ProjectType;
  projectState: string;
  projectTitle?: string;
  disabled?: boolean;
  readOnly?: boolean;
  collaborators?: Array<{ user_id: string; display_name: string }>;
  onStepChange: (step: ProcessStep) => void;
  onSubmitted?: () => void;
}

export function StructureStepView({
  projectId,
  projectType,
  projectState,
  projectTitle,
  disabled,
  readOnly,
  collaborators,
  onStepChange,
  onSubmitted,
}: StructureStepViewProps) {
  const { t } = useTranslation();
  const [draft, setDraft] = useState<RequirementsDraft | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  // Collapsible state
  const [advancedExpanded, setAdvancedExpanded] = useState(false);
  const [submitExpanded, setSubmitExpanded] = useState(false);
  // hasAutoExpandedSubmit removed — submit stays collapsed until user clicks "Next"

  // Attachment selection for PDF
  const [selectedAttachmentIds, setSelectedAttachmentIds] = useState<Set<string>>(new Set());

  // Fetch draft for action controls (readiness, gaps, locks)
  useEffect(() => {
    let cancelled = false;
    fetchRequirements(projectId)
      .then((data) => {
        if (!cancelled) setDraft(data);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [projectId]);

  // Listen for requirements_ready to refresh draft
  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail.project_id !== projectId) return;
      const payload = detail.payload ?? detail;
      if (payload.structure) {
        setDraft((prev) =>
          prev
            ? {
                ...prev,
                structure: payload.structure,
                readiness_evaluation: payload.readiness_evaluation ?? prev.readiness_evaluation,
              }
            : prev,
        );
        setIsGenerating(false);
      }
    };
    window.addEventListener("ws:requirements_ready", handler);
    return () => window.removeEventListener("ws:requirements_ready", handler);
  }, [projectId]);

  // Listen for requirements_updated
  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail.project_id !== projectId) return;
      const payload = detail.payload ?? detail;
      if (payload.structure) {
        setDraft((prev) => (prev ? { ...prev, structure: payload.structure } : prev));
      }
    };
    window.addEventListener("ws:requirements_updated", handler);
    return () => window.removeEventListener("ws:requirements_updated", handler);
  }, [projectId]);

  // Listen for brd_generating (AI generation in progress)
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

  const handleGenerate = useCallback(async () => {
    try {
      setIsGenerating(true);
      const lockedIds = draft
        ? Object.entries(draft.item_locks)
            .filter(([, locked]) => locked)
            .map(([id]) => id)
        : [];
      await generateRequirements(projectId, {
        mode: draft?.structure.length ? "selective" : "full",
        locked_item_ids: lockedIds.length > 0 ? lockedIds : undefined,
      });
    } catch (error) {
      setIsGenerating(false);
      toast.error(
        (error as Error).message || t("structure.generateError", "Failed to generate requirements"),
      );
    }
  }, [projectId, draft, t]);

  const handleGapsToggle = useCallback(
    async (checked: boolean) => {
      if (!draft) return;
      const prev = draft;
      setDraft({ ...draft, allow_information_gaps: checked });
      try {
        await patchRequirements(projectId, {});
      } catch {
        setDraft(prev);
      }
    },
    [draft, projectId],
  );

  const handleToggleLock = useCallback(
    async (itemId: string) => {
      if (!draft) return;
      const prev = draft;
      const newLocks = {
        ...draft.item_locks,
        [itemId]: !draft.item_locks[itemId],
      };
      setDraft({ ...draft, item_locks: newLocks });
      try {
        // Optimistic update - item_locks are tracked in the draft
      } catch {
        setDraft(prev);
      }
    },
    [draft],
  );

  // Auto-select all attachments when they first load
  const handleAttachmentsLoaded = useCallback((attachments: Attachment[]) => {
    setSelectedAttachmentIds(new Set(attachments.map((a) => a.id)));
  }, []);

  const handleSubmitted = useCallback(() => {
    onSubmitted?.();
    onStepChange("review");
  }, [onSubmitted, onStepChange]);

  const hasContent = draft && draft.structure.length > 0;

  // Submit section stays collapsed by default — user clicks "Next" to expand

  // Readiness evaluation summary
  const readinessEntries = draft?.readiness_evaluation
    ? Object.entries(draft.readiness_evaluation)
    : [];
  const readyCount = readinessEntries.filter(([, v]) => v === "ready" || v === "sufficient").length;
  const totalCount = readinessEntries.length;
  const allReady = totalCount > 0 && readyCount === totalCount;

  // Collapsible summaries
  const lockedCount = draft ? Object.values(draft.item_locks).filter(Boolean).length : 0;

  const canSubmit =
    projectState && (projectState === "open" || projectState === "rejected") && hasContent;

  return (
    <div className="flex flex-1 min-h-0 flex-col" data-testid="structure-step-view">
      {/* Sticky toolbar */}
      <div className="shrink-0 flex items-center justify-between gap-4 px-6 py-3 border-b border-border bg-surface">
        <div className="flex items-center gap-4">
          <Button
            variant="primary"
            size="sm"
            onClick={handleGenerate}
            disabled={isGenerating || disabled || readOnly}
            data-testid="generate-requirements-button"
          >
            {isGenerating && <Loader2 className="h-4 w-4 mr-1 animate-spin" />}
            {isGenerating
              ? t("structure.generating", "Generating...")
              : hasContent
                ? t("structure.regenerate", "Regenerate")
                : t("structure.generate", "Generate AI Draft")}
          </Button>

          <div className="flex items-center gap-2">
            <Switch
              checked={draft?.allow_information_gaps ?? false}
              onCheckedChange={handleGapsToggle}
              disabled={disabled || readOnly}
              data-testid="gaps-toggle"
            />
            <label className="text-sm text-muted-foreground">
              {t("brd.allowGaps", "Allow information gaps")}
            </label>
          </div>

          {/* Readiness indicator */}
          {totalCount > 0 && (
            <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
              <div
                className={`h-2 w-2 rounded-full ${allReady ? "bg-green-500" : "bg-amber-500"}`}
              />
              {readyCount}/{totalCount} {t("structure.ready", "ready")}
            </div>
          )}
        </div>
      </div>

      {/* Main content: Requirements panel + PDF preview */}
      <div className="flex flex-1 min-h-0">
        {/* Left: Requirements editor + Attachments (60%) */}
        <div className="flex-[3] min-w-0 flex flex-col min-h-0">
          <div className="flex-1 min-h-0 overflow-y-auto">
            <RequirementsPanel
              projectId={projectId}
              projectType={projectType}
              readOnly={readOnly || disabled}
              collaborators={collaborators}
              projectTitle={projectTitle}
            />
          </div>

          {/* Attachments for PDF — below epics in the left column */}
          <div className="shrink-0 border-t border-border p-4">
            <div className="rounded-lg border border-border overflow-hidden">
              <div className="px-4 py-3 bg-muted/30">
                <h4 className="text-sm font-medium text-foreground">
                  {t("structure.attachmentsForPdf", "Attachments for PDF")}
                </h4>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {t("structure.attachmentsForPdfDesc", "Selected attachments will be appended to the generated PDF document.")}
                </p>
              </div>
              <div className="px-4 py-3">
                <AttachmentSelector
                  projectId={projectId}
                  selectedIds={selectedAttachmentIds}
                  onSelectionChange={setSelectedAttachmentIds}
                  onAttachmentsLoaded={handleAttachmentsLoaded}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Right: PDF preview sidebar (40%) — full height */}
        <div className="flex-[2] border-l border-border p-4 min-h-0 hidden lg:flex lg:flex-col">
          <PDFPreviewPanel projectId={projectId} selectedAttachmentIds={selectedAttachmentIds} />
        </div>
      </div>

      {/* Collapsible: Advanced Options (item locks) */}
      {hasContent && !readOnly && (
        <div className="shrink-0 border-t border-border px-6 py-3">
          <CollapsibleSection
            title={t("structure.advancedOptions", "Advanced Options")}
            summary={lockedCount > 0 ? `${lockedCount} ${t("structure.locked", "locked")}` : undefined}
            expanded={advancedExpanded}
            onExpandedChange={setAdvancedExpanded}
          >
            <div>
              <h4 className="text-xs font-medium text-muted-foreground mb-2">
                {t("structure.itemLocks", "Item Locks")}
              </h4>
              <div className="flex flex-wrap gap-2" data-testid="item-locks">
                {draft!.structure.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => handleToggleLock(item.id)}
                    className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded border transition-colors ${
                      draft!.item_locks[item.id]
                        ? "border-amber-300 bg-amber-50 text-amber-700 dark:border-amber-700 dark:bg-amber-950/30 dark:text-amber-400"
                        : "border-border bg-background text-foreground hover:border-foreground/30"
                    }`}
                    title={
                      draft!.item_locks[item.id]
                        ? t("structure.unlock", "Unlock (allow AI regeneration)")
                        : t("structure.lock", "Lock (prevent AI regeneration)")
                    }
                    data-testid={`lock-${item.id}`}
                  >
                    {draft!.item_locks[item.id] ? (
                      <Lock className="h-3 w-3" />
                    ) : (
                      <Unlock className="h-3 w-3" />
                    )}
                    <span className="truncate max-w-[120px]">{item.title}</span>
                  </button>
                ))}
              </div>
            </div>
          </CollapsibleSection>
        </div>
      )}

      {/* Collapsible: Submit for Review */}
      {canSubmit && (
        <div
          className="shrink-0 border-t border-border px-6 py-3"
          data-testid="structure-submit-area"
        >
          <CollapsibleSection
            title={t("submit.readyTitle", "Ready to submit?")}
            summary={
              !allReady && !draft?.allow_information_gaps
                ? t("structure.notAllReady", "Not all items ready")
                : undefined
            }
            expanded={submitExpanded}
            onExpandedChange={setSubmitExpanded}
            variant="success"
            collapsedActionLabel={t("common.next", "Weiter")}
          >
            <div className="flex items-start gap-3 mb-3">
              <div className="shrink-0 flex items-center justify-center w-8 h-8 rounded-full bg-secondary/10 dark:bg-primary/10">
                <CheckCircle className="h-4 w-4 text-secondary dark:text-primary" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">
                  {t(
                    "submit.readyDescription",
                    "Once submitted, your project will be sent to reviewers for evaluation.",
                  )}
                </p>
                {!allReady && !draft?.allow_information_gaps && (
                  <p className="text-xs text-amber-600 dark:text-amber-400 mt-1">
                    {t(
                      "structure.notReady",
                      "Some items are not ready. Enable 'Allow information gaps' or complete all items.",
                    )}
                  </p>
                )}
              </div>
            </div>
            <SubmitArea
              projectId={projectId}
              projectState={projectState}
              onSubmitted={handleSubmitted}
            />
          </CollapsibleSection>
        </div>
      )}
    </div>
  );
}
