import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { GripVertical, Pencil, Trash2 } from "lucide-react";
import type { RequirementsChild } from "@/api/projects";

interface UserStoryCardProps {
  child: RequirementsChild;
  parentId: string;
  onEdit: (parentId: string, childId: string) => void;
  onDelete: (parentId: string, childId: string) => void;
  readOnly?: boolean;
}

export function UserStoryCard({
  child,
  parentId,
  onEdit,
  onDelete,
  readOnly,
}: UserStoryCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: child.id,
    data: { type: "child", parentId },
    disabled: readOnly,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="flex items-start gap-2 rounded border border-border bg-background p-3"
      data-testid={`user-story-card-${child.id}`}
    >
      {!readOnly && (
        <button
          className="mt-0.5 cursor-grab text-muted-foreground hover:text-foreground"
          {...attributes}
          {...listeners}
          data-testid={`drag-handle-${child.id}`}
        >
          <GripVertical className="h-4 w-4" />
        </button>
      )}
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-foreground">{child.title}</p>
        {child.description && (
          <p className="mt-0.5 line-clamp-2 text-xs text-muted-foreground">
            {child.description}
          </p>
        )}
        {child.acceptance_criteria && child.acceptance_criteria.length > 0 && (
          <div className="mt-1.5 flex flex-wrap gap-1">
            {child.acceptance_criteria.map((c, i) => (
              <span
                key={i}
                className="inline-flex items-center rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground"
              >
                &#10003; {c}
              </span>
            ))}
          </div>
        )}
        {child.priority && (
          <span
            className={`mt-1.5 inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
              child.priority === "high"
                ? "bg-red-100 text-red-700 dark:bg-red-950/30 dark:text-red-400"
                : child.priority === "medium"
                  ? "bg-amber-100 text-amber-700 dark:bg-amber-950/30 dark:text-amber-400"
                  : "bg-green-100 text-green-700 dark:bg-green-950/30 dark:text-green-400"
            }`}
          >
            {child.priority}
          </span>
        )}
      </div>
      {!readOnly && (
        <div className="flex shrink-0 gap-1">
          <button
            className="rounded p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
            onClick={() => onEdit(parentId, child.id)}
            data-testid={`edit-child-${child.id}`}
          >
            <Pencil className="h-3.5 w-3.5" />
          </button>
          <button
            className="rounded p-1 text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
            onClick={() => onDelete(parentId, child.id)}
            data-testid={`delete-child-${child.id}`}
          >
            <Trash2 className="h-3.5 w-3.5" />
          </button>
        </div>
      )}
    </div>
  );
}
