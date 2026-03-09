import { useTranslation } from "react-i18next";
import { Lightbulb, Users, Mail, Trash2 } from "lucide-react";
import { PageShell } from "@/components/layout/PageShell";
import { HeroSection } from "@/components/landing/HeroSection";
import { EmptyState } from "@/components/common/EmptyState";
import { IdeaCard } from "@/components/landing/IdeaCard";
import type { IdeaState } from "@/components/landing/IdeaCard";
import { InvitationCard } from "@/components/landing/InvitationCard";

interface IdeaListItem {
  id: string;
  title: string;
  state: string;
  updatedAt: string;
  deletedAt?: string | null;
}

interface InvitationListItem {
  id: string;
  ideaId: string;
  ideaTitle: string;
  inviterName: string;
  createdAt: string;
}

interface SectionProps {
  title: string;
  count: number;
  children: React.ReactNode;
}

function Section({ title, count, children }: SectionProps) {
  return (
    <section>
      <div className="mb-3 flex items-center gap-2">
        <h2 className="text-lg font-semibold text-foreground">{title}</h2>
        <span className="inline-flex h-6 min-w-6 items-center justify-center rounded-full bg-muted px-2 text-xs font-medium text-text-secondary">
          {count}
        </span>
      </div>
      {children}
    </section>
  );
}

export interface LandingPageProps {
  myIdeas?: IdeaListItem[];
  collaborating?: IdeaListItem[];
  invitations?: InvitationListItem[];
  trash?: IdeaListItem[];
  onDeleteIdea?: (id: string) => void;
  onRestoreIdea?: (id: string) => void;
}

export default function LandingPage({
  myIdeas = [],
  collaborating = [],
  invitations = [],
  trash = [],
  onDeleteIdea,
  onRestoreIdea,
}: LandingPageProps) {
  const { t } = useTranslation();

  return (
    <PageShell>
      <div className="mx-auto max-w-5xl px-4 pb-12">
        <HeroSection />

        <div className="mt-8 grid gap-8 md:grid-cols-2">
          <Section title={t("landing.lists.myIdeas")} count={myIdeas.length}>
            {myIdeas.length === 0 ? (
              <EmptyState
                icon={Lightbulb}
                message={t("landing.empty.myIdeas")}
              />
            ) : (
              <div className="flex flex-col gap-2">
                {myIdeas.map((idea) => (
                  <IdeaCard
                    key={idea.id}
                    id={idea.id}
                    title={idea.title}
                    state={idea.state as IdeaState}
                    updatedAt={idea.updatedAt}
                    deletedAt={idea.deletedAt}
                    onDelete={onDeleteIdea}
                  />
                ))}
              </div>
            )}
          </Section>

          <Section
            title={t("landing.lists.collaborating")}
            count={collaborating.length}
          >
            {collaborating.length === 0 ? (
              <EmptyState
                icon={Users}
                message={t("landing.empty.collaborating")}
              />
            ) : (
              <div className="flex flex-col gap-2">
                {collaborating.map((idea) => (
                  <IdeaCard
                    key={idea.id}
                    id={idea.id}
                    title={idea.title}
                    state={idea.state as IdeaState}
                    updatedAt={idea.updatedAt}
                    deletedAt={idea.deletedAt}
                    onDelete={onDeleteIdea}
                  />
                ))}
              </div>
            )}
          </Section>

          <Section
            title={t("landing.lists.invitations")}
            count={invitations.length}
          >
            {invitations.length === 0 ? (
              <EmptyState
                icon={Mail}
                message={t("landing.empty.invitations")}
              />
            ) : (
              <div className="flex flex-col gap-2">
                {invitations.map((inv) => (
                  <InvitationCard
                    key={inv.id}
                    id={inv.id}
                    ideaId={inv.ideaId}
                    ideaTitle={inv.ideaTitle}
                    inviterName={inv.inviterName}
                    createdAt={inv.createdAt}
                  />
                ))}
              </div>
            )}
          </Section>

          <Section title={t("landing.lists.trash")} count={trash.length}>
            {trash.length === 0 ? (
              <EmptyState
                icon={Trash2}
                message={t("landing.empty.trash")}
              />
            ) : (
              <div className="flex flex-col gap-2">
                {trash.map((idea) => (
                  <IdeaCard
                    key={idea.id}
                    id={idea.id}
                    title={idea.title}
                    state={idea.state as IdeaState}
                    updatedAt={idea.updatedAt}
                    deletedAt={idea.deletedAt}
                    onRestore={onRestoreIdea}
                  />
                ))}
              </div>
            )}
          </Section>
        </div>
      </div>
    </PageShell>
  );
}
