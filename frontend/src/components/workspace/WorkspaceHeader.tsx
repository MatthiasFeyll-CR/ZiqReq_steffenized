import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { ArrowLeft, MessageCircle, MoreVertical, Trash2, Users } from "lucide-react";
import { fetchUnreadCommentCount } from "@/api/comments";
import { CommentsPanel } from "@/components/comments/CommentsPanel";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { patchProject, deleteProject, type Project } from "@/api/projects";
import { CollaboratorModal } from "@/components/collaboration/CollaboratorModal";
import { PresenceIndicators } from "./PresenceIndicators";
import { ProcessStepper, type ProcessStep } from "./ProcessStepper";

const STATE_LABELS: Record<string, string> = {
  open: "Open",
  in_review: "In Review",
  accepted: "Accepted",
  dropped: "Dropped",
  rejected: "Rejected",
  deleted: "Deleted",
};

interface WorkspaceHeaderProps {
  project: Project;
  onProjectUpdate: (project: Project) => void;
  readOnly?: boolean;
  activeStep: ProcessStep;
  onStepChange: (step: ProcessStep) => void;
  canAccessStructure: boolean;
  canAccessReview: boolean;
  structureGateMessage?: string;
  reviewGateMessage?: string;
  shareToken?: string | null;
}

export function WorkspaceHeader({
  project,
  onProjectUpdate,
  readOnly = false,
  activeStep,
  onStepChange,
  canAccessStructure,
  canAccessReview,
  structureGateMessage,
  reviewGateMessage,
  shareToken,
}: WorkspaceHeaderProps) {
  const navigate = useNavigate();
  const { t } = useTranslation();

  const { user } = useAuth();
  const prefersReducedMotion = useReducedMotion();
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(project.title);
  const [collaboratorModalOpen, setCollaboratorModalOpen] = useState(false);
  const [commentsPanelOpen, setCommentsPanelOpen] = useState(false);
  const [unreadComments, setUnreadComments] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  // Fetch unread comment count
  useEffect(() => {
    fetchUnreadCommentCount(project.id, shareToken).then(setUnreadComments).catch(() => {});
  }, [project.id, shareToken]);

  // Listen for new comments via WebSocket to update badge
  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail.project_id === project.id && !detail.is_system_event) {
        if (!commentsPanelOpen && detail.author?.id !== user?.id) {
          setUnreadComments((prev) => prev + 1);
        }
      }
    };
    window.addEventListener("ws:comment_created", handler);
    return () => window.removeEventListener("ws:comment_created", handler);
  }, [project.id, commentsPanelOpen, user?.id]);

  // Reset unread when panel opens
  useEffect(() => {
    if (commentsPanelOpen) {
      setUnreadComments(0);
    }
  }, [commentsPanelOpen]);

  const handleTitleClick = useCallback(() => {
    if (readOnly) return;
    setEditValue(project.title);
    setIsEditing(true);
    setTimeout(() => inputRef.current?.select(), 0);
  }, [project.title, readOnly]);

  const handleTitleSave = useCallback(async () => {
    const trimmed = editValue.trim();
    setIsEditing(false);
    if (!trimmed || trimmed === project.title) return;

    const previousTitle = project.title;
    onProjectUpdate({ ...project, title: trimmed });

    try {
      const updated = await patchProject(project.id, { title: trimmed });
      onProjectUpdate(updated);
    } catch {
      onProjectUpdate({ ...project, title: previousTitle });
    }
  }, [editValue, project, onProjectUpdate]);

  const handleTitleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter") {
        e.preventDefault();
        handleTitleSave();
      } else if (e.key === "Escape") {
        setIsEditing(false);
        setEditValue(project.title);
      }
    },
    [handleTitleSave, project.title],
  );

  const handleDelete = useCallback(async () => {
    try {
      await deleteProject(project.id);
      onProjectUpdate({ ...project, state: "deleted" });
    } catch {
      // Error handled silently — user stays on page
    }
  }, [project, onProjectUpdate]);

  return (
    <div
      className="shrink-0 border-b border-border bg-surface"
      data-testid="workspace-header"
    >
      {/* Top row: back, title, state badge, actions */}
      <div className="h-14 flex items-center gap-3 px-6">
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
            aria-label={t("workspace.editTitle", "Edit project title")}
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
                key={project.title}
                initial={prefersReducedMotion ? false : { opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={prefersReducedMotion ? { opacity: 0 } : { opacity: 0, y: 4 }}
                transition={{ duration: prefersReducedMotion ? 0 : 0.25 }}
                data-testid="title-animated"
              >
                {project.title || t("landing.untitled", "Untitled")}
              </motion.span>
            </AnimatePresence>
          </button>
        )}

        {/* State badge */}
        <Badge
          variant={project.state as "open" | "in_review" | "accepted" | "dropped" | "rejected" | "deleted"}
          className="shrink-0"
        >
          {STATE_LABELS[project.state] || project.state}
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

        {/* Comments button */}
        <Button
          variant="outline"
          size="sm"
          onClick={() => setCommentsPanelOpen(true)}
          className="relative"
          data-testid="comments-button"
        >
          <MessageCircle className="mr-1 h-4 w-4" />
          {t("workspace.comments", "Comments")}
          {unreadComments > 0 && (
            <span className="absolute -top-1.5 -right-1.5 flex h-5 min-w-5 items-center justify-center rounded-full bg-destructive text-[10px] font-bold text-white px-1">
              {unreadComments > 99 ? "99+" : unreadComments}
            </span>
          )}
        </Button>

        {/* Presence indicators */}
        <PresenceIndicators projectId={project.id} />

        {/* Options dropdown — hidden when deleted */}
        {project.state !== "deleted" && (
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
                data-testid="delete-project-option"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                {t("workspace.deleteProject", "Delete Project")}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>

      {/* Bottom row: process stepper */}
      <div className="flex items-center px-4 py-1.5 border-t border-border/50">
        <ProcessStepper
          activeStep={activeStep}
          onStepChange={onStepChange}
          canAccessStructure={canAccessStructure}
          canAccessReview={canAccessReview}
          structureGateMessage={structureGateMessage}
          reviewGateMessage={reviewGateMessage}
        />
      </div>

      <CollaboratorModal
        projectId={project.id}
        ownerId={project.owner_id}
        open={collaboratorModalOpen}
        onOpenChange={setCollaboratorModalOpen}
      />

      <CommentsPanel
        projectId={project.id}
        open={commentsPanelOpen}
        onOpenChange={setCommentsPanelOpen}
        disabled={project.state === "deleted"}
        currentUserId={user?.id}
        isOwnerOrCollaborator={!readOnly}
        shareToken={shareToken}
      />
    </div>
  );
}
