import { useCallback, useEffect, useRef, useState } from "react";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { Plus, Loader2 } from "lucide-react";
import { toast } from "react-toastify";
import { useTranslation } from "react-i18next";
import { EpicCard } from "./EpicCard";
import { MilestoneCard } from "./MilestoneCard";
import {
  RequirementsItemEditor,
  type EditorMode,
} from "./RequirementsItemEditor";
import type {
  ProjectType,
  RequirementsDraft,
  RequirementsItem,
} from "@/api/projects";
import {
  fetchRequirements,
  patchRequirements,
  addRequirementsItem,
  patchRequirementsItem,
  deleteRequirementsItem,
  addRequirementsChild,
  patchRequirementsChild,
  deleteRequirementsChild,
  reorderRequirements,
} from "@/api/projects";
import { useLazyProject } from "@/hooks/use-lazy-project";

interface RequirementsPanelProps {
  projectId: string;
  projectType: ProjectType;
  readOnly?: boolean;
  collaborators?: Array<{ user_id: string; display_name: string }>;
  projectTitle?: string;
  showHeader?: boolean;
}

export function RequirementsPanel({
  projectId,
  projectType,
  readOnly,
  collaborators,
  projectTitle,
  showHeader = true,
}: RequirementsPanelProps) {
  const { t } = useTranslation();
  const { ensureProject, isDraft } = useLazyProject();
  const [draft, setDraft] = useState<RequirementsDraft | null>(null);
  const [loading, setLoading] = useState(true);
  const [editorMode, setEditorMode] = useState<EditorMode | null>(null);
  const [saving, setSaving] = useState(false);
  const [aiGenerating, setAiGenerating] = useState(false);
  const [bannerVisible, setBannerVisible] = useState(false);

  const structureVersionRef = useRef(0);

  // Fetch requirements on mount (skip for draft projects)
  useEffect(() => {
    if (isDraft) {
      setDraft({
        title: null,
        short_description: null,
        structure: [],
        item_locks: {},
        allow_information_gaps: false,
        readiness_evaluation: {},
      });
      setLoading(false);
      return;
    }
    let cancelled = false;
    setLoading(true);
    fetchRequirements(projectId)
      .then((data) => {
        if (!cancelled) {
          setDraft(data);
          setLoading(false);
        }
      })
      .catch(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [projectId]);

  // WebSocket real-time sync
  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail.project_id !== projectId) return;
      const payload = detail.payload ?? detail;
      if (payload.structure) {
        structureVersionRef.current += 1;
        setDraft((prev) =>
          prev
            ? { ...prev, structure: payload.structure }
            : prev,
        );
        if (payload.updated_by) {
          toast.info("Requirements updated by another user", {
            toastId: "req-conflict",
          });
        }
      }
    };
    window.addEventListener("ws:requirements_updated", handler);
    return () => window.removeEventListener("ws:requirements_updated", handler);
  }, [projectId]);

  // Listen for title_update to sync project title into draft
  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail.project_id !== projectId) return;
      if (detail.title != null) {
        setDraft((prev) => (prev ? { ...prev, title: detail.title } : prev));
      }
    };
    window.addEventListener("ws:title_update", handler);
    return () => window.removeEventListener("ws:title_update", handler);
  }, [projectId]);

  // Listen for requirements_ready (AI generation complete)
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
        setAiGenerating(false);
      }
    };
    window.addEventListener("ws:requirements_ready", handler);
    return () => window.removeEventListener("ws:requirements_ready", handler);
  }, [projectId]);

  // Track AI processing state for the generating banner
  useEffect(() => {
    let fallbackTimer: ReturnType<typeof setTimeout> | null = null;

    const handleProcessing = (e: Event) => {
      const { project_id, state } = (e as CustomEvent).detail;
      if (project_id !== projectId) return;
      if (state === "started") {
        if (fallbackTimer) clearTimeout(fallbackTimer);
        setAiGenerating(true);
      } else if (state === "failed") {
        if (fallbackTimer) clearTimeout(fallbackTimer);
        setAiGenerating(false);
      } else if (state === "completed") {
        // Chat response is done but requirements may still arrive.
        // Set a fallback timeout so the banner doesn't stay forever
        // if the AI decided not to update requirements this turn.
        fallbackTimer = setTimeout(() => setAiGenerating(false), 15_000);
      }
    };
    window.addEventListener("ws:ai_processing", handleProcessing);
    return () => {
      window.removeEventListener("ws:ai_processing", handleProcessing);
      if (fallbackTimer) clearTimeout(fallbackTimer);
    };
  }, [projectId]);

  // Keep banner in DOM during exit animation
  useEffect(() => {
    if (aiGenerating) {
      setBannerVisible(true);
    }
    // When aiGenerating turns false, bannerVisible stays true
    // until the CSS animation ends (handled by onAnimationEnd)
  }, [aiGenerating]);

  // Title/description inline edit
  const [editingTitle, setEditingTitle] = useState(false);
  const [editingDesc, setEditingDesc] = useState(false);
  const [titleValue, setTitleValue] = useState("");
  const [descValue, setDescValue] = useState("");

  const handleTitleSave = useCallback(async () => {
    setEditingTitle(false);
    if (!draft || titleValue === (draft.title ?? "")) return;
    const prev = draft;
    setDraft({ ...draft, title: titleValue });
    try {
      const realId = await ensureProject();
      await patchRequirements(realId, { title: titleValue });
    } catch {
      setDraft(prev);
    }
  }, [draft, ensureProject, titleValue]);

  const handleDescSave = useCallback(async () => {
    setEditingDesc(false);
    if (!draft || descValue === (draft.short_description ?? "")) return;
    const prev = draft;
    setDraft({ ...draft, short_description: descValue });
    try {
      const realId = await ensureProject();
      await patchRequirements(realId, { short_description: descValue });
    } catch {
      setDraft(prev);
    }
  }, [draft, ensureProject, descValue]);

  // DnD sensors
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
  );

  const handleDragEnd = useCallback(
    async (event: DragEndEvent) => {
      if (!draft) return;
      const { active, over } = event;
      if (!over || active.id === over.id) return;

      const activeData = active.data.current as
        | { type: "parent" }
        | { type: "child"; parentId: string }
        | undefined;

      if (!activeData) return;

      if (activeData.type === "parent") {
        // Reorder top-level items
        const oldIndex = draft.structure.findIndex(
          (item) => item.id === active.id,
        );
        const newIndex = draft.structure.findIndex(
          (item) => item.id === over.id,
        );
        if (oldIndex === -1 || newIndex === -1) return;

        const newStructure = [...draft.structure];
        const [moved] = newStructure.splice(oldIndex, 1);
        if (moved) {
          newStructure.splice(newIndex, 0, moved);
          setDraft({ ...draft, structure: newStructure });
          try {
            const realId = await ensureProject();
            await reorderRequirements(
              realId,
              newStructure.map((s) => s.id),
            );
          } catch {
            setDraft({ ...draft }); // revert on failure
          }
        }
      } else if (activeData.type === "child") {
        // Reorder children within/between parents
        const overData = over.data.current as
          | { type: "parent" }
          | { type: "child"; parentId: string }
          | undefined;

        const sourceParentId = activeData.parentId;
        const targetParentId =
          overData?.type === "child"
            ? overData.parentId
            : overData?.type === "parent"
              ? (over.id as string)
              : sourceParentId;

        const newStructure = draft.structure.map((item) => ({
          ...item,
          children: [...item.children],
        }));

        const sourceParent = newStructure.find(
          (p) => p.id === sourceParentId,
        );
        const targetParent = newStructure.find(
          (p) => p.id === targetParentId,
        );
        if (!sourceParent || !targetParent) return;

        const childIndex = sourceParent.children.findIndex(
          (c) => c.id === active.id,
        );
        if (childIndex === -1) return;
        const [child] = sourceParent.children.splice(childIndex, 1);
        if (!child) return;

        if (sourceParentId === targetParentId) {
          const overIndex = targetParent.children.findIndex(
            (c) => c.id === over.id,
          );
          targetParent.children.splice(
            overIndex === -1 ? targetParent.children.length : overIndex,
            0,
            child,
          );
        } else {
          const overIndex = targetParent.children.findIndex(
            (c) => c.id === over.id,
          );
          targetParent.children.splice(
            overIndex === -1 ? targetParent.children.length : overIndex,
            0,
            child,
          );
        }

        setDraft({ ...draft, structure: newStructure });
        try {
          const realId = await ensureProject();
          await reorderRequirements(
            realId,
            newStructure.map((s) => s.id),
          );
        } catch {
          setDraft({ ...draft }); // revert
        }
      }
    },
    [draft, ensureProject],
  );

  // Editor handlers
  const handleEditItem = useCallback(
    (itemId: string) => {
      if (!draft) return;
      const item = draft.structure.find((i) => i.id === itemId);
      if (!item) return;
      setEditorMode({
        kind: "edit-parent",
        itemId,
        title: item.title,
        description: item.description,
      });
    },
    [draft],
  );

  const handleDeleteItem = useCallback(
    async (itemId: string) => {
      if (!draft) return;
      const prev = draft;
      setDraft({
        ...draft,
        structure: draft.structure.filter((i) => i.id !== itemId),
      });
      try {
        const realId = await ensureProject();
        await deleteRequirementsItem(realId, itemId);
      } catch {
        setDraft(prev);
      }
    },
    [draft, ensureProject],
  );

  const handleEditChild = useCallback(
    (parentId: string, childId: string) => {
      if (!draft) return;
      const parent = draft.structure.find((i) => i.id === parentId);
      const child = parent?.children.find((c) => c.id === childId);
      if (!child) return;
      setEditorMode({
        kind: "edit-child",
        parentId,
        childId,
        title: child.title,
        description: child.description,
        acceptanceCriteria: child.acceptance_criteria ?? [],
        deliverables: child.deliverables ?? [],
        dependencies: child.dependencies ?? [],
        priority: (child.priority as "high" | "medium" | "low") ?? "",
      });
    },
    [draft],
  );

  const handleDeleteChild = useCallback(
    async (parentId: string, childId: string) => {
      if (!draft) return;
      const prev = draft;
      setDraft({
        ...draft,
        structure: draft.structure.map((item) =>
          item.id === parentId
            ? { ...item, children: item.children.filter((c) => c.id !== childId) }
            : item,
        ),
      });
      try {
        const realId = await ensureProject();
        await deleteRequirementsChild(realId, parentId, childId);
      } catch {
        setDraft(prev);
      }
    },
    [draft, ensureProject],
  );

  const handleAddChild = useCallback(
    (parentId: string) => {
      setEditorMode({ kind: "add-child", parentId, projectType });
    },
    [projectType],
  );

  const handleEditorSave = useCallback(
    async (data: Record<string, unknown>) => {
      if (!draft || !editorMode) return;
      setSaving(true);
      try {
        const realId = await ensureProject();
        if (editorMode.kind === "add-parent") {
          const item = await addRequirementsItem(
            realId,
            data as { title: string; description?: string; type: "epic" | "milestone" },
          );
          setDraft({
            ...draft,
            structure: [...draft.structure, item],
          });
        } else if (editorMode.kind === "edit-parent") {
          const updated = await patchRequirementsItem(
            realId,
            editorMode.itemId,
            data as { title?: string; description?: string },
          );
          setDraft({
            ...draft,
            structure: draft.structure.map((item) =>
              item.id === editorMode.itemId ? { ...item, ...updated } : item,
            ),
          });
        } else if (editorMode.kind === "add-child") {
          const child = await addRequirementsChild(
            realId,
            editorMode.parentId,
            data as { title: string; description?: string },
          );
          setDraft({
            ...draft,
            structure: draft.structure.map((item) =>
              item.id === editorMode.parentId
                ? { ...item, children: [...item.children, child] }
                : item,
            ),
          });
        } else if (editorMode.kind === "edit-child") {
          const updated = await patchRequirementsChild(
            realId,
            editorMode.parentId,
            editorMode.childId,
            data as { title?: string; description?: string },
          );
          setDraft({
            ...draft,
            structure: draft.structure.map((item) =>
              item.id === editorMode.parentId
                ? {
                    ...item,
                    children: item.children.map((c) =>
                      c.id === editorMode.childId ? { ...c, ...updated } : c,
                    ),
                  }
                : item,
            ),
          });
        }
        setEditorMode(null);
      } catch {
        toast.error("Failed to save changes");
      } finally {
        setSaving(false);
      }
    },
    [draft, editorMode, ensureProject],
  );

  if (loading) {
    return (
      <div
        className="flex h-full items-center justify-center text-muted-foreground"
        data-testid="requirements-loading"
      >
        Loading requirements...
      </div>
    );
  }

  if (!draft) {
    return (
      <div
        className="flex h-full items-center justify-center text-muted-foreground"
        data-testid="requirements-empty"
      >
        No requirements found
      </div>
    );
  }

  const isSoftware = projectType === "software";
  const itemIds = draft.structure.map((item) => item.id);

  return (
    <div
      className="flex h-full flex-col overflow-hidden"
      data-testid="requirements-panel"
    >
      {/* Header section — hidden on the define step */}
      {showHeader && (
        <div className="shrink-0 border-b border-border p-4">
          {editingTitle ? (
            <input
              className="w-full rounded border border-border bg-background px-2 py-1 text-lg font-semibold text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              value={titleValue}
              onChange={(e) => setTitleValue(e.target.value)}
              onBlur={handleTitleSave}
              onKeyDown={(e) => e.key === "Enter" && handleTitleSave()}
              autoFocus
              data-testid="requirements-title-input"
            />
          ) : (
            <h2
              className="cursor-pointer text-lg font-semibold text-foreground hover:underline"
              onClick={() => {
                if (!readOnly) {
                  setTitleValue(draft.title ?? "");
                  setEditingTitle(true);
                }
              }}
              data-testid="requirements-title"
            >
              {draft.title || projectTitle || "Untitled Project"}
            </h2>
          )}
          {editingDesc ? (
            <textarea
              className="mt-1 w-full rounded border border-border bg-background px-2 py-1 text-sm text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary resize-none"
              value={descValue}
              onChange={(e) => setDescValue(e.target.value)}
              onBlur={handleDescSave}
              autoFocus
              data-testid="requirements-desc-input"
            />
          ) : (
            <p
              className="mt-1 cursor-pointer text-sm text-muted-foreground hover:underline"
              onClick={() => {
                if (!readOnly) {
                  setDescValue(draft.short_description ?? "");
                  setEditingDesc(true);
                }
              }}
              data-testid="requirements-description"
            >
              {draft.short_description || "Click to add a description..."}
            </p>
          )}
          {collaborators && collaborators.length > 0 && (
            <div
              className="mt-2 flex items-center gap-1"
              data-testid="requirements-contributors"
            >
              {collaborators.map((c) => (
                <span
                  key={c.user_id}
                  className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-primary/10 text-xs font-medium text-primary"
                  title={c.display_name}
                >
                  {c.display_name.charAt(0).toUpperCase()}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* AI generating banner */}
      {bannerVisible && (
        <div
          className={`shrink-0 flex items-center gap-3 border-b border-primary/20 bg-primary/5 px-4 py-3 overflow-hidden ${
            aiGenerating ? "animate-banner-in" : "animate-banner-out"
          }`}
          role="status"
          aria-live="polite"
          data-testid="requirements-generating-banner"
          onAnimationEnd={() => {
            if (!aiGenerating) setBannerVisible(false);
          }}
        >
          <Loader2 className="h-4 w-4 animate-spin text-primary" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-foreground">
              {t("requirements.generating.title", "Structuring requirements...")}
            </p>
            <p className="text-xs text-muted-foreground">
              {isSoftware
                ? t("requirements.generating.subtitleSoftware", "Epics and user stories will appear shortly")
                : t("requirements.generating.subtitleNonSoftware", "Milestones and work packages will appear shortly")}
            </p>
          </div>
          <div className="flex gap-1" aria-hidden="true">
            <span className="h-1.5 w-1.5 rounded-full bg-primary/40 animate-pulse" style={{ animationDelay: "0ms" }} />
            <span className="h-1.5 w-1.5 rounded-full bg-primary/40 animate-pulse" style={{ animationDelay: "300ms" }} />
            <span className="h-1.5 w-1.5 rounded-full bg-primary/40 animate-pulse" style={{ animationDelay: "600ms" }} />
          </div>
        </div>
      )}

      {/* Items list */}
      <div className="flex-1 overflow-y-auto p-4">
        {!readOnly && (
          <button
            className="mb-3 flex items-center gap-1.5 rounded-md border border-dashed border-border px-3 py-2 text-sm text-muted-foreground hover:border-primary hover:text-foreground"
            onClick={() =>
              setEditorMode({ kind: "add-parent", projectType })
            }
            data-testid="add-item-button"
          >
            <Plus className="h-4 w-4" />
            {isSoftware ? "Add Epic" : "Add Milestone"}
          </button>
        )}

        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
        >
          <SortableContext
            items={itemIds}
            strategy={verticalListSortingStrategy}
          >
            <div className="flex flex-col gap-3">
              {draft.structure.map((item: RequirementsItem) =>
                isSoftware ? (
                  <EpicCard
                    key={item.id}
                    item={item}
                    onEdit={handleEditItem}
                    onDelete={handleDeleteItem}
                    onEditChild={handleEditChild}
                    onDeleteChild={handleDeleteChild}
                    onAddChild={handleAddChild}
                    readOnly={readOnly}
                  />
                ) : (
                  <MilestoneCard
                    key={item.id}
                    item={item}
                    onEdit={handleEditItem}
                    onDelete={handleDeleteItem}
                    onEditChild={handleEditChild}
                    onDeleteChild={handleDeleteChild}
                    onAddChild={handleAddChild}
                    readOnly={readOnly}
                  />
                ),
              )}
            </div>
          </SortableContext>
        </DndContext>

        {draft.structure.length === 0 && (
          <p className="mt-8 text-center text-sm text-muted-foreground">
            No {isSoftware ? "epics" : "milestones"} yet.{" "}
            {!readOnly && "Click the button above to add one."}
          </p>
        )}
      </div>

      <RequirementsItemEditor
        mode={editorMode}
        onClose={() => setEditorMode(null)}
        onSave={handleEditorSave}
        saving={saving}
      />
    </div>
  );
}
