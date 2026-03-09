import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { Lightbulb, Users, Mail, Trash2 } from "lucide-react";
import { PageShell } from "@/components/layout/PageShell";
import { HeroSection } from "@/components/landing/HeroSection";
import { EmptyState } from "@/components/common/EmptyState";

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
}

export default function LandingPage({
  myIdeas = [],
  collaborating = [],
  invitations = [],
  trash = [],
}: LandingPageProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();

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
                  <button
                    key={idea.id}
                    className="w-full cursor-pointer rounded-lg border border-border bg-surface p-4 text-left transition-colors hover:bg-muted"
                    onClick={() => navigate(`/idea/${idea.id}`)}
                  >
                    <p className="truncate font-medium text-foreground">
                      {idea.title || t("landing.untitled")}
                    </p>
                  </button>
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
                  <button
                    key={idea.id}
                    className="w-full cursor-pointer rounded-lg border border-border bg-surface p-4 text-left transition-colors hover:bg-muted"
                    onClick={() => navigate(`/idea/${idea.id}`)}
                  >
                    <p className="truncate font-medium text-foreground">
                      {idea.title || t("landing.untitled")}
                    </p>
                  </button>
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
                  <button
                    key={inv.id}
                    className="w-full cursor-pointer rounded-lg border border-border bg-surface p-4 text-left transition-colors hover:bg-muted"
                    onClick={() => navigate(`/idea/${inv.ideaId}`)}
                  >
                    <p className="truncate font-medium text-foreground">
                      {inv.ideaTitle}
                    </p>
                    <p className="text-sm text-text-secondary">
                      {inv.inviterName}
                    </p>
                  </button>
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
                  <button
                    key={idea.id}
                    className="w-full cursor-pointer rounded-lg border border-border bg-surface p-4 text-left transition-colors hover:bg-muted"
                    onClick={() => navigate(`/idea/${idea.id}`)}
                  >
                    <p className="truncate font-medium text-foreground">
                      {idea.title || t("landing.untitled")}
                    </p>
                  </button>
                ))}
              </div>
            )}
          </Section>
        </div>
      </div>
    </PageShell>
  );
}
