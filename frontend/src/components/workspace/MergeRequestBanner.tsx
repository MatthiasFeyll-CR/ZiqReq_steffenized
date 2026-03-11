import { useState } from "react";
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
  const [accepting, setAccepting] = useState(false);
  const [declining, setDeclining] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);

  const busy = accepting || declining;

  async function handleAccept() {
    setAccepting(true);
    try {
      await consentMergeRequest(mergeRequest.id, "accept");
      toast.success("Merge request accepted. Creating merged idea...");
      onResolved();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to accept merge request");
    } finally {
      setAccepting(false);
    }
  }

  async function handleDecline() {
    setDeclining(true);
    setConfirmOpen(false);
    try {
      await consentMergeRequest(mergeRequest.id, "decline");
      toast.success("Merge request declined");
      onResolved();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to decline merge request");
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
          <div className="border-b bg-warning/5 px-4 py-3 flex items-center justify-between">
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
                Accept
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setConfirmOpen(true)}
                disabled={busy}
                data-testid="merge-decline-button"
              >
                {declining && <Loader2 className="mr-1 h-3 w-3 animate-spin" />}
                Decline
              </Button>
            </div>
          </div>
        </motion.div>
      </AnimatePresence>

      <Dialog open={confirmOpen} onOpenChange={setConfirmOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Decline merge request?</DialogTitle>
            <DialogDescription>
              This will permanently dismiss the merge suggestion between your idea and &quot;
              {mergeRequest.requesting_idea_title}&quot;. This pair will not be suggested again.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setConfirmOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDecline}>
              Decline
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
