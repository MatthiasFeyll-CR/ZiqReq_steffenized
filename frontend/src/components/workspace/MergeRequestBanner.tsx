import { useState } from "react";
import { useTranslation } from "react-i18next";
import { AnimatePresence, motion } from "framer-motion";
import { GitMerge, Loader2 } from "lucide-react";
import { toast } from "react-toastify";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { consentMergeRequest, type MergeRequestPending } from "@/api/ideas";

interface MergeRequestBannerProps {
  mergeRequest: MergeRequestPending;
  onResolved: () => void;
}

export function MergeRequestBanner({ mergeRequest, onResolved }: MergeRequestBannerProps) {
  const { t } = useTranslation();
  const [accepting, setAccepting] = useState(false);
  const [declining, setDeclining] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);

  const busy = accepting || declining;

  async function handleAccept() {
    setAccepting(true);
    try {
      await consentMergeRequest(mergeRequest.id, "accept");
      toast.success(t("merge.mergeAccepted"));
      onResolved();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : t("merge.failedToAccept"));
    } finally {
      setAccepting(false);
    }
  }

  async function handleDecline() {
    setDeclining(true);
    setConfirmOpen(false);
    try {
      await consentMergeRequest(mergeRequest.id, "decline");
      toast.success(t("merge.mergeDeclined"));
      onResolved();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : t("merge.failedToDecline"));
    } finally {
      setDeclining(false);
    }
  }

  return (
    <>
      <AnimatePresence>
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.2 }}
          data-testid="merge-request-banner"
        >
          <div className="border-b bg-warning/5 px-4 py-3 flex items-center justify-between" role="alert" aria-live="polite">
            <div className="flex items-center gap-2">
              <GitMerge className="h-4 w-4 text-warning" />
              <p className="text-sm text-foreground">
                Merge request from{" "}
                <span className="font-medium">{mergeRequest.requesting_owner_name}</span>: merge
                your idea with &quot;{mergeRequest.requesting_idea_title}&quot;
              </p>
            </div>
            <div className="ml-4 flex gap-2">
              <Button
                variant="primary"
                size="sm"
                onClick={handleAccept}
                disabled={busy}
                data-testid="merge-accept-button"
              >
                {accepting && <Loader2 className="mr-1 h-3 w-3 animate-spin" />}
                {t("merge.accept")}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setConfirmOpen(true)}
                disabled={busy}
                data-testid="merge-decline-button"
              >
                {declining && <Loader2 className="mr-1 h-3 w-3 animate-spin" />}
                {t("merge.decline")}
              </Button>
            </div>
          </div>
        </motion.div>
      </AnimatePresence>

      <Dialog open={confirmOpen} onOpenChange={setConfirmOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t("merge.declineTitle")}</DialogTitle>
            <DialogDescription>
              {t("merge.declineDescription", { title: mergeRequest.requesting_idea_title })}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setConfirmOpen(false)}>
              {t("common.cancel")}
            </Button>
            <Button variant="destructive" onClick={handleDecline}>
              {t("merge.decline")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
