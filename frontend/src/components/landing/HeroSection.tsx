import { useTranslation } from "react-i18next";
import { Code, Package, Loader2 } from "lucide-react";
import { useCreateProject } from "@/hooks/use-create-project";
import { cn } from "@/lib/utils";
import type { ProjectType } from "@/api/projects";

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

export function HeroSection() {
  const { t } = useTranslation();
  const mutation = useCreateProject();

  const handleSelect = (type: ProjectType) => {
    if (mutation.isPending) return;
    mutation.mutate(type);
  };

  return (
    <section className="flex flex-col items-center gap-6 py-16 text-center">
      <h1 className="text-3xl font-bold text-foreground">
        {t("landing.hero.heading")}
      </h1>
      <p className="max-w-md text-text-secondary">
        {t("landing.hero.subtext")}
      </p>

      <div className="grid w-full max-w-lg grid-cols-2 gap-4">
        {TYPE_OPTIONS.map((option) => {
          const Icon = option.icon;
          const isLoading =
            mutation.isPending &&
            mutation.variables === option.value;
          return (
            <button
              key={option.value}
              type="button"
              data-testid={`new-project-${option.value}`}
              disabled={mutation.isPending}
              onClick={() => handleSelect(option.value)}
              className={cn(
                "group flex flex-col items-center gap-3 rounded-xl border-2 border-border bg-surface p-6 text-center transition-all",
                "hover:border-primary hover:bg-primary/5 hover:shadow-md",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2",
                "disabled:pointer-events-none disabled:opacity-60",
                isLoading && "border-primary bg-primary/5",
              )}
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 transition-colors group-hover:bg-primary/20">
                {isLoading ? (
                  <Loader2 className="h-6 w-6 animate-spin text-primary" />
                ) : (
                  <Icon className="h-6 w-6 text-primary" />
                )}
              </div>
              <div>
                <div className="text-base font-semibold text-foreground">
                  {t(option.titleKey, option.titleFallback)}
                </div>
                <div className="mt-1 text-sm text-muted-foreground">
                  {t(option.subtitleKey, option.subtitleFallback)}
                </div>
              </div>
            </button>
          );
        })}
      </div>

    </section>
  );
}
