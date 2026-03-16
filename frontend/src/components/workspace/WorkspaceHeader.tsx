import { useCallback, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { ArrowLeft, GitMerge, MoreVertical, Trash2, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { patchIdea, fetchIdea, deleteIdea, type Idea } from "@/api/ideas";
import { CollaboratorModal } from "@/components/collaboration/CollaboratorModal";
import { ManualMergeModal } from "./ManualMergeModal";
import { PresenceIndicators } from "./PresenceIndicators";
import { ProcessStepper, type ProcessStep } from "./ProcessStepper";

const STATE_LABELS: Record<string, string> = {
  open: "Open",
  in_review: "In Review",
  accepted: "Accepted",
  dropped: "Dropped",
  rejected: "Rejected",
};

interface WorkspaceHeaderProps {
  idea: Idea;
  onIdeaUpdate: (idea: Idea) => void;
  readOnly?: boolean;
  activeStep: ProcessStep;
  onStepChange: (step: ProcessStep) => void;
  canAccessDocument: boolean;
  canAccessReview: boolean;
  documentGateMessage?: string;
  reviewGateMessage?: string;
}

export function WorkspaceHeader({
  idea,
  onIdeaUpdate,
  readOnly = false,
  activeStep,
  onStepChange,
  canAccessDocument,
  canAccessReview,
  documentGateMessage,
  reviewGateMessage,
}: WorkspaceHeaderProps) {
  const navigate = useNavigate();
  const { t } = useTranslation();

  const prefersReducedMotion = useReducedMotion();
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(idea.title);
  const [collaboratorModalOpen, setCollaboratorModalOpen] = useState(false);
  const [mergeModalOpen, setMergeModalOpen] = useState(false);
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

  const handleDelete = useCallback(async () => {
    try {
      await deleteIdea(idea.id);
      navigate("/");
    } catch {
      // Error handled silently — user stays on page
    }
  }, [idea.id, navigate]);

  return (
    <div
      className="shrink-0 border-b border-border bg-surface"
      data-testid="workspace-header"
    >
      {/* Top row: back, title, state badge, actions */}
      <div className="h-14 flex items-center gap-3 px-4">
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
            aria-label={t("workspace.editTitle", "Edit idea title")}
            data-testid="title-input"
          />
        ) : (
          <button
            className="min-w-0 text-left text-lg font-semibold text-foreground truncate hover:text-primary cursor-text"
            onClick={handleTitleClick}
            data-testid="title-display"
          >
            <AnimatePresence>
              <motion.span
                key={idea.title}
                initial={prefersReducedMotion ? false : { opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={prefersReducedMotion ? { opacity: 0 } : { opacity: 0, y: 4 }}
                transition={{ duration: prefersReducedMotion ? 0 : 0.25 }}
                data-testid="title-animated"
              >
                {idea.title || t("landing.untitled", "Untitled")}
              </motion.span>
            </AnimatePresence>
          </button>
        )}

        {/* State badge */}
        <Badge
          variant={idea.state as "open" | "in_review" | "accepted" | "dropped" | "rejected"}
          className="shrink-0"
        >
          {STATE_LABELS[idea.state] || idea.state}
        </Badge>

        <div className="flex-1" />

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

        {/* Request merge */}
        {!readOnly && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => setMergeModalOpen(true)}
            data-testid="request-merge-button"
          >
            <GitMerge className="mr-1 h-4 w-4" />
            {t("workspace.requestMerge", "Merge")}
          </Button>
        )}

        {/* Presence indicators */}
        <PresenceIndicators ideaId={idea.id} />

        {/* Options dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon-sm"
              aria-label={t("workspace.options", "Options")}
              data-testid="options-menu-trigger"
            >
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem
              className="text-destructive focus:text-destructive"
              onClick={handleDelete}
              data-testid="delete-idea-option"
            >
              <Trash2 className="mr-2 h-4 w-4" />
              {t("workspace.deleteIdea", "Delete Idea")}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Bottom row: process stepper */}
      <div className="h-10 flex items-center px-4 border-t border-border/50">
        <ProcessStepper
          activeStep={activeStep}
          onStepChange={onStepChange}
          canAccessDocument={canAccessDocument}
          canAccessReview={canAccessReview}
          documentGateMessage={documentGateMessage}
          reviewGateMessage={reviewGateMessage}
        />
      </div>

      <CollaboratorModal
        ideaId={idea.id}
        ownerId={idea.owner_id}
        coOwnerId={idea.co_owner_id}
        open={collaboratorModalOpen}
        onOpenChange={setCollaboratorModalOpen}
      />

      <ManualMergeModal
        ideaId={idea.id}
        open={mergeModalOpen}
        onOpenChange={setMergeModalOpen}
        onSuccess={() => {
          fetchIdea(idea.id).then((updated) => {
            onIdeaUpdate(updated);
          }).catch(() => {});
        }}
      />
    </div>
  );
}
