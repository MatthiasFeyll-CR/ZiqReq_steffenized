import { useCallback } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { Lightbulb, Users, Mail, Trash2 } from "lucide-react";
import { toast } from "react-toastify";

import { HeroSection } from "@/components/landing/HeroSection";
import { FilterBar } from "@/components/landing/FilterBar";
import { EmptyState } from "@/components/common/EmptyState";
import { ProjectCard } from "@/components/landing/ProjectCard";
import type { ProjectState } from "@/components/landing/ProjectCard";
import { InvitationCard } from "@/components/landing/InvitationCard";
import { ProjectCardSkeleton } from "@/components/landing/ProjectCardSkeleton";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { acceptInvitation, declineInvitation } from "@/api/collaboration";
import { useMyProjects } from "@/hooks/use-my-projects";
import { useCollaboratingProjects } from "@/hooks/use-collaborating-projects";
import { useInvitations } from "@/hooks/use-invitations";
import { useTrash } from "@/hooks/use-trash";
import { useDeleteProject } from "@/hooks/use-delete-project";
import { useRestoreProject } from "@/hooks/use-restore-project";
import { useProjectsFilters } from "@/hooks/use-projects-filters";
import { useLandingSync } from "@/hooks/use-landing-sync";

interface SectionProps {
  title: string;
  count: number;
  children: React.ReactNode;
}

function Section({ title, count, children }: SectionProps) {
  return (
    <section className="rounded-lg border border-border bg-surface p-4 shadow-sm dark:shadow-md dark:shadow-black/20">
      <div className="mb-3 flex items-center gap-2">
        <h2 className="text-base font-semibold text-foreground">{title}</h2>
        <span className="inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-muted px-1.5 text-xs font-medium text-text-secondary">
          {count}
        </span>
      </div>
      {children}
    </section>
  );
}

function SkeletonList() {
  return (
    <div className="flex flex-col gap-2">
      <ProjectCardSkeleton />
      <ProjectCardSkeleton />
      <ProjectCardSkeleton />
    </div>
  );
}

export default function LandingPage() {
  const { t } = useTranslation();
  const {
    filters,
    searchInput,
    setSearchInput,
    setStateFilter,
    setOwnershipFilter,
    clearFilters,
    hasActiveFilters,
  } = useProjectsFilters();

  useLandingSync();

  const showMyProjects = !filters.ownership || filters.ownership === "my_ideas";
  const showCollaborating =
    !filters.ownership || filters.ownership === "collaborating";

  const myProjects = useMyProjects(showMyProjects ? filters : undefined);
  const collaborating = useCollaboratingProjects(
    showCollaborating ? filters : undefined,
  );
  const invitations = useInvitations();
  const trash = useTrash();
  const deleteMutation = useDeleteProject();
  const restoreMutation = useRestoreProject();
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const acceptMutation = useMutation({
    mutationFn: ({ invitationId }: { invitationId: string; projectId: string }) =>
      acceptInvitation(invitationId),
    onSuccess: (_data, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: ["invitations"] });
      queryClient.invalidateQueries({ queryKey: ["collaboratingProjects"] });
      toast.success(t("landing.invitations.accepted", "Invitation accepted"));
      navigate(`/project/${projectId}`);
    },
  });

  const declineMutation = useMutation({
    mutationFn: declineInvitation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["invitations"] });
      toast.success(t("landing.invitations.declined", "Invitation declined"));
    },
  });

  const handleAccept = useCallback(
    (id: string, projectId: string) =>
      acceptMutation.mutate({ invitationId: id, projectId }),
    [acceptMutation],
  );

  const handleDecline = useCallback(
    (id: string) => declineMutation.mutate(id),
    [declineMutation],
  );

  const myProjectsData = showMyProjects ? (myProjects.data?.results ?? []) : [];
  const collaboratingData = showCollaborating
    ? (collaborating.data?.results ?? [])
    : [];
  const invitationsData = invitations.data?.invitations ?? [];
  const trashData = trash.data?.results ?? [];

  const handleDelete = useCallback(
    (id: string) => {
      deleteMutation.mutate(id, {
        onSuccess: () => {
          const toastId = toast(
            <div className="flex items-center justify-between gap-4">
              <span>{t("landing.ideaCard.deletedUndo")}</span>
              <button
                type="button"
                className="shrink-0 font-medium text-primary underline"
                onClick={() => {
                  restoreMutation.mutate(id);
                  toast.dismiss(toastId);
                }}
              >
                {t("landing.ideaCard.undo")}
              </button>
            </div>,
            { autoClose: 5000 },
          );
        },
      });
    },
    [deleteMutation, restoreMutation, t],
  );

  const handleRestore = useCallback(
    (id: string) => {
      restoreMutation.mutate(id);
    },
    [restoreMutation],
  );

  return (
      <div className="mx-auto max-w-5xl px-4 pb-12">
        <HeroSection />

        <div className="mt-6">
          <FilterBar
            searchInput={searchInput}
            onSearchChange={setSearchInput}
            stateFilter={filters.state}
            onStateChange={setStateFilter}
            ownershipFilter={filters.ownership}
            onOwnershipChange={setOwnershipFilter}
            hasActiveFilters={hasActiveFilters}
            onClear={clearFilters}
          />
        </div>

        <div className="mt-8 grid gap-8 md:grid-cols-2">
          <Section
            title={t("landing.lists.myIdeas")}
            count={myProjectsData.length}
          >
            {myProjects.isLoading ? (
              <SkeletonList />
            ) : myProjectsData.length === 0 ? (
              <EmptyState
                icon={Lightbulb}
                message={t("landing.empty.myIdeas")}
              />
            ) : (
              <div className="flex flex-col gap-2">
                {myProjectsData.map((p) => (
                  <ProjectCard
                    key={p.id}
                    id={p.id}
                    title={p.title}
                    state={p.state as ProjectState}
                    updatedAt={p.updated_at}
                    deletedAt={p.deleted_at}
                    onDelete={handleDelete}
                  />
                ))}
              </div>
            )}
          </Section>

          <Section
            title={t("landing.lists.collaborating")}
            count={collaboratingData.length}
          >
            {collaborating.isLoading ? (
              <SkeletonList />
            ) : collaboratingData.length === 0 ? (
              <EmptyState
                icon={Users}
                message={t("landing.empty.collaborating")}
              />
            ) : (
              <div className="flex flex-col gap-2">
                {collaboratingData.map((p) => (
                  <ProjectCard
                    key={p.id}
                    id={p.id}
                    title={p.title}
                    state={p.state as ProjectState}
                    updatedAt={p.updated_at}
                    deletedAt={p.deleted_at}
                    onDelete={handleDelete}
                  />
                ))}
              </div>
            )}
          </Section>

          <Section
            title={t("landing.lists.invitations")}
            count={invitationsData.length}
          >
            {invitations.isLoading ? (
              <SkeletonList />
            ) : invitationsData.length === 0 ? (
              <EmptyState
                icon={Mail}
                message={t("landing.empty.invitations")}
              />
            ) : (
              <div className="flex flex-col gap-2">
                {invitationsData.map((inv) => (
                  <InvitationCard
                    key={inv.id}
                    id={inv.id}
                    projectId={inv.project_id}
                    projectTitle={inv.project_title}
                    inviterName={inv.inviter.display_name}
                    createdAt={inv.created_at}
                    onAccept={handleAccept}
                    onDecline={handleDecline}
                  />
                ))}
              </div>
            )}
          </Section>

          <Section title={t("landing.lists.trash")} count={trashData.length}>
            {trash.isLoading ? (
              <SkeletonList />
            ) : trashData.length === 0 ? (
              <EmptyState
                icon={Trash2}
                message={t("landing.empty.trash")}
              />
            ) : (
              <div className="flex flex-col gap-2">
                {trashData.map((p) => (
                  <ProjectCard
                    key={p.id}
                    id={p.id}
                    title={p.title}
                    state={p.state as ProjectState}
                    updatedAt={p.updated_at}
                    deletedAt={p.deleted_at}
                    onRestore={handleRestore}
                  />
                ))}
              </div>
            )}
          </Section>
        </div>
      </div>
  );
}
