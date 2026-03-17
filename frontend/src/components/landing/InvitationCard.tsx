import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";

export interface InvitationCardProps {
  id: string;
  projectId: string;
  projectTitle: string;
  inviterName: string;
  createdAt: string;
  onAccept?: (id: string, projectId: string) => void;
  onDecline?: (id: string) => void;
}

export function InvitationCard({
  id,
  projectId,
  projectTitle,
  inviterName,
  onAccept,
  onDecline,
}: InvitationCardProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();

  return (
    <div
      className="flex items-center justify-between rounded-md border border-border bg-background p-3 border-l-4 border-l-primary dark:bg-muted/40 cursor-pointer transition-colors hover:bg-muted/50"
      onClick={() => navigate(`/project/${projectId}`)}
      role="link"
      data-testid={`invitation-card-${projectId}`}
    >
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium text-foreground">{projectTitle}</p>
        <p className="text-sm text-text-secondary">
          {t("landing.invitations.from", { name: inviterName })}
        </p>
      </div>
      <div className="ml-4 flex gap-2">
        <Button
          variant="primary"
          size="sm"
          onClick={(e) => { e.stopPropagation(); onAccept?.(id, projectId); }}
        >
          {t("landing.invitations.accept")}
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={(e) => { e.stopPropagation(); onDecline?.(id); }}
        >
          {t("landing.invitations.decline")}
        </Button>
      </div>
    </div>
  );
}
