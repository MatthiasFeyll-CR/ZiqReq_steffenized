import { useTranslation } from "react-i18next";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { toast } from "react-toastify";
import { UserPlus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { acceptInvitation, declineInvitation } from "@/api/collaboration";
import { fetchInvitations } from "@/api/projects";
import { useAuth } from "@/hooks/use-auth";

interface InvitationBannerProps {
  projectId: string;
  onAccepted?: () => void;
  onDeclined?: () => void;
}

export function InvitationBanner({ projectId, onAccepted, onDeclined }: InvitationBannerProps) {
  const { t } = useTranslation();
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const { data } = useQuery({
    queryKey: ["invitations"],
    queryFn: fetchInvitations,
    enabled: !!user,
  });

  const invitation = data?.invitations?.find((inv) => inv.project_id === projectId);
  const prefersReducedMotion = useReducedMotion();

  const acceptMut = useMutation({
    mutationFn: acceptInvitation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["invitations"] });
      queryClient.invalidateQueries({ queryKey: ["collaborators", projectId] });
      queryClient.invalidateQueries({ queryKey: ["project", projectId] });
      toast.success(t("landing.invitations.accepted", "Invitation accepted"));
      onAccepted?.();
    },
  });

  const declineMut = useMutation({
    mutationFn: declineInvitation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["invitations"] });
      toast.success(t("landing.invitations.declined", "Invitation declined"));
      onDeclined?.();
    },
  });

  return (
    <AnimatePresence>
      {invitation && (
        <motion.div
          key={invitation.id}
          initial={prefersReducedMotion ? false : { height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          exit={prefersReducedMotion ? { opacity: 0 } : { height: 0, opacity: 0 }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.3 }}
          data-testid="invitation-banner"
        >
          <div className="shrink-0 border-b border-l-4 border-l-primary bg-primary/5 px-6 py-3 flex items-center gap-3" role="alert" aria-live="polite">
              <UserPlus className="h-4 w-4 text-primary shrink-0" />
              <p className="text-sm text-foreground">
                <span className="font-medium">{invitation.inviter.display_name}</span>
                {" "}
                {t("workspace.invitationBanner.text", "invited you to collaborate on this project")}
              </p>
            <div className="flex gap-2 ml-3">
              <Button
                variant="primary"
                size="sm"
                onClick={() => acceptMut.mutate(invitation.id)}
                disabled={acceptMut.isPending || declineMut.isPending}
                data-testid="banner-accept-button"
              >
                {t("workspace.invitationBanner.accept", "Accept Invite")}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => declineMut.mutate(invitation.id)}
                disabled={acceptMut.isPending || declineMut.isPending}
                data-testid="banner-decline-button"
              >
                {t("workspace.invitationBanner.decline", "Decline")}
              </Button>
            </div>
            </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
