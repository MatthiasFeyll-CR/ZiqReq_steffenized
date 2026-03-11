import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { ChevronDown, ChevronRight, ClipboardList, Inbox } from "lucide-react";
import { PageShell } from "@/components/layout/PageShell";
import { EmptyState } from "@/components/common/EmptyState";
import { ReviewCard } from "@/components/review/ReviewCard";
import { fetchReviews } from "@/api/review";
import type { ReviewIdea } from "@/api/review";

interface CollapsibleCategoryProps {
  title: string;
  count: number;
  defaultOpen: boolean;
  categoryKey: "assigned" | "unassigned" | "accepted" | "rejected" | "dropped";
  ideas: ReviewIdea[];
}

function CollapsibleCategory({
  title,
  count,
  defaultOpen,
  categoryKey,
  ideas,
}: CollapsibleCategoryProps) {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <section>
      <button
        type="button"
        className="mb-3 flex w-full items-center gap-2 text-left"
        onClick={() => setIsOpen((o) => !o)}
        aria-expanded={isOpen}
      >
        {isOpen ? (
          <ChevronDown className="h-4 w-4 shrink-0 text-text-secondary" />
        ) : (
          <ChevronRight className="h-4 w-4 shrink-0 text-text-secondary" />
        )}
        <h2 className="text-lg font-semibold text-foreground">{title}</h2>
        <span className="inline-flex h-6 min-w-6 items-center justify-center rounded-full bg-muted px-2 text-xs font-medium text-text-secondary">
          {count}
        </span>
      </button>
      {isOpen && (
        ideas.length === 0 ? (
          <EmptyState
            icon={Inbox}
            message={t("review.noCategoryIdeas", { category: title.toLowerCase() })}
          />
        ) : (
          <div className="flex flex-col gap-2">
            {ideas.map((idea) => (
              <ReviewCard key={idea.id} idea={idea} category={categoryKey} />
            ))}
          </div>
        )
      )}
    </section>
  );
}

export default function ReviewPage() {
  const { t } = useTranslation();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["reviews"],
    queryFn: fetchReviews,
  });

  return (
    <PageShell>
      <div className="mx-auto max-w-5xl px-4 pb-12">
        <div className="mb-8 mt-6">
          <h1 className="text-2xl font-bold text-foreground">{t("review.pageTitle")}</h1>
          <p className="mt-1 text-sm text-text-secondary">
            {t("review.pageDescription")}
          </p>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-16">
            <p className="text-text-secondary">{t("review.loadingReviews")}</p>
          </div>
        ) : isError ? (
          <EmptyState
            icon={ClipboardList}
            message={t("review.failedToLoad")}
            description={t("review.tryAgainLater")}
          />
        ) : (
          <div className="flex flex-col gap-8">
            <CollapsibleCategory
              title={t("review.assignedToMe")}
              count={data?.assigned_to_me.length ?? 0}
              defaultOpen={true}
              categoryKey="assigned"
              ideas={data?.assigned_to_me ?? []}
            />
            <CollapsibleCategory
              title={t("review.unassigned")}
              count={data?.unassigned.length ?? 0}
              defaultOpen={true}
              categoryKey="unassigned"
              ideas={data?.unassigned ?? []}
            />
            <CollapsibleCategory
              title={t("review.accepted")}
              count={data?.accepted.length ?? 0}
              defaultOpen={false}
              categoryKey="accepted"
              ideas={data?.accepted ?? []}
            />
            <CollapsibleCategory
              title={t("review.rejected")}
              count={data?.rejected.length ?? 0}
              defaultOpen={false}
              categoryKey="rejected"
              ideas={data?.rejected ?? []}
            />
            <CollapsibleCategory
              title={t("review.dropped")}
              count={data?.dropped.length ?? 0}
              defaultOpen={false}
              categoryKey="dropped"
              ideas={data?.dropped ?? []}
            />
          </div>
        )}
      </div>
    </PageShell>
  );
}
