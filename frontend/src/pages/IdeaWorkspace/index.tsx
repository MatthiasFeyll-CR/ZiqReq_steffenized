import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { fetchIdea, restoreIdea, type Idea } from "@/api/ideas";
import { fetchChatMessages } from "@/api/chat";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertTriangle, ArrowRight, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { patchIdea } from "@/api/ideas";
import { WorkspaceLayout } from "@/components/workspace/WorkspaceLayout";
import { WorkspaceHeader } from "@/components/workspace/WorkspaceHeader";
import { ChatPanel } from "@/components/workspace/ChatPanel";
import { DocumentView } from "@/components/workspace/DocumentView";
import { OfflineBanner } from "@/components/common/OfflineBanner";
import { InvitationBanner } from "@/components/workspace/InvitationBanner";
import { ReadOnlyBanner } from "@/components/workspace/ReadOnlyBanner";
import { MergeRequestBanner } from "@/components/workspace/MergeRequestBanner";
import { MergedIdeaBanner } from "@/components/workspace/MergedIdeaBanner";
import { AppendedIdeaBanner } from "@/components/workspace/AppendedIdeaBanner";
import { ReviewSection } from "@/components/review/ReviewSection";
import { useSectionVisibility } from "@/components/workspace/useSectionVisibility";
import { useIdeaSync } from "@/hooks/useIdeaSync";
import { useSelector } from "react-redux";
import { selectIsOnline, selectConnectionState } from "@/store/websocket-slice";
import { useWsSend } from "@/app/providers";
import type { ProcessStep } from "@/components/workspace/ProcessStepper";

const VALID_STEPS: ProcessStep[] = ["brainstorm", "document", "review"];

function parseStep(value: string | null): ProcessStep {
  if (value && VALID_STEPS.includes(value as ProcessStep)) {
    return value as ProcessStep;
  }
  return "brainstorm";
}

export default function IdeaWorkspacePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const shareToken = searchParams.get("token");

  const [idea, setIdea] = useState<Idea | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<{ message: string; status?: number } | null>(null);

  useEffect(() => {
    if (!id) return;

    let cancelled = false;
    setLoading(true);
    setError(null);

    (shareToken ? fetchIdea(id, shareToken) : fetchIdea(id))
      .then((data) => {
        if (!cancelled) {
          setIdea(data);
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
  }, [id, shareToken, t]);

  const handleIdeaUpdate = useCallback((updated: Idea) => {
    setIdea(updated);
  }, []);

  useEffect(() => {
    if (idea?.title) {
      document.title = idea.title;
    }
    return () => {
      document.title = "ZiqReq";
    };
  }, [idea?.title]);

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
            ? t("workspace.notFound", "Idea not found")
            : is403
              ? t("workspace.noAccess", "You don't have access to this idea")
              : t("common.error")}
        </h2>
        <p className="text-sm text-muted-foreground">{error.message}</p>
        <Button variant="outline" onClick={() => navigate("/")}>
          {t("workspace.backToHome", "Back to home")}
        </Button>
      </div>
    );
  }

  if (!idea) return null;

  return (
    <IdeaWorkspaceContent idea={idea} onIdeaUpdate={handleIdeaUpdate} readOnly={!!shareToken || !!idea.read_only} shareToken={shareToken} />
  );
}

function IdeaWorkspaceContent({
  idea,
  onIdeaUpdate,
  readOnly = false,
  shareToken,
}: {
  idea: Idea;
  onIdeaUpdate: (idea: Idea) => void;
  readOnly?: boolean;
  shareToken?: string | null;
}) {
  const { t } = useTranslation();
  const [searchParams, setSearchParams] = useSearchParams();
  const { chatLocked, allReadOnly, lockReason } = useSectionVisibility(idea);
  const isOnline = useSelector(selectIsOnline);
  const connectionState = useSelector(selectConnectionState);
  const sendWs = useWsSend();

  // Step management via URL — default step depends on idea state
  const [activeStep, setActiveStep] = useState<ProcessStep>(() => {
    const urlStep = parseStep(searchParams.get("step"));
    // If no explicit step in URL, derive from idea state
    if (!searchParams.get("step")) {
      if (idea.state === "rejected" || idea.state === "deleted") return "brainstorm";
      if (["in_review", "accepted", "dropped"].includes(idea.state)) return "review";
    }
    return urlStep;
  });

  // Track whether the idea has at least one chat message
  const [hasMessages, setHasMessages] = useState<boolean | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchChatMessages(idea.id, { limit: 1 }).then((data) => {
      if (!cancelled) {
        setHasMessages(data.total > 0);
      }
    }).catch(() => {
      if (!cancelled) setHasMessages(false);
    });
    return () => { cancelled = true; };
  }, [idea.id]);

  // Listen for new chat messages to update hasMessages
  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      if (detail.idea_id === idea.id) {
        setHasMessages(true);
      }
    };
    window.addEventListener("ws:chat_message", handler);
    return () => window.removeEventListener("ws:chat_message", handler);
  }, [idea.id]);

  const handleStepChange = useCallback(
    (step: ProcessStep) => {
      setActiveStep(step);
      setSearchParams((prev) => {
        const next = new URLSearchParams(prev);
        if (step === "brainstorm") {
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
  const hasBeenSubmitted = idea.state !== "open" && idea.state !== "deleted";

  // Access gates
  const canAccessDocument = hasMessages === true;
  const canAccessReview = hasBeenSubmitted;

  const documentGateMessage = t(
    "process.documentGate",
    "Send at least one message in the brainstorming chat before proceeding to the document.",
  );
  const reviewGateMessage = t(
    "process.reviewGate",
    "Submit your idea for review first.",
  );

  // Auto-navigate on state transitions
  const prevStateRef = useRef(idea.state);
  useEffect(() => {
    if (prevStateRef.current === idea.state) return;
    prevStateRef.current = idea.state;

    if (idea.state === "rejected" || idea.state === "deleted") {
      handleStepChange("brainstorm");
    } else if (["in_review", "accepted", "dropped"].includes(idea.state)) {
      handleStepChange("review");
    }
  }, [idea.state, handleStepChange]);

  // If landed on a gated step, redirect to brainstorm
  useEffect(() => {
    if (activeStep === "document" && !canAccessDocument) {
      handleStepChange("brainstorm");
    } else if (activeStep === "review" && !canAccessReview) {
      // Redirect to document if they can access it, otherwise brainstorm
      handleStepChange(canAccessDocument ? "document" : "brainstorm");
    }
  }, [activeStep, canAccessDocument, canAccessReview, handleStepChange]);

  // Subscribe to idea's WebSocket group when connected
  useEffect(() => {
    if (connectionState === "online") {
      sendWs({ type: "subscribe_idea", idea_id: idea.id });
    }
    return () => {
      if (connectionState === "online") {
        sendWs({ type: "unsubscribe_idea", idea_id: idea.id });
      }
    };
  }, [idea.id, connectionState, sendWs]);

  // Return-from-idle sync
  useIdeaSync({ ideaId: idea.id, onIdeaUpdate });
  const ideaRef = useRef(idea);
  ideaRef.current = idea;
  const onIdeaUpdateRef = useRef(onIdeaUpdate);
  onIdeaUpdateRef.current = onIdeaUpdate;

  const hasMergePending = !!idea.merge_request_pending;
  const isClosedByMerge = !!idea.merged_idea_ref;
  const isClosedByAppend = !!idea.appended_idea_ref;
  const isDeleted = idea.state === "deleted";
  const isClosedIdea = isClosedByMerge || isClosedByAppend || isDeleted;
  const isInReview = idea.state === "in_review";
  const isInReviewReadOnly = isInReview && activeStep !== "review";

  // Listen for WebSocket title_update events
  useEffect(() => {
    const handler = (e: Event) => {
      const { idea_id, title } = (e as CustomEvent).detail;
      if (idea_id === ideaRef.current.id) {
        onIdeaUpdateRef.current({ ...ideaRef.current, title });
      }
    };
    window.addEventListener("ws:title_update", handler);
    return () => window.removeEventListener("ws:title_update", handler);
  }, []);

  // Listen for WebSocket merge_request events
  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      const targetId = detail?.target_idea_id ?? detail?.idea_id;
      if (targetId === ideaRef.current.id) {
        fetchIdea(ideaRef.current.id).then((updated) => {
          onIdeaUpdateRef.current(updated);
        }).catch(() => {});
      }
    };
    window.addEventListener("ws:merge_request", handler);
    return () => window.removeEventListener("ws:merge_request", handler);
  }, []);

  const handleMergeResolved = useCallback(() => {
    fetchIdea(idea.id).then((updated) => {
      onIdeaUpdate(updated);
    }).catch(() => {
      onIdeaUpdate({ ...idea, merge_request_pending: null });
    });
  }, [idea, onIdeaUpdate]);

  const [isRestoring, setIsRestoring] = useState(false);
  const handleRestore = useCallback(async () => {
    setIsRestoring(true);
    try {
      await restoreIdea(idea.id);
      const updated = await fetchIdea(idea.id);
      onIdeaUpdate(updated);
    } catch {
      // If refetch fails, optimistically set state back to open
      onIdeaUpdate({ ...idea, state: "open" });
    } finally {
      setIsRestoring(false);
    }
  }, [idea, onIdeaUpdate]);

  const effectiveChatLocked = chatLocked || !isOnline || readOnly || hasMergePending || isClosedIdea || isInReviewReadOnly;
  const effectiveLockReason = readOnly
    ? "Viewing shared idea — chat is read-only"
    : !isOnline
      ? "You are currently offline. Chat is disabled."
      : isDeleted
        ? "This idea has been deleted. All sections are read-only."
        : isClosedByMerge
          ? "This idea was merged. Content is read-only."
          : isClosedByAppend
            ? "This idea was appended. Content is read-only."
            : hasMergePending
              ? "This idea has a pending merge request. Accept or decline to continue editing."
              : isInReviewReadOnly
                ? "This idea is currently under review. Content is read-only."
                : lockReason;
  const effectiveReadOnly = allReadOnly || readOnly || isClosedIdea || isInReviewReadOnly;

  const handleAgentModeChange = useCallback(
    async (value: string) => {
      const mode = value as "interactive" | "silent";
      const previousMode = idea.agent_mode;
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
    <div className="flex flex-col h-full overflow-hidden" data-testid="idea-workspace">
      <WorkspaceHeader
        idea={idea}
        onIdeaUpdate={onIdeaUpdate}
        readOnly={effectiveReadOnly || hasMergePending}
        activeStep={activeStep}
        onStepChange={handleStepChange}
        canAccessDocument={canAccessDocument}
        canAccessReview={canAccessReview}
        documentGateMessage={documentGateMessage}
        reviewGateMessage={reviewGateMessage}
        shareToken={shareToken}
      />

      {/* Banners */}
      {readOnly && <ReadOnlyBanner />}
      {!readOnly && isClosedByMerge && idea.merged_idea_ref && (
        <MergedIdeaBanner mergedIdeaRef={idea.merged_idea_ref} />
      )}
      {!readOnly && isClosedByAppend && idea.appended_idea_ref && (
        <AppendedIdeaBanner appendedIdeaRef={idea.appended_idea_ref} />
      )}
      {!readOnly && idea.merge_request_pending && (
        <MergeRequestBanner mergeRequest={idea.merge_request_pending} onResolved={handleMergeResolved} />
      )}
      {!readOnly && !isClosedIdea && <InvitationBanner ideaId={idea.id} />}
      {isDeleted && (
        <div
          className="shrink-0 flex items-center gap-3 px-6 py-3 bg-red-50 dark:bg-red-950/20 border-b border-red-200 dark:border-red-900/30"
          data-testid="deleted-banner"
        >
          <p className="text-sm text-red-700 dark:text-red-400 flex-1">
            {t("workspace.deletedReason", "This idea has been deleted. All content is read-only.")}
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRestore}
            disabled={isRestoring}
            data-testid="restore-idea-button"
            className="shrink-0 border-red-300 text-red-700 hover:bg-red-100 dark:border-red-800 dark:text-red-400 dark:hover:bg-red-950/40"
          >
            {isRestoring ? (
              <RotateCcw className="mr-1 h-4 w-4 animate-spin" />
            ) : (
              <RotateCcw className="mr-1 h-4 w-4" />
            )}
            {t("workspace.restoreIdea", "Restore")}
          </Button>
        </div>
      )}
      {isInReviewReadOnly && (
        <div
          className="shrink-0 flex items-center gap-3 px-6 py-3 bg-amber-50 dark:bg-amber-950/20 border-b border-amber-200 dark:border-amber-900/30"
          data-testid="in-review-banner"
        >
          <p className="text-sm text-amber-700 dark:text-amber-400 flex-1">
            {t("workspace.inReviewReadOnly", "This idea is currently under review. Content is read-only until the review is complete.")}
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleStepChange("review")}
            data-testid="go-to-review-button"
            className="shrink-0 border-amber-300 text-amber-700 hover:bg-amber-100 dark:border-amber-800 dark:text-amber-400 dark:hover:bg-amber-950/40"
          >
            {t("workspace.goToReview", "Go to Review")}
          </Button>
        </div>
      )}
      <OfflineBanner />

      {/* Step Content */}
      {activeStep === "brainstorm" && (
        <div className="flex-1 min-h-0 flex flex-col">

          {/* Agent mode selector — contextual to brainstorm step */}
          <div className="shrink-0 flex items-center gap-2 px-6 py-2 border-b border-border/50 bg-surface">
            <span className="text-sm text-muted-foreground">
              {t("workspace.agentMode", "AI Mode")}
            </span>
            <Select value={idea.agent_mode} onValueChange={handleAgentModeChange} disabled={effectiveReadOnly}>
              <SelectTrigger className="w-36 h-8 text-sm" data-testid="agent-mode-trigger">
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
          </div>

          <WorkspaceLayout
            chatPanel={
              <ChatPanel idea={idea} locked={effectiveChatLocked} lockReason={effectiveLockReason} readOnly={readOnly || isInReviewReadOnly} />
            }
            ideaId={idea.id}
            disabled={!isOnline || readOnly || hasMergePending || isClosedIdea || isInReviewReadOnly}
            readOnly={readOnly || isInReviewReadOnly}
          />

          {/* Next step CTA — shown when user has chat messages and idea is still open */}
          {hasMessages && !effectiveReadOnly && !hasMergePending && !isClosedIdea && !isInReviewReadOnly && (
            <div className="shrink-0 border-t border-border bg-surface/80 backdrop-blur-sm px-6 py-3" data-testid="next-step-cta">
              <div className="flex items-center justify-between gap-4">
                <p className="text-sm text-muted-foreground">
                  {t("process.brainstormDoneHint", "Ready to formalize your idea? Continue to generate your Business Requirements Document.")}
                </p>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => handleStepChange("document")}
                  className="shrink-0 gap-1.5"
                  data-testid="continue-to-document"
                >
                  {t("process.continueToDocument", "Continue to Document")}
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </div>
      )}

      {activeStep === "document" && (
        <div className="flex-1 min-h-0 flex flex-col">

          {/* Step guidance */}
          <div className="shrink-0 px-6 pt-4 pb-2">
            <p className="text-sm text-muted-foreground">
              {t("process.documentGuide", "Review and refine each section below, then submit for review when you're ready.")}
            </p>
          </div>

          <div className="flex-1 min-h-0 overflow-y-auto px-6 pb-4">
            <DocumentView
              ideaId={idea.id}
              ideaState={idea.state}
              disabled={!isOnline || readOnly || hasMergePending || isClosedIdea || isInReviewReadOnly}
              onStepChange={handleStepChange}
              onSubmitted={() => {
                fetchIdea(idea.id).then((updated) => {
                  onIdeaUpdate(updated);
                }).catch(() => {});
              }}
            />
          </div>
        </div>
      )}

      {activeStep === "review" && (
        <div className="relative flex-1 min-h-0 flex flex-col overflow-y-auto px-6 py-6">
          <ReviewSection ideaId={idea.id} idea={idea} />
          {idea.state === "rejected" && (
            <div className="px-6 py-4 mt-4 rounded-lg border-t border-border bg-orange-50 dark:bg-orange-950/20">
              <p className="text-sm text-orange-700 dark:text-orange-400 mb-2">
                {t("review.rejectedHint", "Your idea was rejected. You can go back to brainstorming to refine it.")}
              </p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleStepChange("brainstorm")}
                data-testid="go-back-to-brainstorm"
              >
                {t("review.backToBrainstorm", "Back to Brainstorm")}
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
