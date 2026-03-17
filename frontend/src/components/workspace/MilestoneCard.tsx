import { useState } from "react";
import { useSortable } from "@dnd-kit/sortable";
import {
  SortableContext,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import {
  ChevronDown,
  ChevronRight,
  GripVertical,
  Pencil,
  Plus,
  Trash2,
} from "lucide-react";
import { WorkPackageCard } from "./WorkPackageCard";
import type { RequirementsItem } from "@/api/projects";

interface MilestoneCardProps {
  item: RequirementsItem;
  onEdit: (itemId: string) => void;
  onDelete: (itemId: string) => void;
  onEditChild: (parentId: string, childId: string) => void;
  onDeleteChild: (parentId: string, childId: string) => void;
  onAddChild: (parentId: string) => void;
  readOnly?: boolean;
}

export function MilestoneCard({
  item,
  onEdit,
  onDelete,
  onEditChild,
  onDeleteChild,
  onAddChild,
  readOnly,
}: MilestoneCardProps) {
  const [expanded, setExpanded] = useState(true);

  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: item.id,
    data: { type: "parent" },
    disabled: readOnly,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const childIds = item.children.map((c) => c.id);

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="rounded-md border border-border bg-card"
      data-testid={`milestone-card-${item.id}`}
    >
      {/* Header */}
      <div className="flex items-center gap-2 p-3">
        {!readOnly && (
          <button
            className="cursor-grab text-muted-foreground hover:text-foreground"
            {...attributes}
            {...listeners}
            data-testid={`drag-handle-${item.id}`}
          >
            <GripVertical className="h-4 w-4" />
          </button>
        )}
        <button
          className="text-muted-foreground hover:text-foreground"
          onClick={() => setExpanded((prev) => !prev)}
          data-testid={`toggle-${item.id}`}
        >
          {expanded ? (
            <ChevronDown className="h-4 w-4" />
          ) : (
            <ChevronRight className="h-4 w-4" />
          )}
        </button>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold text-foreground">{item.title}</p>
          {!expanded && item.description && (
            <p className="line-clamp-1 text-xs text-muted-foreground">
              {item.description}
            </p>
          )}
          {!expanded && item.children.length > 0 && (
            <p className="text-xs text-muted-foreground">
              {item.children.length} work{" "}
              {item.children.length === 1 ? "package" : "packages"}
            </p>
          )}
        </div>
        {!readOnly && (
          <div className="flex shrink-0 gap-1">
            <button
              className="rounded p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
              onClick={() => onEdit(item.id)}
              data-testid={`edit-item-${item.id}`}
            >
              <Pencil className="h-3.5 w-3.5" />
            </button>
            <button
              className="rounded p-1 text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
              onClick={() => onDelete(item.id)}
              data-testid={`delete-item-${item.id}`}
            >
              <Trash2 className="h-3.5 w-3.5" />
            </button>
          </div>
        )}
      </div>

      {/* Expanded content */}
      {expanded && (
        <div className="border-t border-border px-3 pb-3 pt-2">
          {item.description && (
            <p className="mb-2 text-xs text-muted-foreground line-clamp-2">
              {item.description}
            </p>
          )}
          <SortableContext
            items={childIds}
            strategy={verticalListSortingStrategy}
          >
            <div className="flex flex-col gap-2">
              {item.children.map((child) => (
                <WorkPackageCard
                  key={child.id}
                  child={child}
                  parentId={item.id}
                  onEdit={onEditChild}
                  onDelete={onDeleteChild}
                  readOnly={readOnly}
                />
              ))}
            </div>
          </SortableContext>
          {!readOnly && (
            <button
              className="mt-2 flex items-center gap-1 rounded px-2 py-1 text-xs text-muted-foreground hover:bg-muted hover:text-foreground"
              onClick={() => onAddChild(item.id)}
              data-testid={`add-child-${item.id}`}
            >
              <Plus className="h-3.5 w-3.5" />
              Add Work Package
            </button>
          )}
        </div>
      )}
    </div>
  );
}
