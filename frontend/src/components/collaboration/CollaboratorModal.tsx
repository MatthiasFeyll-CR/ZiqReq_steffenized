import { useCallback, useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-toastify";
import { useTranslation } from "react-i18next";
import { Users } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useAuth } from "@/hooks/use-auth";
import {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
  TooltipProvider,
} from "@/components/ui/tooltip";
import {
  searchUsers,
  sendInvitation,
  fetchCollaborators,
  removeCollaborator,
  transferOwnership,
  leaveIdea,
  fetchPendingInvitations,
  revokeInvitation,
  type UserSearchResult,
  type CollaboratorUser,
} from "@/api/collaboration";
import { formatRelativeTime } from "@/lib/utils";

interface CollaboratorModalProps {
  ideaId: string;
  ownerId: string;
  coOwnerId?: string | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CollaboratorModal({
  ideaId,
  ownerId,
  coOwnerId,
  open,
  onOpenChange,
}: CollaboratorModalProps) {
  const { user } = useAuth();
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const isOwner = user?.id === ownerId;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl" data-testid="collaborator-modal">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            {t("collaboration.manageTitle")}
          </DialogTitle>
          <DialogDescription>
            {t("collaboration.manageDescription")}
          </DialogDescription>
        </DialogHeader>
        <Tabs defaultValue="invite" data-testid="collaborator-tabs">
          <TabsList className="w-full">
            <TabsTrigger value="invite" data-testid="tab-invite">
              {t("collaboration.tabInvite")}
            </TabsTrigger>
            <TabsTrigger value="collaborators" data-testid="tab-collaborators">
              {t("collaboration.tabCollaborators")}
            </TabsTrigger>
            <TabsTrigger value="pending" data-testid="tab-pending">
              {t("collaboration.tabPending")}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="invite">
            <InviteTab ideaId={ideaId} isOwner={isOwner} />
          </TabsContent>

          <TabsContent value="collaborators">
            <CollaboratorsTab
              ideaId={ideaId}
              ownerId={ownerId}
              coOwnerId={coOwnerId}
              isOwner={isOwner}
              queryClient={queryClient}
              onCloseModal={() => onOpenChange(false)}
            />
          </TabsContent>

          <TabsContent value="pending">
            <PendingTab ideaId={ideaId} isOwner={isOwner} />
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}

/* ---------- Invite Tab ---------- */

function InviteTab({ ideaId, isOwner }: { ideaId: string; isOwner: boolean }) {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  const handleSearchChange = useCallback((value: string) => {
    setSearchQuery(value);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setDebouncedQuery(value.trim());
    }, 300);
  }, []);

  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, []);

  const { data: searchResults, isLoading: isSearching } = useQuery({
    queryKey: ["userSearch", debouncedQuery],
    queryFn: () => searchUsers(debouncedQuery),
    enabled: debouncedQuery.length >= 2,
  });

  const inviteMutation = useMutation({
    mutationFn: (inviteeId: string) => sendInvitation(ideaId, inviteeId),
    onSuccess: () => {
      toast.success(t("collaboration.invitationSent"));
      setSearchQuery("");
      setDebouncedQuery("");
      queryClient.invalidateQueries({ queryKey: ["invitations", ideaId] });
    },
    onError: (error: Error) => {
      toast.error(error.message || t("collaboration.failedToInvite"));
    },
  });

  return (
    <div className="space-y-4 py-2" data-testid="invite-tab">
      <Input
        placeholder={t("collaboration.searchPlaceholder")}
        value={searchQuery}
        onChange={(e) => handleSearchChange(e.target.value)}
        data-testid="invite-search-input"
      />
      {isSearching && debouncedQuery.length >= 2 && (
        <p className="text-sm text-text-secondary">{t("common.searching")}</p>
      )}
      {searchResults && searchResults.length === 0 && debouncedQuery.length >= 2 && (
        <p className="text-sm text-text-secondary" data-testid="no-results">
          {t("collaboration.noUsersFound")}
        </p>
      )}
      {searchResults && searchResults.length > 0 && (
        <ul className="space-y-2" data-testid="search-results">
          {searchResults.map((u: UserSearchResult) => (
            <li
              key={u.id}
              className="flex items-center justify-between rounded-md border p-3"
              data-testid={`search-result-${u.id}`}
            >
              <div className="flex items-center gap-3">
                <Avatar size="sm">
                  <AvatarFallback userId={u.id}>
                    {u.display_name.charAt(0).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <p className="text-sm font-medium">{u.display_name}</p>
                  <p className="text-xs text-text-secondary">{u.email}</p>
                </div>
              </div>
              {isOwner && (
                <Button
                  size="sm"
                  onClick={() => inviteMutation.mutate(u.id)}
                  disabled={inviteMutation.isPending}
                  data-testid={`invite-button-${u.id}`}
                >
                  {t("collaboration.invite")}
                </Button>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

/* ---------- Collaborators Tab ---------- */

interface CollaboratorsTabProps {
  ideaId: string;
  ownerId: string;
  coOwnerId?: string | null;
  isOwner: boolean;
  queryClient: ReturnType<typeof useQueryClient>;
  onCloseModal: () => void;
}

function CollaboratorsTab({
  ideaId,
  coOwnerId,
  isOwner,
  queryClient,
  onCloseModal,
}: CollaboratorsTabProps) {
  const { user } = useAuth();
  const { t } = useTranslation();
  const [transferDialogOpen, setTransferDialogOpen] = useState(false);
  const [transferTarget, setTransferTarget] = useState<CollaboratorUser | null>(null);
  const [removeTarget, setRemoveTarget] = useState<CollaboratorUser | null>(null);

  const isSingleOwner = isOwner && !coOwnerId;

  const { data, isLoading } = useQuery({
    queryKey: ["collaborators", ideaId],
    queryFn: () => fetchCollaborators(ideaId),
  });

  const removeMutation = useMutation({
    mutationFn: (userId: string) => removeCollaborator(ideaId, userId),
    onSuccess: () => {
      toast.success(t("collaboration.collaboratorRemoved"));
      setRemoveTarget(null);
      queryClient.invalidateQueries({ queryKey: ["collaborators", ideaId] });
    },
    onError: (error: Error) => {
      toast.error(error.message || t("collaboration.failedToRemove"));
    },
  });

  const transferMutation = useMutation({
    mutationFn: (newOwnerId: string) => transferOwnership(ideaId, newOwnerId),
    onSuccess: () => {
      toast.success(t("collaboration.ownershipTransferred"));
      setTransferDialogOpen(false);
      setTransferTarget(null);
      queryClient.invalidateQueries({ queryKey: ["collaborators", ideaId] });
      onCloseModal();
    },
    onError: (error: Error) => {
      toast.error(error.message || t("collaboration.failedToTransfer"));
    },
  });

  const leaveMutation = useMutation({
    mutationFn: () => leaveIdea(ideaId),
    onSuccess: () => {
      toast.success(t("collaboration.leftIdea"));
      queryClient.invalidateQueries({ queryKey: ["collaborators", ideaId] });
      onCloseModal();
    },
    onError: (error: Error) => {
      toast.error(error.message || t("collaboration.failedToLeave"));
    },
  });

  if (isLoading) return <p className="py-4 text-sm text-text-secondary">{t("common.loading")}</p>;

  const owner = data?.owner;
  const coOwner = data?.co_owner;
  const collaborators = data?.collaborators ?? [];

  return (
    <div className="space-y-2 py-2" data-testid="collaborators-tab">
      {/* Owner */}
      {owner && (
        <CollaboratorRow user={owner} badge={t("collaboration.owner")} />
      )}
      {/* Co-owner */}
      {coOwner && (
        <CollaboratorRow user={coOwner} badge={t("collaboration.coOwner")} />
      )}
      {/* Collaborators */}
      {collaborators.map((c) => (
        <div key={c.id} className="flex items-center justify-between rounded-md border p-3">
          <div className="flex items-center gap-3">
            <Avatar size="sm">
              <AvatarFallback userId={c.id}>
                {c.display_name.charAt(0).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div>
              <p className="text-sm font-medium">{c.display_name}</p>
              <p className="text-xs text-text-secondary">{c.email}</p>
              {c.joined_at && (
                <p className="text-xs text-text-secondary">
                  {t("collaboration.joined", { time: formatRelativeTime(c.joined_at) })}
                </p>
              )}
            </div>
          </div>
          {isOwner && c.id !== user?.id && (
            <div className="flex gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  setTransferTarget(c);
                  setTransferDialogOpen(true);
                }}
                data-testid={`transfer-button-${c.id}`}
              >
                {t("collaboration.transfer")}
              </Button>
              <Button
                size="sm"
                variant="destructive"
                onClick={() => setRemoveTarget(c)}
                data-testid={`remove-button-${c.id}`}
              >
                {t("collaboration.remove")}
              </Button>
            </div>
          )}
        </div>
      ))}
      {collaborators.length === 0 && !coOwner && (
        <p className="py-4 text-center text-sm text-text-secondary" data-testid="no-collaborators">
          {t("collaboration.noCollaborators")}
        </p>
      )}

      {/* Leave button */}
      <div className="pt-4 border-t">
        {isSingleOwner ? (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <span data-testid="leave-button-wrapper">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled
                    data-testid="leave-button"
                  >
                    {t("collaboration.leaveIdea")}
                  </Button>
                </span>
              </TooltipTrigger>
              <TooltipContent data-testid="leave-tooltip">
                {t("collaboration.transferBeforeLeaving")}
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        ) : (
          <Button
            variant="outline"
            size="sm"
            onClick={() => leaveMutation.mutate()}
            disabled={leaveMutation.isPending}
            data-testid="leave-button"
          >
            {t("collaboration.leaveIdea")}
          </Button>
        )}
      </div>

      {/* Remove confirmation dialog */}
      {removeTarget && (
        <Dialog open={!!removeTarget} onOpenChange={() => setRemoveTarget(null)}>
          <DialogContent data-testid="remove-confirm-dialog">
            <DialogHeader>
              <DialogTitle>{t("collaboration.removeCollaborator")}</DialogTitle>
              <DialogDescription>
                {t("collaboration.removeConfirm", { name: removeTarget.display_name })}
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button variant="ghost" onClick={() => setRemoveTarget(null)}>
                {t("common.cancel")}
              </Button>
              <Button
                variant="destructive"
                onClick={() => removeMutation.mutate(removeTarget.id)}
                disabled={removeMutation.isPending}
                data-testid="confirm-remove-button"
              >
                {t("collaboration.remove")}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}

      {/* Transfer confirmation dialog */}
      {transferDialogOpen && transferTarget && (
        <Dialog open={transferDialogOpen} onOpenChange={setTransferDialogOpen}>
          <DialogContent data-testid="transfer-confirm-dialog">
            <DialogHeader>
              <DialogTitle>{t("collaboration.transferOwnership")}</DialogTitle>
              <DialogDescription>
                {t("collaboration.transferConfirm", { name: transferTarget.display_name })}
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button variant="ghost" onClick={() => setTransferDialogOpen(false)}>
                {t("common.cancel")}
              </Button>
              <Button
                onClick={() => transferMutation.mutate(transferTarget.id)}
                disabled={transferMutation.isPending}
                data-testid="confirm-transfer-button"
              >
                {t("collaboration.transfer")}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}

function CollaboratorRow({ user, badge }: { user: CollaboratorUser; badge: string }) {
  return (
    <div className="flex items-center justify-between rounded-md border p-3">
      <div className="flex items-center gap-3">
        <Avatar size="sm">
          <AvatarFallback userId={user.id}>
            {user.display_name.charAt(0).toUpperCase()}
          </AvatarFallback>
        </Avatar>
        <div>
          <p className="text-sm font-medium">
            {user.display_name}
            <Badge className="ml-2" data-testid={`badge-${badge.toLowerCase().replace(" ", "-")}`}>
              {badge}
            </Badge>
          </p>
          <p className="text-xs text-text-secondary">{user.email}</p>
        </div>
      </div>
    </div>
  );
}

/* ---------- Pending Invitations Tab ---------- */

function PendingTab({ ideaId, isOwner }: { ideaId: string; isOwner: boolean }) {
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["invitations", ideaId],
    queryFn: () => fetchPendingInvitations(ideaId),
    enabled: isOwner,
  });

  const revokeMutation = useMutation({
    mutationFn: (invitationId: string) => revokeInvitation(invitationId),
    onSuccess: () => {
      toast.success(t("collaboration.invitationRevoked"));
      queryClient.invalidateQueries({ queryKey: ["invitations", ideaId] });
    },
    onError: (error: Error) => {
      toast.error(error.message || t("collaboration.failedToRevoke"));
    },
  });

  if (!isOwner) {
    return (
      <p className="py-4 text-center text-sm text-text-secondary" data-testid="pending-tab">
        {t("collaboration.ownerOnly")}
      </p>
    );
  }

  if (isLoading) return <p className="py-4 text-sm text-text-secondary">{t("common.loading")}</p>;

  const invitations = data?.invitations ?? [];

  return (
    <div className="space-y-2 py-2" data-testid="pending-tab">
      {invitations.length === 0 && (
        <p className="py-4 text-center text-sm text-text-secondary" data-testid="no-pending">
          {t("collaboration.noPending")}
        </p>
      )}
      {invitations.map((inv) => (
        <div
          key={inv.id}
          className="flex items-center justify-between rounded-md border p-3"
          data-testid={`pending-invitation-${inv.id}`}
        >
          <div className="flex items-center gap-3">
            <Avatar size="sm">
              <AvatarFallback userId={inv.invitee.id}>
                {inv.invitee.display_name.charAt(0).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div>
              <p className="text-sm font-medium">{inv.invitee.display_name}</p>
              <p className="text-xs text-text-secondary">{inv.invitee.email}</p>
              <p className="text-xs text-text-secondary">
                {t("collaboration.invited", { time: formatRelativeTime(inv.created_at) })}
              </p>
            </div>
          </div>
          <Button
            size="sm"
            variant="destructive"
            onClick={() => revokeMutation.mutate(inv.id)}
            disabled={revokeMutation.isPending}
            data-testid={`revoke-button-${inv.id}`}
          >
            {t("collaboration.revoke")}
          </Button>
        </div>
      ))}
    </div>
  );
}
