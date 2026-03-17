import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { MoreVertical, Trash2, RotateCcw } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { formatRelativeTime } from "@/lib/utils";

export type ProjectState =
  | "open"
  | "in_review"
  | "accepted"
  | "dropped"
  | "rejected";

const STATE_DOT_COLORS: Record<ProjectState, string> = {
  open: "#0284C7",
  in_review: "#F59E0B",
  accepted: "#16A34A",
  dropped: "#9CA3AF",
  rejected: "#F97316",
};

const STATE_LABELS: Record<ProjectState, string> = {
  open: "Open",
  in_review: "In Review",
  accepted: "Accepted",
  dropped: "Dropped",
  rejected: "Rejected",
};

export interface ProjectCardProps {
  id: string;
  title: string;
  state: ProjectState;
  updatedAt: string;
  deletedAt?: string | null;
  onDelete?: (id: string) => void;
  onRestore?: (id: string) => void;
}

export function ProjectCard({
  id,
  title,
  state,
  updatedAt,
  deletedAt,
  onDelete,
  onRestore,
}: ProjectCardProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const isTrash = !!deletedAt;

  return (
    <button
      type="button"
      className="flex w-full cursor-pointer items-center gap-3 rounded-md border border-border bg-background p-3 text-left transition-colors hover:bg-muted dark:bg-muted/40 dark:hover:bg-muted"
      onClick={() => navigate(`/project/${id}`)}
    >
      <span
        className="shrink-0 rounded-full"
        style={{
          width: 8,
          height: 8,
          backgroundColor: STATE_DOT_COLORS[state],
        }}
        aria-label={STATE_LABELS[state]}
      />

      <div className="min-w-0 flex-1">
        <p className="truncate text-base font-medium text-foreground">
          {title || t("landing.untitled")}
        </p>
        <p className="text-sm text-text-secondary">
          {t("landing.ideaCard.lastUpdated", {
            time: formatRelativeTime(updatedAt),
          })}
        </p>
      </div>

      <Badge variant={state} className="shrink-0">
        {STATE_LABELS[state]}
      </Badge>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <span
            role="button"
            tabIndex={0}
            className="shrink-0 rounded-md p-1.5 text-text-secondary hover:bg-muted"
            onClick={(e) => e.stopPropagation()}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.stopPropagation();
              }
            }}
          >
            <MoreVertical className="h-4 w-4" />
          </span>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          {isTrash ? (
            <DropdownMenuItem
              onClick={(e) => {
                e.stopPropagation();
                onRestore?.(id);
              }}
            >
              <RotateCcw className="mr-2 h-4 w-4" />
              {t("landing.ideaCard.restore")}
            </DropdownMenuItem>
          ) : (
            <DropdownMenuItem
              onClick={(e) => {
                e.stopPropagation();
                onDelete?.(id);
              }}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              {t("landing.ideaCard.delete")}
            </DropdownMenuItem>
          )}
        </DropdownMenuContent>
      </DropdownMenu>
    </button>
  );
}
