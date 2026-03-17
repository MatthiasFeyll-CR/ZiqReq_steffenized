import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { MoreVertical, Trash2, RotateCcw, Star } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
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

export type ProjectType = "software" | "non_software";

export interface ProjectCardProps {
  id: string;
  title: string;
  projectType?: ProjectType;
  state: ProjectState;
  updatedAt: string;
  deletedAt?: string | null;
  isHighlighted?: boolean;
  onDelete?: (id: string) => void;
  onRestore?: (id: string) => void;
  onToggleFavorite?: (id: string) => void;
}

export function ProjectCard({
  id,
  title,
  projectType,
  state,
  updatedAt,
  deletedAt,
  isHighlighted,
  onDelete,
  onRestore,
  onToggleFavorite,
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
          {t("landing.projectCard.lastUpdated", {
            time: formatRelativeTime(updatedAt),
          })}
        </p>
      </div>

      {projectType && (
        <span className="shrink-0 rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
          {t(`projectType.${projectType === "software" ? "software" : "nonSoftware"}`)}
        </span>
      )}

      <Badge variant={state} className="shrink-0">
        {STATE_LABELS[state]}
      </Badge>

      {onToggleFavorite && (
        <TooltipProvider delayDuration={300}>
          <Tooltip>
            <TooltipTrigger asChild>
              <span
                role="button"
                tabIndex={0}
                className="shrink-0 rounded-md p-1.5 text-text-secondary hover:bg-muted"
                onClick={(e) => {
                  e.stopPropagation();
                  onToggleFavorite(id);
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.stopPropagation();
                    onToggleFavorite(id);
                  }
                }}
              >
                <Star
                  className={`h-4 w-4 ${isHighlighted ? "fill-yellow-400 text-yellow-400" : ""}`}
                />
              </span>
            </TooltipTrigger>
            <TooltipContent>
              <p>{t("landing.projectCard.highlight")}</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      )}

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
              {t("landing.projectCard.restore")}
            </DropdownMenuItem>
          ) : (
            <DropdownMenuItem
              onClick={(e) => {
                e.stopPropagation();
                onDelete?.(id);
              }}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              {t("landing.projectCard.delete")}
            </DropdownMenuItem>
          )}
        </DropdownMenuContent>
      </DropdownMenu>
    </button>
  );
}
