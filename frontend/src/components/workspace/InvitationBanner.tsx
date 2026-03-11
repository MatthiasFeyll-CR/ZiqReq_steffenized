import { useTranslation } from "react-i18next";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import { toast } from "react-toastify";
import { Button } from "@/components/ui/button";
import { acceptInvitation, declineInvitation } from "@/api/collaboration";
import { fetchInvitations } from "@/api/ideas";
import { useAuth } from "@/hooks/use-auth";

interface InvitationBannerProps {
  ideaId: string;
}

export function InvitationBanner({ ideaId }: InvitationBannerProps) {
  const { t } = useTranslation();
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const { data } = useQuery({
    queryKey: ["invitations"],
    queryFn: fetchInvitations,
    enabled: !!user,
  });

  const invitation = data?.invitations?.find((inv) => inv.idea_id === ideaId);

  const acceptMut = useMutation({
    mutationFn: acceptInvitation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["invitations"] });
      queryClient.invalidateQueries({ queryKey: ["collaborators", ideaId] });
      toast.success(t("landing.invitations.accepted", "Invitation accepted"));
    },
  });

  const declineMut = useMutation({
    mutationFn: declineInvitation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["invitations"] });
      toast.success(t("landing.invitations.declined", "Invitation declined"));
    },
  });

  return (
    <AnimatePresence>
      {invitation && (
        <motion.div
          key={invitation.id}
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.3 }}
          data-testid="invitation-banner"
        >
          <div className="border-b bg-primary/5 px-4 py-3 border-l-4 border-l-primary flex items-center justify-between">
            <p className="text-sm text-foreground">
              <span className="font-medium">{invitation.inviter.display_name}</span>
              {" "}
              {t("workspace.invitationBanner.text", "invited you to collaborate on this idea")}
            </p>
            <div className="ml-4 flex gap-2">
              <Button
                variant="primary"
                size="sm"
                onClick={() => acceptMut.mutate(invitation.id)}
                disabled={acceptMut.isPending || declineMut.isPending}
                data-testid="banner-accept-button"
              >
                {t("landing.invitations.accept", "Accept")}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => declineMut.mutate(invitation.id)}
                disabled={acceptMut.isPending || declineMut.isPending}
                data-testid="banner-decline-button"
              >
                {t("landing.invitations.decline", "Decline")}
              </Button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
