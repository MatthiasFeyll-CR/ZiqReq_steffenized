import { useCallback, useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-toastify";
import { useTranslation } from "react-i18next";
import { Check, Copy, Link, Users } from "lucide-react";
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
  sendBulkInvitations,
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
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const isOwner = user?.id === ownerId;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl flex flex-col" data-testid="collaborator-modal">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            {t("collaboration.manageTitle")}
          </DialogTitle>
          <DialogDescription>
            {t("collaboration.manageDescription")}
          </DialogDescription>
        </DialogHeader>
        <Tabs defaultValue="invite" className="flex flex-col min-h-0 flex-1" data-testid="collaborator-tabs">
          <TabsList className="w-full shrink-0">
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

          <TabsContent value="invite" className="overflow-visible">
            <InviteTab ideaId={ideaId} onClose={() => onOpenChange(false)} />
          </TabsContent>

          <TabsContent value="collaborators" className="overflow-y-auto">
            <CollaboratorsTab
              ideaId={ideaId}
              ownerId={ownerId}
              isOwner={isOwner}
              queryClient={queryClient}
              onCloseModal={() => onOpenChange(false)}
            />
          </TabsContent>

          <TabsContent value="pending" className="overflow-y-auto">
            <PendingTab ideaId={ideaId} isOwner={isOwner} onClose={() => onOpenChange(false)} />
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}

/* ---------- Invite Tab ---------- */

function InviteTab({ ideaId, onClose }: { ideaId: string; onClose: () => void }) {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [selectedUsers, setSelectedUsers] = useState<UserSearchResult[]>([]);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const [copied, setCopied] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined);
  const listRef = useRef<HTMLUListElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSearchChange = useCallback((value: string) => {
    setSearchQuery(value);
    setHighlightedIndex(-1);
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

  // Filter out already-selected users from results
  const filteredResults = searchResults?.filter(
    (u) => !selectedUsers.some((s) => s.id === u.id)
  );

  const selectUser = useCallback((user: UserSearchResult) => {
    setSelectedUsers((prev) => {
      if (prev.some((u) => u.id === user.id)) return prev;
      return [...prev, user];
    });
    setSearchQuery("");
    setDebouncedQuery("");
    setHighlightedIndex(-1);
    inputRef.current?.focus();
  }, []);

  const removeSelectedUser = useCallback((userId: string) => {
    setSelectedUsers((prev) => prev.filter((u) => u.id !== userId));
  }, []);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      const results = filteredResults ?? [];
      if (results.length === 0) return;

      if (e.key === "ArrowDown") {
        e.preventDefault();
        setHighlightedIndex((prev) =>
          prev < results.length - 1 ? prev + 1 : 0
        );
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setHighlightedIndex((prev) =>
          prev > 0 ? prev - 1 : results.length - 1
        );
      } else if (e.key === "Enter" && highlightedIndex >= 0) {
        e.preventDefault();
        const target = results[highlightedIndex];
        if (target) selectUser(target);
      }
    },
    [filteredResults, highlightedIndex, selectUser]
  );

  // Scroll highlighted item into view
  useEffect(() => {
    if (highlightedIndex < 0 || !listRef.current) return;
    const items = listRef.current.querySelectorAll("[data-result-item]");
    items[highlightedIndex]?.scrollIntoView({ block: "nearest" });
  }, [highlightedIndex]);

  const bulkInviteMutation = useMutation({
    mutationFn: (inviteeIds: string[]) =>
      sendBulkInvitations(ideaId, inviteeIds),
    onSuccess: (data) => {
      const sentCount = data.results.filter((r) => r.status === "pending").length;
      toast.success(t("collaboration.invitationsSent", { count: sentCount }));
      setSelectedUsers([]);
      setSearchQuery("");
      setDebouncedQuery("");
      queryClient.invalidateQueries({ queryKey: ["invitations", ideaId] });
      onClose();
    },
    onError: (error: Error) => {
      toast.error(error.message || t("collaboration.failedToInvite"));
    },
  });

  const ideaUrl = `${window.location.origin}/idea/${ideaId}`;

  const handleCopyLink = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(ideaUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      const textarea = document.createElement("textarea");
      textarea.value = ideaUrl;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }, [ideaUrl]);

  const handleInviteSelected = useCallback(() => {
    if (selectedUsers.length === 0) return;
    bulkInviteMutation.mutate(selectedUsers.map((u) => u.id));
  }, [selectedUsers, bulkInviteMutation]);

  return (
    <div
      className="space-y-4 py-2"
      data-testid="invite-tab"
      onKeyDown={(e) => {
        if (e.key === "Enter" && !e.defaultPrevented) {
          e.preventDefault();
          handleInviteSelected();
        }
      }}
    >
      {/* Selected users chips */}
      {selectedUsers.length > 0 && (
        <div className="flex flex-wrap gap-1.5" data-testid="selected-users">
          {selectedUsers.map((u) => (
            <Badge
              key={u.id}
              className="flex items-center gap-1 pr-1"
            >
              {u.display_name}
              <button
                type="button"
                className="ml-0.5 rounded-full hover:bg-white/20 p-0.5"
                onClick={() => removeSelectedUser(u.id)}
                aria-label={`Remove ${u.display_name}`}
              >
                &times;
              </button>
            </Badge>
          ))}
          <span className="text-xs text-muted-foreground self-center ml-1">
            {t("collaboration.selectedUsers", { count: selectedUsers.length })}
          </span>
        </div>
      )}

      {/* Search input */}
      <div className="relative">
        <Input
          ref={inputRef}
          placeholder={t("collaboration.searchPlaceholder")}
          aria-label={t("collaboration.searchPlaceholder")}
          value={searchQuery}
          onChange={(e) => handleSearchChange(e.target.value)}
          onKeyDown={handleKeyDown}
          data-testid="invite-search-input"
          role="combobox"
          aria-expanded={!!filteredResults && filteredResults.length > 0}
          aria-activedescendant={
            highlightedIndex >= 0
              ? `search-result-option-${highlightedIndex}`
              : undefined
          }
        />
        {isSearching && debouncedQuery.length >= 2 && (
          <p className="text-sm text-text-secondary mt-1">{t("common.searching")}</p>
        )}

        {/* Search results dropdown */}
        {filteredResults && filteredResults.length > 0 && (
          <ul
            ref={listRef}
            className="absolute z-10 left-0 right-0 top-full mt-1 max-h-48 overflow-y-auto rounded-md border border-border bg-surface shadow-md"
            role="listbox"
            data-testid="search-results"
          >
            {filteredResults.map((u: UserSearchResult, index: number) => (
              <li
                key={u.id}
                id={`search-result-option-${index}`}
                role="option"
                aria-selected={index === highlightedIndex}
                data-result-item
                className={`flex items-center gap-3 px-3 py-2 cursor-pointer transition-colors ${
                  index === highlightedIndex
                    ? "bg-primary/10 text-foreground"
                    : "hover:bg-muted"
                }`}
                onClick={() => selectUser(u)}
                data-testid={`search-result-${u.id}`}
              >
                <Avatar size="sm">
                  <AvatarFallback userId={u.id}>
                    {u.display_name.charAt(0).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium truncate text-foreground">{u.display_name}</p>
                  <p className="text-xs text-text-secondary truncate">{u.email}</p>
                </div>
              </li>
            ))}
          </ul>
        )}
        {filteredResults && filteredResults.length === 0 && debouncedQuery.length >= 2 && !isSearching && (
          <p className="text-sm text-text-secondary mt-1" data-testid="no-results">
            {t("collaboration.noUsersFound")}
          </p>
        )}
      </div>

      {/* Share link + copy */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Link className="h-4 w-4 shrink-0" />
        <span className="truncate select-all">{ideaUrl}</span>
        <TooltipProvider delayDuration={0}>
          <Tooltip open={copied}>
            <TooltipTrigger asChild>
              <button
                type="button"
                className="shrink-0 rounded p-0.5 hover:text-foreground transition-colors"
                onClick={handleCopyLink}
                data-testid="copy-link-button"
                aria-label={t("collaboration.copyLink")}
              >
                {copied ? (
                  <Check className="h-4 w-4 text-green-500" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </button>
            </TooltipTrigger>
            <TooltipContent>
              {t("collaboration.copied")}
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>
      <p className="text-sm text-muted-foreground -mt-2">
        {t("collaboration.shareLinkDescription")}
      </p>

      {/* Footer buttons */}
      <DialogFooter>
        <Button variant="ghost" onClick={onClose}>
          {t("common.back")}
        </Button>
        <Button
          onClick={handleInviteSelected}
          disabled={selectedUsers.length === 0 || bulkInviteMutation.isPending}
          data-testid="invite-selected-button"
        >
          {selectedUsers.length > 0
            ? t("collaboration.inviteSelected", { count: selectedUsers.length })
            : t("collaboration.invite")}
        </Button>
      </DialogFooter>
    </div>
  );
}

/* ---------- Collaborators Tab ---------- */

interface CollaboratorsTabProps {
  ideaId: string;
  ownerId: string;
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
  const { t } = useTranslation();
  const [transferDialogOpen, setTransferDialogOpen] = useState(false);
  const [transferTarget, setTransferTarget] = useState<CollaboratorUser | null>(null);
  const [removeTarget, setRemoveTarget] = useState<CollaboratorUser | null>(null);

  const isSingleOwner = isOwner;

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
      onCloseModal();
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
  const collaborators = data?.collaborators ?? [];

  return (
    <div className="space-y-2 py-2" data-testid="collaborators-tab">
      {/* Owner */}
      {owner && (
        <CollaboratorRow user={owner} badge={t("collaboration.owner")} />
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
      {collaborators.length === 0 && (
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

      <DialogFooter>
        <Button variant="ghost" onClick={onCloseModal}>
          {t("common.back")}
        </Button>
      </DialogFooter>

      {/* Remove confirmation dialog */}
      {removeTarget && (
        <Dialog open={!!removeTarget} onOpenChange={() => setRemoveTarget(null)}>
          <DialogContent
            data-testid="remove-confirm-dialog"
            onKeyDown={(e: React.KeyboardEvent) => {
              if (e.key === "Enter") {
                e.preventDefault();
                removeMutation.mutate(removeTarget.id);
              }
            }}
          >
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
          <DialogContent
            data-testid="transfer-confirm-dialog"
            onKeyDown={(e: React.KeyboardEvent) => {
              if (e.key === "Enter") {
                e.preventDefault();
                transferMutation.mutate(transferTarget.id);
              }
            }}
          >
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

function PendingTab({ ideaId, isOwner, onClose }: { ideaId: string; isOwner: boolean; onClose: () => void }) {
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
      onClose();
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
      <DialogFooter>
        <Button variant="ghost" onClick={onClose}>
          {t("common.back")}
        </Button>
      </DialogFooter>
    </div>
  );
}
