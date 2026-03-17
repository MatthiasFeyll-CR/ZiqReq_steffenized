import { useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { ProjectCardCompact } from "@/components/landing/ProjectCardCompact";
import { useProjectsByState } from "@/hooks/use-projects-by-state";
import type { ProjectState } from "@/components/landing/ProjectCard";

interface Tab {
  value: string;
  labelKey: string;
  state: string;
}

const TABS: Tab[] = [
  { value: "active", labelKey: "projectsFloat.tabs.active", state: "open" },
  { value: "in_review", labelKey: "projectsFloat.tabs.inReview", state: "in_review" },
  { value: "accepted", labelKey: "projectsFloat.tabs.accepted", state: "accepted" },
  { value: "closed", labelKey: "projectsFloat.tabs.closed", state: "dropped" },
];

interface ProjectsListFloatingProps {
  onClose: () => void;
}

export function ProjectsListFloating({ onClose }: ProjectsListFloatingProps) {
  const { t } = useTranslation();
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    function handleClickOutside(e: MouseEvent) {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
        onClose();
      }
    }
    document.addEventListener("keydown", handleKeyDown);
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [onClose]);

  return (
    <div
      ref={panelRef}
      className="absolute right-0 top-full z-20 mt-1 w-80 rounded-lg border border-border bg-surface shadow-lg"
      role="dialog"
      aria-label={t("projectsFloat.title")}
    >
      <Tabs defaultValue="active" className="w-full">
        <TabsList className="w-full">
          {TABS.map((tab) => (
            <TabsTrigger key={tab.value} value={tab.value} className="flex-1 text-xs">
              {t(tab.labelKey)}
            </TabsTrigger>
          ))}
        </TabsList>

        {TABS.map((tab) => (
          <TabsContent key={tab.value} value={tab.value}>
            <TabPanel state={tab.state} onItemClick={onClose} />
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}

function TabPanel({ state, onItemClick }: { state: string; onItemClick: () => void }) {
  const { t } = useTranslation();
  const { data, isLoading } = useProjectsByState(state);
  const projects = data?.results ?? [];

  if (isLoading) {
    return (
      <div className="px-3 py-4 text-center text-sm text-text-secondary">
        {t("common.loading")}
      </div>
    );
  }

  if (projects.length === 0) {
    return (
      <div className="px-3 py-4 text-center text-sm text-text-secondary">
        {t("projectsFloat.empty", { state: t(`projectsFloat.stateLabels.${state}`) })}
      </div>
    );
  }

  return (
    <div className="max-h-64 overflow-y-auto py-1">
      {projects.map((project) => (
        <ProjectCardCompact
          key={project.id}
          id={project.id}
          title={project.title}
          state={project.state as ProjectState}
          onClick={onItemClick}
        />
      ))}
    </div>
  );
}
