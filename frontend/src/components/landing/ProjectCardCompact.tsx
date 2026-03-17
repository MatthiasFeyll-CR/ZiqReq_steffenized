import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import type { ProjectState } from "./ProjectCard";

const STATE_DOT_COLORS: Record<ProjectState, string> = {
  open: "#0284C7",
  in_review: "#F59E0B",
  accepted: "#16A34A",
  dropped: "#9CA3AF",
  rejected: "#F97316",
};

export interface ProjectCardCompactProps {
  id: string;
  title: string;
  state: ProjectState;
  onClick?: () => void;
}

export function ProjectCardCompact({
  id,
  title,
  state,
  onClick,
}: ProjectCardCompactProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();

  return (
    <button
      type="button"
      className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-left transition-colors hover:bg-muted"
      onClick={() => {
        navigate(`/project/${id}`);
        onClick?.();
      }}
    >
      <span
        className="shrink-0 rounded-full"
        style={{
          width: 8,
          height: 8,
          backgroundColor: STATE_DOT_COLORS[state],
        }}
      />
      <span className="truncate text-sm font-medium text-foreground">
        {title || t("landing.untitled")}
      </span>
    </button>
  );
}
