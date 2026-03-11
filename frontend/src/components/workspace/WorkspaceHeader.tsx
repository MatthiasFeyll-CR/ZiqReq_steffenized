import { useCallback, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { AnimatePresence, motion } from "framer-motion";
import { ArrowLeft, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { patchIdea, type Idea } from "@/api/ideas";
import { CollaboratorModal } from "@/components/collaboration/CollaboratorModal";
import { PresenceIndicators } from "./PresenceIndicators";

interface WorkspaceHeaderProps {
  idea: Idea;
  onIdeaUpdate: (idea: Idea) => void;
  readOnly?: boolean;
}

export function WorkspaceHeader({ idea, onIdeaUpdate, readOnly = false }: WorkspaceHeaderProps) {
  const navigate = useNavigate();
  const { t } = useTranslation();

  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(idea.title);
  const [collaboratorModalOpen, setCollaboratorModalOpen] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleTitleClick = useCallback(() => {
    if (readOnly) return;
    setEditValue(idea.title);
    setIsEditing(true);
    setTimeout(() => inputRef.current?.select(), 0);
  }, [idea.title, readOnly]);

  const handleTitleSave = useCallback(async () => {
    const trimmed = editValue.trim();
    setIsEditing(false);
    if (!trimmed || trimmed === idea.title) return;

    // Optimistic update
    const previousTitle = idea.title;
    onIdeaUpdate({ ...idea, title: trimmed });

    try {
      const updated = await patchIdea(idea.id, { title: trimmed });
      onIdeaUpdate(updated);
    } catch {
      onIdeaUpdate({ ...idea, title: previousTitle });
    }
  }, [editValue, idea, onIdeaUpdate]);

  const handleTitleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter") {
        e.preventDefault();
        handleTitleSave();
      } else if (e.key === "Escape") {
        setIsEditing(false);
        setEditValue(idea.title);
      }
    },
    [handleTitleSave, idea.title],
  );

  const handleAgentModeChange = useCallback(
    async (value: string) => {
      const mode = value as "interactive" | "silent";
      const previousMode = idea.agent_mode;

      // Optimistic update
      onIdeaUpdate({ ...idea, agent_mode: mode });

      try {
        const updated = await patchIdea(idea.id, { agent_mode: mode });
        onIdeaUpdate(updated);
      } catch {
        onIdeaUpdate({ ...idea, agent_mode: previousMode });
      }
    },
    [idea, onIdeaUpdate],
  );

  return (
    <div
      className="h-16 border-b flex items-center gap-4 px-4"
      data-testid="workspace-header"
    >
      {/* Back button */}
      <Button
        variant="ghost"
        size="icon-sm"
        onClick={() => navigate("/")}
        aria-label={t("workspace.back", "Back")}
        data-testid="back-button"
      >
        <ArrowLeft className="h-5 w-5" />
      </Button>

      {/* Editable title */}
      {isEditing ? (
        <input
          ref={inputRef}
          className="flex-1 min-w-0 text-lg font-semibold bg-transparent border-b border-primary outline-none text-foreground"
          value={editValue}
          onChange={(e) => setEditValue(e.target.value)}
          onBlur={handleTitleSave}
          onKeyDown={handleTitleKeyDown}
          data-testid="title-input"
        />
      ) : (
        <button
          className="flex-1 min-w-0 text-left text-lg font-semibold text-foreground truncate hover:text-primary cursor-text"
          onClick={handleTitleClick}
          data-testid="title-display"
        >
          <AnimatePresence>
            <motion.span
              key={idea.title}
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 4 }}
              transition={{ duration: 0.25 }}
              data-testid="title-animated"
            >
              {idea.title || t("landing.untitled", "Untitled")}
            </motion.span>
          </AnimatePresence>
        </button>
      )}

      {/* Agent mode dropdown */}
      <Select value={idea.agent_mode} onValueChange={handleAgentModeChange} disabled={readOnly}>
        <SelectTrigger
          className="w-40 shrink-0"
          data-testid="agent-mode-trigger"
        >
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="interactive" data-testid="mode-interactive">
            {t("workspace.modeInteractive", "Interactive")}
          </SelectItem>
          <SelectItem value="silent" data-testid="mode-silent">
            {t("workspace.modeSilent", "Silent")}
          </SelectItem>
        </SelectContent>
      </Select>

      {/* Manage collaborators */}
      {!readOnly && (
        <Button
          variant="outline"
          size="sm"
          onClick={() => setCollaboratorModalOpen(true)}
          data-testid="manage-collaborators-button"
        >
          <Users className="mr-1 h-4 w-4" />
          {t("workspace.manage", "Manage")}
        </Button>
      )}

      {/* Presence indicators */}
      <PresenceIndicators ideaId={idea.id} />

      <CollaboratorModal
        ideaId={idea.id}
        ownerId={idea.owner_id}
        coOwnerId={idea.co_owner_id}
        open={collaboratorModalOpen}
        onOpenChange={setCollaboratorModalOpen}
      />
    </div>
  );
}
