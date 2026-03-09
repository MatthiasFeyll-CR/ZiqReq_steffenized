import { useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { IdeaCardCompact } from "@/components/landing/IdeaCardCompact";
import { useIdeasByState } from "@/hooks/use-ideas-by-state";
import type { IdeaState } from "@/components/landing/IdeaCard";

interface Tab {
  value: string;
  labelKey: string;
  state: string;
}

const TABS: Tab[] = [
  { value: "active", labelKey: "ideasFloat.tabs.active", state: "open" },
  { value: "in_review", labelKey: "ideasFloat.tabs.inReview", state: "in_review" },
  { value: "accepted", labelKey: "ideasFloat.tabs.accepted", state: "accepted" },
  { value: "closed", labelKey: "ideasFloat.tabs.closed", state: "dropped" },
];

interface IdeasListFloatingProps {
  onClose: () => void;
}

export function IdeasListFloating({ onClose }: IdeasListFloatingProps) {
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
      aria-label={t("ideasFloat.title")}
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
  const { data, isLoading } = useIdeasByState(state);
  const ideas = data?.results ?? [];

  if (isLoading) {
    return (
      <div className="px-3 py-4 text-center text-sm text-text-secondary">
        {t("common.loading")}
      </div>
    );
  }

  if (ideas.length === 0) {
    return (
      <div className="px-3 py-4 text-center text-sm text-text-secondary">
        {t("ideasFloat.empty", { state: t(`ideasFloat.stateLabels.${state}`) })}
      </div>
    );
  }

  return (
    <div className="max-h-64 overflow-y-auto py-1">
      {ideas.map((idea) => (
        <IdeaCardCompact
          key={idea.id}
          id={idea.id}
          title={idea.title}
          state={idea.state as IdeaState}
          onClick={onItemClick}
        />
      ))}
    </div>
  );
}
