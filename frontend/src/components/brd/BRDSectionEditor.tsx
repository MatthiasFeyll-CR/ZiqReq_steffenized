import { useCallback, useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import { X } from "lucide-react";
import { toast } from "react-toastify";
import { Switch } from "@/components/ui/switch";
import { SectionField } from "./SectionField";
import { ProgressIndicator, SECTION_KEYS } from "./ProgressIndicator";
import { patchBrdDraft, triggerBrdGeneration } from "@/api/brd";
import type { BrdDraft } from "@/api/brd";

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

interface BRDSectionEditorProps {
  ideaId: string;
  brdDraft: BrdDraft;
  open: boolean;
  onClose: () => void;
}

export function BRDSectionEditor({
  ideaId,
  brdDraft,
  open,
  onClose,
}: BRDSectionEditorProps) {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const debounceTimers = useRef<Record<string, ReturnType<typeof setTimeout>>>({});
  const [regeneratingSection, setRegeneratingSection] = useState<string | null>(null);

  // Local state for section content (to enable editing without waiting for server)
  const [localSections, setLocalSections] = useState<Record<string, string>>({});

  // Sync local state when brdDraft changes (e.g., after regeneration)
  useEffect(() => {
    const sections: Record<string, string> = {};
    for (const key of SECTION_KEYS) {
      sections[key] = brdDraft[sectionKeyToFieldKey(key)] ?? "";
    }
    setLocalSections(sections);
  }, [brdDraft]);

  const patchMutation = useMutation({
    mutationFn: (data: Parameters<typeof patchBrdDraft>[1]) =>
      patchBrdDraft(ideaId, data),
    onSuccess: (updated) => {
      queryClient.setQueryData(["brd", ideaId], updated);
    },
    onError: (error: Error) => {
      toast.error(error.message || t("brd.saveError", "Failed to save changes"));
    },
  });

  const handleContentChange = useCallback(
    (sectionKey: string, value: string) => {
      setLocalSections((prev) => ({ ...prev, [sectionKey]: value }));

      // Auto-lock on edit: optimistic
      if (!brdDraft.section_locks[sectionKey]) {
        const newLocks = { ...brdDraft.section_locks, [sectionKey]: true };
        queryClient.setQueryData(["brd", ideaId], {
          ...brdDraft,
          section_locks: newLocks,
        });
      }

      // Debounced save (300ms)
      if (debounceTimers.current[sectionKey]) {
        clearTimeout(debounceTimers.current[sectionKey]);
      }
      debounceTimers.current[sectionKey] = setTimeout(() => {
        const fieldKey = sectionKeyToFieldKey(sectionKey);
        patchMutation.mutate({ [fieldKey]: value });
      }, 300);
    },
    [brdDraft, ideaId, queryClient, patchMutation],
  );

  const handleBlur = useCallback(
    (sectionKey: string, value: string) => {
      // Clear any pending debounce and save immediately
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
      const newLocks = { ...brdDraft.section_locks, [sectionKey]: locked };
      patchMutation.mutate({ section_locks: newLocks });
    },
    [brdDraft.section_locks, patchMutation],
  );

  const handleRegenerate = useCallback(
    async (sectionKey: string) => {
      try {
        setRegeneratingSection(sectionKey);
        await triggerBrdGeneration(ideaId, "section_regeneration", sectionKey);
        queryClient.invalidateQueries({ queryKey: ["brd", ideaId] });
      } catch (error) {
        toast.error(
          (error as Error).message ||
            t("brd.regenerateError", "Failed to regenerate section"),
        );
      } finally {
        setRegeneratingSection(null);
      }
    },
    [ideaId, queryClient, t],
  );

  const handleGapsToggle = useCallback(
    (checked: boolean) => {
      patchMutation.mutate({ allow_information_gaps: checked });
    },
    [patchMutation],
  );

  // Cleanup debounce timers on unmount
  useEffect(() => {
    const timers = debounceTimers.current;
    return () => {
      Object.values(timers).forEach(clearTimeout);
    };
  }, []);

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ x: "100%" }}
          animate={{ x: 0 }}
          exit={{ x: "100%" }}
          transition={{ type: "tween", duration: 0.25, ease: "easeOut" }}
          className="absolute inset-0 z-10 bg-background flex flex-col overflow-hidden"
          data-testid="brd-section-editor"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b shrink-0">
            <h2 className="text-lg font-semibold">
              {t("brd.editDocument", "Edit Document")}
            </h2>
            <button
              type="button"
              className="p-1 rounded hover:bg-muted text-muted-foreground"
              onClick={onClose}
              data-testid="editor-close-button"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Progress indicator + gaps toggle */}
          <div className="px-4 py-3 border-b space-y-3 shrink-0">
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
          </div>

          {/* Sections */}
          <div className="flex-1 overflow-y-auto px-4 py-4 space-y-6">
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
        </motion.div>
      )}
    </AnimatePresence>
  );
}
