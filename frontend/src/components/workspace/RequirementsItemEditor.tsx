import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { ProjectType } from "@/api/projects";

export type EditorMode =
  | { kind: "add-parent"; projectType: ProjectType }
  | { kind: "edit-parent"; itemId: string; title: string; description: string }
  | {
      kind: "add-child";
      parentId: string;
      projectType: ProjectType;
    }
  | {
      kind: "edit-child";
      parentId: string;
      childId: string;
      title: string;
      description: string;
      acceptanceCriteria: string[];
      deliverables: string[];
      dependencies: string[];
      priority: "high" | "medium" | "low" | "";
    };

interface RequirementsItemEditorProps {
  mode: EditorMode | null;
  onClose: () => void;
  onSave: (data: Record<string, unknown>) => void;
  saving?: boolean;
}

export function RequirementsItemEditor({
  mode,
  onClose,
  onSave,
  saving,
}: RequirementsItemEditorProps) {
  if (!mode) return null;
  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-md">
        <EditorForm mode={mode} onSave={onSave} saving={saving} />
      </DialogContent>
    </Dialog>
  );
}

function EditorForm({
  mode,
  onSave,
  saving,
}: {
  mode: EditorMode;
  onSave: (data: Record<string, unknown>) => void;
  saving?: boolean;
}) {
  const isParent =
    mode.kind === "add-parent" || mode.kind === "edit-parent";
  const isAdd = mode.kind === "add-parent" || mode.kind === "add-child";

  const [title, setTitle] = useState(
    mode.kind === "edit-parent"
      ? mode.title
      : mode.kind === "edit-child"
        ? mode.title
        : "",
  );
  const [description, setDescription] = useState(
    mode.kind === "edit-parent"
      ? mode.description
      : mode.kind === "edit-child"
        ? mode.description
        : "",
  );
  const [criteriaText, setCriteriaText] = useState(
    mode.kind === "edit-child" ? mode.acceptanceCriteria.join("\n") : "",
  );
  const [deliverablesText, setDeliverablesText] = useState(
    mode.kind === "edit-child" ? mode.deliverables.join("\n") : "",
  );
  const [depsText, setDepsText] = useState(
    mode.kind === "edit-child" ? mode.dependencies.join("\n") : "",
  );
  const [priority, setPriority] = useState(
    mode.kind === "edit-child" ? mode.priority : "",
  );

  const isSoftware =
    (mode.kind === "add-parent" || mode.kind === "add-child") &&
    mode.projectType === "software";
  const isNonSoftware =
    (mode.kind === "add-parent" || mode.kind === "add-child") &&
    mode.projectType === "non_software";
  const showChildFields = !isParent;
  const showStoryFields =
    showChildFields &&
    (isSoftware ||
      (mode.kind === "edit-child" &&
        !mode.deliverables.length &&
        !mode.dependencies.length &&
        (mode.acceptanceCriteria.length > 0 || mode.priority !== "")));
  const showPackageFields = showChildFields && !showStoryFields;

  const heading = isAdd
    ? isParent
      ? isSoftware
        ? "Add Epic"
        : "Add Milestone"
      : isSoftware
        ? "Add User Story"
        : isNonSoftware
          ? "Add Work Package"
          : "Add Item"
    : isParent
      ? "Edit Item"
      : "Edit Item";

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const data: Record<string, unknown> = { title, description };
    if (!isParent) {
      if (showStoryFields || (mode.kind === "edit-child" && !showPackageFields)) {
        data.acceptance_criteria = criteriaText
          .split("\n")
          .map((s) => s.trim())
          .filter(Boolean);
        if (priority) data.priority = priority;
      }
      if (showPackageFields) {
        data.deliverables = deliverablesText
          .split("\n")
          .map((s) => s.trim())
          .filter(Boolean);
        data.dependencies = depsText
          .split("\n")
          .map((s) => s.trim())
          .filter(Boolean);
      }
    }
    if (mode.kind === "add-parent") {
      data.type = mode.projectType === "software" ? "epic" : "milestone";
    }
    onSave(data);
  };

  return (
    <form onSubmit={handleSubmit}>
      <DialogHeader>
        <DialogTitle>{heading}</DialogTitle>
        <DialogDescription>
          {isAdd ? "Fill in the details below." : "Update the details below."}
        </DialogDescription>
      </DialogHeader>
      <div className="mt-4 flex flex-col gap-3">
        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium text-foreground">Title</span>
          <input
            className="rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            data-testid="editor-title"
          />
        </label>
        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium text-foreground">
            Description
          </span>
          <textarea
            className="min-h-16 rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary resize-none"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            data-testid="editor-description"
          />
        </label>
        {showChildFields && (showStoryFields || (!showPackageFields && mode.kind === "add-child")) && (
          <>
            <label className="flex flex-col gap-1">
              <span className="text-sm font-medium text-foreground">
                Acceptance Criteria (one per line)
              </span>
              <textarea
                className="min-h-16 rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                value={criteriaText}
                onChange={(e) => setCriteriaText(e.target.value)}
                data-testid="editor-criteria"
              />
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-sm font-medium text-foreground">
                Priority
              </span>
              <select
                className="rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                value={priority}
                onChange={(e) => setPriority(e.target.value as "" | "high" | "medium" | "low")}
                data-testid="editor-priority"
              >
                <option value="">None</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </label>
          </>
        )}
        {showChildFields && showPackageFields && (
          <>
            <label className="flex flex-col gap-1">
              <span className="text-sm font-medium text-foreground">
                Deliverables (one per line)
              </span>
              <textarea
                className="min-h-16 rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                value={deliverablesText}
                onChange={(e) => setDeliverablesText(e.target.value)}
                data-testid="editor-deliverables"
              />
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-sm font-medium text-foreground">
                Dependencies (one per line)
              </span>
              <textarea
                className="min-h-16 rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                value={depsText}
                onChange={(e) => setDepsText(e.target.value)}
                data-testid="editor-dependencies"
              />
            </label>
          </>
        )}
      </div>
      <DialogFooter className="mt-4">
        <Button type="submit" disabled={!title.trim() || saving} data-testid="editor-save">
          {saving ? "Saving..." : isAdd ? "Add" : "Save"}
        </Button>
      </DialogFooter>
    </form>
  );
}
