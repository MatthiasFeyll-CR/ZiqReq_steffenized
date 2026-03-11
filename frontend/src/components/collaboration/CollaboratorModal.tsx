import { useCallback, useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-toastify";
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
  searchUsers,
  sendInvitation,
  fetchCollaborators,
  removeCollaborator,
  transferOwnership,
  fetchPendingInvitations,
  revokeInvitation,
  type UserSearchResult,
  type CollaboratorUser,
} from "@/api/collaboration";
import { formatRelativeTime } from "@/lib/utils";

interface CollaboratorModalProps {
  ideaId: string;
  ownerId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CollaboratorModal({
  ideaId,
  ownerId,
  open,
  onOpenChange,
}: CollaboratorModalProps) {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const isOwner = user?.id === ownerId;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl" data-testid="collaborator-modal">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Manage Collaborators
          </DialogTitle>
          <DialogDescription>
            Invite users, manage collaborators, and view pending invitations.
          </DialogDescription>
        </DialogHeader>
        <Tabs defaultValue="invite" data-testid="collaborator-tabs">
          <TabsList className="w-full">
            <TabsTrigger value="invite" data-testid="tab-invite">
              Invite
            </TabsTrigger>
            <TabsTrigger value="collaborators" data-testid="tab-collaborators">
              Collaborators
            </TabsTrigger>
            <TabsTrigger value="pending" data-testid="tab-pending">
              Pending Invitations
            </TabsTrigger>
          </TabsList>

          <TabsContent value="invite">
            <InviteTab ideaId={ideaId} isOwner={isOwner} />
          </TabsContent>

          <TabsContent value="collaborators">
            <CollaboratorsTab
              ideaId={ideaId}
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
      toast.success("Invitation sent");
      setSearchQuery("");
      setDebouncedQuery("");
      queryClient.invalidateQueries({ queryKey: ["invitations", ideaId] });
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to send invitation");
    },
  });

  return (
    <div className="space-y-4 py-2" data-testid="invite-tab">
      <Input
        placeholder="Search users by name or email..."
        value={searchQuery}
        onChange={(e) => handleSearchChange(e.target.value)}
        data-testid="invite-search-input"
      />
      {isSearching && debouncedQuery.length >= 2 && (
        <p className="text-sm text-text-secondary">Searching...</p>
      )}
      {searchResults && searchResults.length === 0 && debouncedQuery.length >= 2 && (
        <p className="text-sm text-text-secondary" data-testid="no-results">
          No users found
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
                  Invite
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
  isOwner: boolean;
  queryClient: ReturnType<typeof useQueryClient>;
  onCloseModal: () => void;
}

function CollaboratorsTab({
  ideaId,
  isOwner,
  queryClient,
  onCloseModal,
}: CollaboratorsTabProps) {
  const { user } = useAuth();
  const [transferDialogOpen, setTransferDialogOpen] = useState(false);
  const [transferTarget, setTransferTarget] = useState<CollaboratorUser | null>(null);
  const [removeTarget, setRemoveTarget] = useState<CollaboratorUser | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["collaborators", ideaId],
    queryFn: () => fetchCollaborators(ideaId),
  });

  const removeMutation = useMutation({
    mutationFn: (userId: string) => removeCollaborator(ideaId, userId),
    onSuccess: () => {
      toast.success("Collaborator removed");
      setRemoveTarget(null);
      queryClient.invalidateQueries({ queryKey: ["collaborators", ideaId] });
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to remove collaborator");
    },
  });

  const transferMutation = useMutation({
    mutationFn: (newOwnerId: string) => transferOwnership(ideaId, newOwnerId),
    onSuccess: () => {
      toast.success("Ownership transferred");
      setTransferDialogOpen(false);
      setTransferTarget(null);
      queryClient.invalidateQueries({ queryKey: ["collaborators", ideaId] });
      onCloseModal();
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to transfer ownership");
    },
  });

  if (isLoading) return <p className="py-4 text-sm text-text-secondary">Loading...</p>;

  const owner = data?.owner;
  const coOwner = data?.co_owner;
  const collaborators = data?.collaborators ?? [];

  return (
    <div className="space-y-2 py-2" data-testid="collaborators-tab">
      {/* Owner */}
      {owner && (
        <CollaboratorRow user={owner} badge="Owner" />
      )}
      {/* Co-owner */}
      {coOwner && (
        <CollaboratorRow user={coOwner} badge="Co-owner" />
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
                  Joined {formatRelativeTime(c.joined_at)}
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
                Transfer
              </Button>
              <Button
                size="sm"
                variant="destructive"
                onClick={() => setRemoveTarget(c)}
                data-testid={`remove-button-${c.id}`}
              >
                Remove
              </Button>
            </div>
          )}
        </div>
      ))}
      {collaborators.length === 0 && !coOwner && (
        <p className="py-4 text-center text-sm text-text-secondary" data-testid="no-collaborators">
          No collaborators yet
        </p>
      )}

      {/* Remove confirmation dialog */}
      {removeTarget && (
        <Dialog open={!!removeTarget} onOpenChange={() => setRemoveTarget(null)}>
          <DialogContent data-testid="remove-confirm-dialog">
            <DialogHeader>
              <DialogTitle>Remove Collaborator</DialogTitle>
              <DialogDescription>
                Are you sure you want to remove {removeTarget.display_name} from this idea?
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button variant="ghost" onClick={() => setRemoveTarget(null)}>
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={() => removeMutation.mutate(removeTarget.id)}
                disabled={removeMutation.isPending}
                data-testid="confirm-remove-button"
              >
                Remove
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
              <DialogTitle>Transfer Ownership</DialogTitle>
              <DialogDescription>
                Transfer ownership to {transferTarget.display_name}? You will become a collaborator.
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button variant="ghost" onClick={() => setTransferDialogOpen(false)}>
                Cancel
              </Button>
              <Button
                onClick={() => transferMutation.mutate(transferTarget.id)}
                disabled={transferMutation.isPending}
                data-testid="confirm-transfer-button"
              >
                Transfer
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
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["invitations", ideaId],
    queryFn: () => fetchPendingInvitations(ideaId),
    enabled: isOwner,
  });

  const revokeMutation = useMutation({
    mutationFn: (invitationId: string) => revokeInvitation(invitationId),
    onSuccess: () => {
      toast.success("Invitation revoked");
      queryClient.invalidateQueries({ queryKey: ["invitations", ideaId] });
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to revoke invitation");
    },
  });

  if (!isOwner) {
    return (
      <p className="py-4 text-center text-sm text-text-secondary" data-testid="pending-tab">
        Only the owner can view pending invitations.
      </p>
    );
  }

  if (isLoading) return <p className="py-4 text-sm text-text-secondary">Loading...</p>;

  const invitations = data?.invitations ?? [];

  return (
    <div className="space-y-2 py-2" data-testid="pending-tab">
      {invitations.length === 0 && (
        <p className="py-4 text-center text-sm text-text-secondary" data-testid="no-pending">
          No pending invitations
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
                Invited {formatRelativeTime(inv.created_at)}
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
            Revoke
          </Button>
        </div>
      ))}
    </div>
  );
}
