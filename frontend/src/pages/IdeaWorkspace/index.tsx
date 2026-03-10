import { useCallback, useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { fetchIdea, type Idea } from "@/api/ideas";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { WorkspaceLayout } from "@/components/workspace/WorkspaceLayout";
import { WorkspaceHeader } from "@/components/workspace/WorkspaceHeader";
import { ChatPanel } from "@/components/workspace/ChatPanel";
import { OfflineBanner } from "@/components/common/OfflineBanner";
import { useSectionVisibility } from "@/components/workspace/useSectionVisibility";
import { useSelector } from "react-redux";
import { selectIsOnline } from "@/store/websocket-slice";

export default function IdeaWorkspacePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t } = useTranslation();

  const [idea, setIdea] = useState<Idea | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<{ message: string; status?: number } | null>(null);

  useEffect(() => {
    if (!id) return;

    let cancelled = false;
    setLoading(true);
    setError(null);

    fetchIdea(id)
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
    <IdeaWorkspaceContent idea={idea} onIdeaUpdate={handleIdeaUpdate} />
  );
}

function IdeaWorkspaceContent({
  idea,
  onIdeaUpdate,
}: {
  idea: Idea;
  onIdeaUpdate: (idea: Idea) => void;
}) {
  const { reviewVisible, chatLocked, allReadOnly, lockReason } = useSectionVisibility(idea);
  const isOnline = useSelector(selectIsOnline);

  const effectiveChatLocked = chatLocked || !isOnline;
  const effectiveLockReason = !isOnline
    ? "You are currently offline. Chat is disabled."
    : lockReason;

  return (
    <div className="flex flex-col h-full" data-testid="idea-workspace">
      <WorkspaceHeader idea={idea} onIdeaUpdate={onIdeaUpdate} readOnly={allReadOnly} />
      <OfflineBanner />
      <WorkspaceLayout
        chatPanel={
          <ChatPanel idea={idea} locked={effectiveChatLocked} lockReason={effectiveLockReason} />
        }
        reviewVisible={reviewVisible}
        ideaId={idea.id}
        disabled={!isOnline}
      />
    </div>
  );
}
