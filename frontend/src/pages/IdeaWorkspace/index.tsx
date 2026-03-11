import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { fetchIdea, type Idea } from "@/api/ideas";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { WorkspaceLayout } from "@/components/workspace/WorkspaceLayout";
import { WorkspaceHeader } from "@/components/workspace/WorkspaceHeader";
import { ChatPanel } from "@/components/workspace/ChatPanel";
import { OfflineBanner } from "@/components/common/OfflineBanner";
import { InvitationBanner } from "@/components/workspace/InvitationBanner";
import { ReadOnlyBanner } from "@/components/workspace/ReadOnlyBanner";
import { MergeRequestBanner } from "@/components/workspace/MergeRequestBanner";
import { MergedIdeaBanner } from "@/components/workspace/MergedIdeaBanner";
import { AppendedIdeaBanner } from "@/components/workspace/AppendedIdeaBanner";
import { LockOverlay } from "@/components/workspace/LockOverlay";
import { ReviewSection } from "@/components/review/ReviewSection";
import { useSectionVisibility } from "@/components/workspace/useSectionVisibility";
import { useSelector } from "react-redux";
import { selectIsOnline } from "@/store/websocket-slice";

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

    fetchIdea(id, shareToken ?? undefined)
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
  }, [id, t]);

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
        <div className="h-16 border-b flex items-center gap-4 px-4">
          <Skeleton className="h-8 w-8 rounded" />
          <Skeleton className="h-6 w-64" />
          <div className="flex-1" />
          <Skeleton className="h-8 w-32" />
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
    <IdeaWorkspaceContent idea={idea} onIdeaUpdate={handleIdeaUpdate} readOnly={!!shareToken} />
  );
}

function IdeaWorkspaceContent({
  idea,
  onIdeaUpdate,
  readOnly = false,
}: {
  idea: Idea;
  onIdeaUpdate: (idea: Idea) => void;
  readOnly?: boolean;
}) {
  const { reviewVisible, chatLocked, allReadOnly, lockReason } = useSectionVisibility(idea);
  const isOnline = useSelector(selectIsOnline);
  const ideaRef = useRef(idea);
  ideaRef.current = idea;
  const onIdeaUpdateRef = useRef(onIdeaUpdate);
  onIdeaUpdateRef.current = onIdeaUpdate;
  const reviewSectionRef = useRef<HTMLDivElement>(null);
  const brainstormingRef = useRef<HTMLDivElement>(null);
  const prevStateRef = useRef(idea.state);

  const hasMergePending = !!idea.merge_request_pending;
  const isClosedByMerge = !!idea.merged_idea_ref;
  const isClosedByAppend = !!idea.appended_idea_ref;
  const isClosedIdea = isClosedByMerge || isClosedByAppend;

  // has_been_submitted heuristic: state !== 'open' means it was submitted at least once
  const hasBeenSubmitted = idea.state !== "open";

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

  // Listen for WebSocket merge_request events — refetch idea to update merge_request_pending
  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      const targetId = detail?.target_idea_id ?? detail?.idea_id;
      if (targetId === ideaRef.current.id) {
        fetchIdea(ideaRef.current.id).then((updated) => {
          onIdeaUpdateRef.current(updated);
        }).catch(() => {
          // Silently ignore refetch errors
        });
      }
    };
    window.addEventListener("ws:merge_request", handler);
    return () => window.removeEventListener("ws:merge_request", handler);
  }, []);

  // Auto-scroll based on state transitions
  useEffect(() => {
    if (prevStateRef.current === idea.state) return;
    prevStateRef.current = idea.state;

    if (idea.state === "rejected") {
      // Scroll to brainstorming (top)
      brainstormingRef.current?.scrollIntoView({ behavior: "smooth" });
    } else if (["in_review", "accepted", "dropped"].includes(idea.state)) {
      // Scroll to review section (below fold)
      reviewSectionRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [idea.state]);

  // Refetch idea after merge request resolved to clear merge_request_pending
  const handleMergeResolved = useCallback(() => {
    fetchIdea(idea.id).then((updated) => {
      onIdeaUpdate(updated);
    }).catch(() => {
      // Optimistically clear merge_request_pending
      onIdeaUpdate({ ...idea, merge_request_pending: null });
    });
  }, [idea, onIdeaUpdate]);

  const effectiveChatLocked = chatLocked || !isOnline || readOnly || hasMergePending || isClosedIdea;
  const effectiveLockReason = readOnly
    ? "Viewing shared idea — chat is read-only"
    : !isOnline
      ? "You are currently offline. Chat is disabled."
      : isClosedByMerge
        ? "This idea was merged. Content is read-only."
        : isClosedByAppend
          ? "This idea was appended. Content is read-only."
          : hasMergePending
            ? "This idea has a pending merge request. Accept or decline to continue editing."
            : lockReason;
  const effectiveReadOnly = allReadOnly || readOnly || isClosedIdea;

  return (
    <div className="flex flex-col h-full overflow-y-auto" data-testid="idea-workspace">
      <WorkspaceHeader idea={idea} onIdeaUpdate={onIdeaUpdate} readOnly={effectiveReadOnly || hasMergePending} />
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
      <OfflineBanner />
      <div ref={brainstormingRef} className="relative flex-1 min-h-0 flex flex-col" style={{ minHeight: hasBeenSubmitted ? "calc(100vh - 64px)" : undefined }}>
        {(hasMergePending || isClosedIdea) && (
          <LockOverlay reason={isClosedByMerge ? "This idea was merged. Content is read-only." : isClosedByAppend ? "This idea was appended. Content is read-only." : "This idea has a pending merge request. Accept or decline to continue editing."} />
        )}
        <WorkspaceLayout
          chatPanel={
            <ChatPanel idea={idea} locked={effectiveChatLocked} lockReason={effectiveLockReason} readOnly={readOnly} />
          }
          reviewVisible={reviewVisible}
          ideaId={idea.id}
          ideaState={idea.state}
          disabled={!isOnline || readOnly || hasMergePending || isClosedIdea}
          readOnly={readOnly}
        />
      </div>
      {hasBeenSubmitted && (
        <div ref={reviewSectionRef} data-testid="review-section-wrapper">
          <ReviewSection ideaId={idea.id} idea={idea} />
        </div>
      )}
    </div>
  );
}
