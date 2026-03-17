import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Code, Package } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { useCreateProject } from "@/hooks/use-create-project";
import { cn } from "@/lib/utils";
import type { ProjectType } from "@/api/projects";

interface NewProjectModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const TYPE_OPTIONS: Array<{
  value: ProjectType;
  icon: typeof Code;
  titleKey: string;
  titleFallback: string;
  subtitleKey: string;
  subtitleFallback: string;
}> = [
  {
    value: "software",
    icon: Code,
    titleKey: "landing.newProject.software",
    titleFallback: "Software Project",
    subtitleKey: "landing.newProject.softwareSubtitle",
    subtitleFallback: "Epics & User Stories",
  },
  {
    value: "non_software",
    icon: Package,
    titleKey: "landing.newProject.nonSoftware",
    titleFallback: "Non-Software Project",
    subtitleKey: "landing.newProject.nonSoftwareSubtitle",
    subtitleFallback: "Milestones & Work Packages",
  },
];

export function NewProjectModal({ open, onOpenChange }: NewProjectModalProps) {
  const { t } = useTranslation();
  const [selectedType, setSelectedType] = useState<ProjectType | null>(null);
  const mutation = useCreateProject();

  const handleCreate = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!selectedType) return;
    mutation.mutate(selectedType, {
      onSuccess: () => onOpenChange(false),
    });
  };

  const handleOpenChange = (nextOpen: boolean) => {
    if (!nextOpen) {
      setSelectedType(null);
      mutation.reset();
    }
    onOpenChange(nextOpen);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-w-md" data-testid="new-project-modal">
        <form onSubmit={handleCreate}>
          <DialogHeader>
            <DialogTitle>
              {t("landing.newProject.title", "Create New Project")}
            </DialogTitle>
            <DialogDescription>
              {t(
                "landing.newProject.description",
                "Choose the type of project you want to create.",
              )}
            </DialogDescription>
          </DialogHeader>

          <div className="flex flex-col gap-3 py-4">
            {TYPE_OPTIONS.map((option) => {
              const Icon = option.icon;
              const isSelected = selectedType === option.value;
              return (
                <button
                  key={option.value}
                  type="button"
                  data-testid={`project-type-${option.value}`}
                  onClick={() => setSelectedType(option.value)}
                  className={cn(
                    "flex items-center gap-4 rounded-md border p-4 text-left cursor-pointer transition-colors hover:bg-muted/50",
                    isSelected
                      ? "border-primary border-2 bg-primary/5"
                      : "border-border",
                  )}
                >
                  <Icon className="h-5 w-5 shrink-0 text-primary" />
                  <div>
                    <div className="text-base font-medium text-foreground">
                      {t(option.titleKey, option.titleFallback)}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {t(option.subtitleKey, option.subtitleFallback)}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="ghost"
              onClick={() => handleOpenChange(false)}
            >
              {t("common.cancel", "Cancel")}
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={!selectedType || mutation.isPending}
              data-testid="create-project-button"
            >
              {mutation.isPending
                ? t("common.loading", "Loading...")
                : t("landing.newProject.create", "Create")}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
