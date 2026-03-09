import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";

export interface InvitationCardProps {
  id: string;
  ideaId: string;
  ideaTitle: string;
  inviterName: string;
  createdAt: string;
  onAccept?: (id: string) => void;
  onDecline?: (id: string) => void;
}

export function InvitationCard({
  id,
  ideaTitle,
  inviterName,
  onAccept,
  onDecline,
}: InvitationCardProps) {
  const { t } = useTranslation();

  return (
    <div className="flex items-center justify-between rounded-lg border border-border bg-surface p-4 border-l-4 border-l-primary">
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium text-foreground">{ideaTitle}</p>
        <p className="text-sm text-text-secondary">
          {t("landing.invitations.from", { name: inviterName })}
        </p>
      </div>
      <div className="ml-4 flex gap-2">
        <Button
          variant="primary"
          size="sm"
          onClick={() => onAccept?.(id)}
        >
          {t("landing.invitations.accept")}
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onDecline?.(id)}
        >
          {t("landing.invitations.decline")}
        </Button>
      </div>
    </div>
  );
}
