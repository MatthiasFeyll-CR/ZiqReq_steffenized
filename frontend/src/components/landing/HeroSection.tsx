import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { NewProjectModal } from "./NewProjectModal";

export function HeroSection() {
  const { t } = useTranslation();
  const [newProjectModalOpen, setNewProjectModalOpen] = useState(false);

  return (
    <section className="flex flex-col items-center gap-4 py-16 text-center">
      <h1 className="text-3xl font-bold text-foreground">
        {t("landing.hero.heading")}
      </h1>
      <p className="max-w-md text-text-secondary">
        {t("landing.hero.subtext")}
      </p>
      <Button
        variant="primary"
        size="lg"
        onClick={() => setNewProjectModalOpen(true)}
        data-testid="new-project-button"
      >
        {t("landing.hero.newProject", "New Project")}
      </Button>
      <NewProjectModal
        open={newProjectModalOpen}
        onOpenChange={setNewProjectModalOpen}
      />
    </section>
  );
}
