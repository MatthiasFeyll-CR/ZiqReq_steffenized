import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { fetchProject, restoreProject, type Project, type ProjectType } from "@/api/projects";
import { fetchChatMessages } from "@/api/chat";
import { LazyProjectProvider } from "@/hooks/use-lazy-project";
import { useAuth } from "@/hooks/use-auth";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertTriangle, ArrowRight, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { WorkspaceLayout } from "@/components/workspace/WorkspaceLayout";
import { RequirementsPanel } from "@/components/workspace/RequirementsPanel";
import { WorkspaceHeader } from "@/components/workspace/WorkspaceHeader";
import { ChatPanel } from "@/components/workspace/ChatPanel";
import { StructureStepView } from "./StructureStepView";
import { OfflineBanner } from "@/components/common/OfflineBanner";
import { InvitationBanner } from "@/components/workspace/InvitationBanner";
import { ReadOnlyBanner } from "@/components/workspace/ReadOnlyBanner";
import { ReviewSection } from "@/components/review/ReviewSection";
import { useSectionVisibility } from "@/components/workspace/useSectionVisibility";
import { useProjectSync } from "@/hooks/useProjectSync";
import { useInvitations } from "@/hooks/use-invitations";
import { useSelector } from "react-redux";
import { selectIsOnline, selectConnectionState } from "@/store/websocket-slice";
import { useWsSend } from "@/app/providers";
import type { ProcessStep } from "@/components/workspace/ProcessStepper";

const VALID_STEPS: ProcessStep[] = ["define", "structure", "review"];

function parseStep(value: string | null): ProcessStep {
  if (value && VALID_STEPS.includes(value as ProcessStep)) {
    return value as ProcessStep;
  }
  return "define";
}

export default function ProjectWorkspacePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const shareToken = searchParams.get("token");

  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<{ message: string; status?: number } | null>(null);

  const isNewDraft = id === "new";
  const draftType = (searchParams.get("type") as ProjectType) || "software";

  useEffect(() => {
    if (!id || isNewDraft) return;

    let cancelled = false;
    setLoading(true);
    setError(null);

    (shareToken ? fetchProject(id, shareToken) : fetchProject(id))
      .then((data) => {
        if (!cancelled) {
          setProject(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError({
            message: err.message ?? t("common.error"),
            status: (err as Error & { status?: number }).status,
          });
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [id, isNewDraft, shareToken, t]);

  // For new drafts, create a synthetic project immediately (no API call)
  useEffect(() => {
    if (!isNewDraft) return;
    setProject({
      id: "new",
      title: "",
      project_type: draftType,
      state: "open",
      visibility: "private",
      owner: { id: user?.id ?? "", display_name: user?.display_name ?? "" },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      collaborators: [],
    });
    setLoading(false);
  }, [isNewDraft, draftType, user]);

  const handleProjectUpdate = useCallback((updated: Project) => {
    setProject(updated);
  }, []);

  useEffect(() => {
    if (project?.title) {
      document.title = project.title;
    }
    return () => {
      document.title = "ZiqReq";
    };
  }, [project?.title]);

  if (loading) {
    return (
      <div className="flex flex-col h-full" data-testid="workspace-loading">
        <div className="h-14 border-b flex items-center gap-4 px-4">
          <Skeleton className="h-8 w-8 rounded" />
          <Skeleton className="h-6 w-64" />
          <div className="flex-1" />
          <Skeleton className="h-8 w-32" />
        </div>
        <div className="border-b flex items-center px-4 py-2 gap-3">
          <div className="flex items-center gap-2">
            <Skeleton className="h-8 w-8 rounded-full" />
            <div className="space-y-1 hidden sm:block">
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-3 w-32" />
            </div>
          </div>
          <Skeleton className="h-0.5 w-8" />
          <div className="flex items-center gap-2">
            <Skeleton className="h-8 w-8 rounded-full" />
            <div className="space-y-1 hidden sm:block">
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-3 w-28" />
            </div>
          </div>
          <Skeleton className="h-0.5 w-8" />
          <div className="flex items-center gap-2">
            <Skeleton className="h-8 w-8 rounded-full" />
            <div className="space-y-1 hidden sm:block">
              <Skeleton className="h-4 w-16" />
              <Skeleton className="h-3 w-24" />
            </div>
          </div>
        </div>
        <div className="flex flex-1">
          <div className="w-2/5 p-4 space-y-4">
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-3/4" />
            <Skeleton className="h-16 w-full" />
          </div>
          <div className="w-3/5 p-4 space-y-4">
            <Skeleton className="h-10 w-48" />
            <Skeleton className="h-64 w-full" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    const is404 = error.status === 404;
    const is403 = error.status === 403;

    return (
      <div
        className="flex flex-col items-center justify-center h-full gap-4 py-12"
        data-testid="workspace-error"
      >
        <AlertTriangle className="h-12 w-12 text-destructive" />
        <h2 className="text-lg font-semibold text-foreground">
          {is404
            ? t("workspace.notFound", "Project not found")
            : is403
              ? t("workspace.noAccess", "You don't have access to this project")
              : t("common.error")}
        </h2>
        <p className="text-sm text-muted-foreground">{error.message}</p>
        <Button variant="outline" onClick={() => navigate("/")}>
          {t("workspace.backToHome", "Back to home")}
        </Button>
      </div>
    );
  }

  if (!project) return null;

  return (
    <LazyProjectProvider
      projectId={project.id}
      projectType={project.project_type}
      onCreated={handleProjectUpdate}
    >
      <ProjectWorkspaceContent project={project} onProjectUpdate={handleProjectUpdate} readOnly={!!shareToken || !!project.read_only} shareToken={shareToken} />
    </LazyProjectProvider>
  );
}

function ProjectWorkspaceContent({
  project,
  onProjectUpdate,
  readOnly: readOnlyProp = false,
  shareToken,
}: {
  project: Project;
  onProjectUpdate: (project: Project) => void;
  readOnly?: boolean;
  shareToken?: string | null;
}) {
  const { t } = useTranslation();
  const [searchParams, setSearchParams] = useSearchParams();
  const { chatLocked, allReadOnly, lockReason } = useSectionVisibility(project);
  const isOnline = useSelector(selectIsOnline);
  const connectionState = useSelector(selectConnectionState);
  const sendWs = useWsSend();
  const { user } = useAuth();

  // Invitation-aware read-only: starts as prop value, can be lifted on accept
  const [inviteReadOnlyOverride, setInviteReadOnlyOverride] = useState(false);
  const readOnly = readOnlyProp && !inviteReadOnlyOverride;

  // Check if there's a pending invitation for this project
  const { data: invitationData } = useInvitations();
  const hasPendingInvite = !!user && !!invitationData?.invitations?.find(
    (inv) => inv.project_id === project.id,
  );

  const handleInviteAccepted = useCallback(() => {
    setInviteReadOnlyOverride(true);
    // Refetch project to get updated access
    fetchProject(project.id).then((updated) => {
      onProjectUpdate(updated);
    }).catch(() => {});
  }, [project.id, onProjectUpdate]);

  // Step management via URL — default step depends on project state
  const [activeStep, setActiveStep] = useState<ProcessStep>(() => {
    const urlStep = parseStep(searchParams.get("step"));
    // If no explicit step in URL, derive from project state
    if (!searchParams.get("step")) {
      if (project.state === "rejected" || project.state === "deleted") return "define";
      if (["in_review", "accepted", "dropped"].includes(project.state)) return "review";
    }
    return urlStep;
  });

  // Track which steps have been explicitly completed (via CTA buttons, not manual tab clicks)
  const [completedSteps, setCompletedSteps] = useState<Set<ProcessStep>>(() => {
    // If project was already submitted, both define and structure are completed
    if (["in_review", "accepted", "dropped"].includes(project.state)) {
      return new Set<ProcessStep>(["define", "structure"]);
    }
    return new Set<ProcessStep>();
  });

  const isDraft = project.id === "new";

  // Track whether the project has at least one chat message
  const [hasMessages, setHasMessages] = useState<boolean | null>(null);

  useEffect(() => {
    if (isDraft) { setHasMessages(false); return; }
    let cancelled = false;
    fetchChatMessages(project.id, { limit: 1 }).then((data) => {
      if (!cancelled) {
        setHasMessages(data.total > 0);
      }
    }).catch(() => {
      if (!cancelled) setHasMessages(false);
    });
    return () => { cancelled = true; };
  }, [project.id, isDraft]);

  // Listen for new chat messages to update hasMessages
  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail.project_id === project.id) {
        setHasMessages(true);
      }
    };
    window.addEventListener("ws:chat_message", handler);
    return () => window.removeEventListener("ws:chat_message", handler);
  }, [project.id]);

  const handleStepChange = useCallback(
    (step: ProcessStep) => {
      setActiveStep(step);
      setSearchParams((prev) => {
        const next = new URLSearchParams(prev);
        if (step === "define") {
          next.delete("step");
        } else {
          next.set("step", step);
        }
        return next;
      }, { replace: true });
    },
    [setSearchParams],
  );

  // has_been_submitted heuristic — deleted doesn't count
  const hasBeenSubmitted = project.state !== "open" && project.state !== "deleted";

  // Access gates
  const canAccessStructure = hasMessages === true;
  const canAccessReview = hasBeenSubmitted;

  const structureGateMessage = t(
    "process.structureGate",
    "Send at least one message in the chat before proceeding to structure.",
  );
  const reviewGateMessage = t(
    "process.reviewGate",
    "Submit your project for review first.",
  );

  // Auto-navigate on state transitions
  const prevStateRef = useRef(project.state);
  useEffect(() => {
    if (prevStateRef.current === project.state) return;
    prevStateRef.current = project.state;

    if (project.state === "rejected" || project.state === "deleted") {
      handleStepChange("define");
    } else if (["in_review", "accepted", "dropped"].includes(project.state)) {
      setCompletedSteps((prev) => new Set(prev).add("define").add("structure"));
      handleStepChange("review");
    }
  }, [project.state, handleStepChange]);

  // If landed on a gated step, redirect to define
  useEffect(() => {
    if (activeStep === "structure" && !canAccessStructure) {
      handleStepChange("define");
    } else if (activeStep === "review" && !canAccessReview) {
      // Redirect to structure if they can access it, otherwise define
      handleStepChange(canAccessStructure ? "structure" : "define");
    }
  }, [activeStep, canAccessStructure, canAccessReview, handleStepChange]);

  // Subscribe to project's WebSocket group when connected (skip for drafts)
  useEffect(() => {
    if (isDraft) return;
    if (connectionState === "online") {
      sendWs({ type: "subscribe_project", project_id: project.id });
    }
    return () => {
      if (connectionState === "online") {
        sendWs({ type: "unsubscribe_project", project_id: project.id });
      }
    };
  }, [project.id, isDraft, connectionState, sendWs]);

  // Return-from-idle sync (skip for drafts)
  useProjectSync({ projectId: isDraft ? "" : project.id, onProjectUpdate });
  const projectRef = useRef(project);
  projectRef.current = project;
  const onProjectUpdateRef = useRef(onProjectUpdate);
  onProjectUpdateRef.current = onProjectUpdate;

  const isDeleted = project.state === "deleted";
  const isInReview = project.state === "in_review";
  const isInReviewReadOnly = isInReview && activeStep !== "review";

  // Listen for WebSocket title_update events
  useEffect(() => {
    const handler = (e: Event) => {
      const { project_id, title } = (e as CustomEvent).detail;
      if (project_id === projectRef.current.id) {
        onProjectUpdateRef.current({ ...projectRef.current, title });
      }
    };
    window.addEventListener("ws:title_update", handler);
    return () => window.removeEventListener("ws:title_update", handler);
  }, []);

  const [isRestoring, setIsRestoring] = useState(false);
  const handleRestore = useCallback(async () => {
    setIsRestoring(true);
    try {
      await restoreProject(project.id);
      const updated = await fetchProject(project.id);
      onProjectUpdate(updated);
    } catch {
      // If refetch fails, optimistically set state back to open
      onProjectUpdate({ ...project, state: "open" });
    } finally {
      setIsRestoring(false);
    }
  }, [project, onProjectUpdate]);

  // Structure step is read-only when user navigated there manually (without completing define via CTA)
  const structureNotCompleted = activeStep === "structure" && !completedSteps.has("define");

  const effectiveChatLocked = chatLocked || !isOnline || readOnly || isDeleted || isInReviewReadOnly;
  const effectiveLockReason = readOnly
    ? "Viewing shared project — chat is read-only"
    : !isOnline
      ? "You are currently offline. Chat is disabled."
      : isDeleted
        ? "This project has been deleted. All sections are read-only."
        : isInReviewReadOnly
          ? "This project is currently under review. Content is read-only."
          : lockReason;
  const effectiveReadOnly = allReadOnly || readOnly || isDeleted || isInReviewReadOnly;

  return (
    <div className="flex flex-col h-full overflow-hidden" data-testid="project-workspace">
      <WorkspaceHeader
        project={project}
        onProjectUpdate={onProjectUpdate}
        readOnly={effectiveReadOnly}
        activeStep={activeStep}
        onStepChange={handleStepChange}
        canAccessStructure={canAccessStructure}
        canAccessReview={canAccessReview}
        structureGateMessage={structureGateMessage}
        reviewGateMessage={reviewGateMessage}
        shareToken={shareToken}
        completedSteps={completedSteps}
        isHighlighted={project.is_highlighted}
      />

      {/* Banners */}
      {readOnly && !hasPendingInvite && <ReadOnlyBanner />}
      {!isDeleted && (
        <InvitationBanner
          projectId={project.id}
          onAccepted={handleInviteAccepted}
        />
      )}
      {isDeleted && (
        <div
          className="shrink-0 border-b border-l-4 border-l-red-400 dark:border-l-red-500 bg-red-50 dark:bg-red-950/20 px-6 py-3 flex items-center gap-3"
          data-testid="deleted-banner"
        >
          <AlertTriangle className="h-4 w-4 text-red-600 dark:text-red-400 shrink-0" />
          <p className="text-sm text-red-700 dark:text-red-400">
            {t("workspace.deletedReason", "This project has been deleted. All content is read-only.")}
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRestore}
            disabled={isRestoring}
            data-testid="restore-project-button"
            className="ml-3 shrink-0 border-red-300 text-red-700 hover:bg-red-100 dark:border-red-800 dark:text-red-400 dark:hover:bg-red-950/40"
          >
            {isRestoring ? (
              <RotateCcw className="mr-1 h-4 w-4 animate-spin" />
            ) : (
              <RotateCcw className="mr-1 h-4 w-4" />
            )}
            {t("workspace.restoreProject", "Restore")}
          </Button>
        </div>
      )}
      {isInReviewReadOnly && (
        <div
          className="shrink-0 border-b border-l-4 border-l-amber-400 dark:border-l-amber-500 bg-amber-50 dark:bg-amber-950/20 px-6 py-3 flex items-center gap-3"
          data-testid="in-review-banner"
        >
          <AlertTriangle className="h-4 w-4 text-amber-600 dark:text-amber-400 shrink-0" />
          <p className="text-sm text-amber-700 dark:text-amber-400">
            {t("workspace.inReviewReadOnly", "This project is currently under review. Content is read-only until the review is complete.")}
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleStepChange("review")}
            data-testid="go-to-review-button"
            className="ml-3 shrink-0 border-amber-300 text-amber-700 hover:bg-amber-100 dark:border-amber-800 dark:text-amber-400 dark:hover:bg-amber-950/40"
          >
            {t("workspace.goToReview", "Go to Review")}
          </Button>
        </div>
      )}
      <OfflineBanner />

      {/* Step Content */}
      {activeStep === "define" && (
        <div className="flex-1 min-h-0 flex flex-col">

          <WorkspaceLayout
            chatPanel={
              <ChatPanel project={project} locked={effectiveChatLocked} lockReason={effectiveLockReason} readOnly={readOnly || isInReviewReadOnly} />
            }
            requirementsPanel={
              <RequirementsPanel
                projectId={project.id}
                projectType={project.project_type}
                readOnly={effectiveReadOnly}
                collaborators={project.collaborators}
                projectTitle={project.title}
                showHeader={false}
              />
            }
          />

          {/* Next step CTA — shown when user has chat messages and project is still open */}
          {hasMessages && !effectiveReadOnly && !isDeleted && !isInReviewReadOnly && (
            <div className="shrink-0 border-t border-border bg-surface/80 backdrop-blur-sm px-6 py-3" data-testid="next-step-cta">
              <div className="flex items-center justify-between gap-4">
                <p className="text-sm text-muted-foreground">
                  {t("process.defineDoneHint", "Ready to formalize your project? Continue to structure your requirements.")}
                </p>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => {
                    setCompletedSteps((prev) => new Set(prev).add("define"));
                    handleStepChange("structure");
                  }}
                  className="shrink-0 gap-1.5"
                  data-testid="continue-to-structure"
                >
                  {t("process.continueToStructure", "Continue to Structure")}
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </div>
      )}

      {activeStep === "structure" && (
        <StructureStepView
          projectId={project.id}
          projectType={project.project_type}
          projectState={project.state}
          projectTitle={project.title}
          disabled={!isOnline || readOnly || isDeleted || isInReviewReadOnly || structureNotCompleted}
          readOnly={effectiveReadOnly || structureNotCompleted}
          collaborators={project.collaborators}
          onStepChange={handleStepChange}
          onSubmitted={() => {
            setCompletedSteps((prev) => new Set(prev).add("define").add("structure"));
            fetchProject(project.id).then((updated) => {
              onProjectUpdate(updated);
            }).catch(() => {});
          }}
        />
      )}

      {activeStep === "review" && (
        <div className="relative flex-1 min-h-0 flex flex-col overflow-y-auto px-6 py-6">
          <ReviewSection projectId={project.id} project={project} />
          {project.state === "rejected" && (
            <div className="px-6 py-4 mt-4 rounded-lg border-t border-border bg-orange-50 dark:bg-orange-950/20">
              <p className="text-sm text-orange-700 dark:text-orange-400 mb-2">
                {t("review.rejectedHint", "Your project was rejected. You can refine it and resubmit.")}
              </p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleStepChange("define")}
                data-testid="go-back-to-define"
              >
                {t("review.backToDefine", "Back to Define")}
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
