import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Code, Compass, Package, Search, X, ChevronLeft, ChevronRight, Users } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/common/EmptyState";
import { useExploreProjects } from "@/hooks/use-explore-projects";
import { formatRelativeTime } from "@/lib/utils";
import type { ProjectListItem } from "@/api/projects";

const STATE_TABS = [
  { value: "", labelKey: "explore.tabs.all" },
  { value: "open", labelKey: "explore.tabs.open" },
  { value: "in_review", labelKey: "explore.tabs.inReview" },
  { value: "accepted", labelKey: "explore.tabs.accepted" },
  { value: "dropped", labelKey: "explore.tabs.dropped" },
  { value: "rejected", labelKey: "explore.tabs.rejected" },
] as const;

const STATE_LABELS: Record<string, string> = {
  open: "Open",
  in_review: "In Review",
  accepted: "Accepted",
  dropped: "Dropped",
  rejected: "Rejected",
};

const PAGE_SIZE = 20;

export default function ExplorePage() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const [stateFilter, setStateFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [page, setPage] = useState(1);

  // Debounce search input (400ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchInput);
      setPage(1);
    }, 400);
    return () => clearTimeout(timer);
  }, [searchInput]);

  // Reset page when filters change
  const handleStateChange = useCallback((value: string) => {
    setStateFilter(value);
    setPage(1);
  }, []);
  const handleTypeChange = useCallback((value: string) => {
    setTypeFilter(value === "__all__" ? "" : value);
    setPage(1);
  }, []);

  const { data, isLoading, isFetching } = useExploreProjects({
    search: debouncedSearch,
    state: stateFilter,
    projectType: typeFilter,
    page,
  });

  const projects = data?.results ?? [];
  const totalCount = data?.count ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE));
  const hasNext = data?.next != null;
  const hasPrev = page > 1;

  return (
    <div className="mx-auto max-w-6xl px-4 pb-12">
      {/* Header */}
      <div className="mt-8 mb-6">
        <div className="flex items-center gap-3">
          <Compass className="h-7 w-7 text-primary" />
          <h1 className="text-2xl font-bold text-foreground">
            {t("explore.title", "Explore Projects")}
          </h1>
          {!isLoading && (
            <span className="inline-flex h-6 min-w-6 items-center justify-center rounded-full bg-muted px-2 text-xs font-medium text-text-secondary">
              {totalCount}
            </span>
          )}
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          {t("explore.subtitle", "Discover and browse all projects across the organization.")}
        </p>
      </div>

      {/* Filters row */}
      <div className="flex flex-wrap items-center gap-3 rounded-lg border border-border bg-surface p-3 shadow-sm dark:shadow-md dark:shadow-black/20">
        <div className="relative min-w-48 flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-secondary" />
          <Input
            type="text"
            placeholder={t("explore.searchPlaceholder", "Search projects by title...")}
            aria-label={t("explore.searchPlaceholder", "Search projects by title...")}
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            className="pl-9 pr-9"
            data-testid="explore-search"
          />
          {searchInput && (
            <button
              type="button"
              onClick={() => setSearchInput("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-text-secondary hover:text-foreground"
              aria-label={t("landing.filter.clearSearch")}
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        <Select
          value={typeFilter || "__all__"}
          onValueChange={handleTypeChange}
        >
          <SelectTrigger className="w-44" data-testid="explore-type-filter">
            <SelectValue placeholder={t("explore.typePlaceholder", "Project Type")} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="__all__">{t("explore.typeAll", "All Types")}</SelectItem>
            <SelectItem value="software">
              <span className="flex items-center gap-2">
                <Code className="h-3.5 w-3.5" />
                {t("projectType.software")}
              </span>
            </SelectItem>
            <SelectItem value="non_software">
              <span className="flex items-center gap-2">
                <Package className="h-3.5 w-3.5" />
                {t("projectType.nonSoftware")}
              </span>
            </SelectItem>
          </SelectContent>
        </Select>

        {(searchInput || typeFilter) && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setSearchInput("");
              setTypeFilter("");
            }}
          >
            {t("landing.filter.clearAll")}
          </Button>
        )}
      </div>

      {/* State tabs */}
      <Tabs
        value={stateFilter}
        onValueChange={handleStateChange}
        className="mt-4"
      >
        <TabsList className="w-full justify-start" data-testid="explore-state-tabs">
          {STATE_TABS.map((tab) => (
            <TabsTrigger key={tab.value} value={tab.value}>
              {t(tab.labelKey)}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      {/* Loading indicator for refetch */}
      {isFetching && !isLoading && (
        <div className="mt-2 h-0.5 w-full overflow-hidden rounded-full bg-muted">
          <div className="h-full w-1/3 animate-pulse rounded-full bg-primary" />
        </div>
      )}

      {/* Content */}
      <div className="mt-4">
        {isLoading ? (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <ExploreCardSkeleton key={i} />
            ))}
          </div>
        ) : projects.length === 0 ? (
          <EmptyState
            icon={Compass}
            message={t("explore.empty", "No projects found")}
            description={
              debouncedSearch || stateFilter || typeFilter
                ? t("explore.emptyFiltered", "Try adjusting your filters or search term.")
                : t("explore.emptyAll", "There are no projects in the organization yet.")
            }
          />
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {projects.map((project) => (
              <ExploreCard
                key={project.id}
                project={project}
                onClick={() => navigate(`/project/${project.id}`)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-6 flex items-center justify-center gap-3">
          <Button
            variant="outline"
            size="sm"
            disabled={!hasPrev}
            onClick={() => setPage((p) => p - 1)}
            data-testid="explore-prev"
          >
            <ChevronLeft className="mr-1 h-4 w-4" />
            {t("explore.prev", "Previous")}
          </Button>
          <span className="text-sm text-muted-foreground">
            {t("explore.pageInfo", "Page {{current}} of {{total}}", {
              current: page,
              total: totalPages,
            })}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={!hasNext}
            onClick={() => setPage((p) => p + 1)}
            data-testid="explore-next"
          >
            {t("explore.next", "Next")}
            <ChevronRight className="ml-1 h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
}

function ExploreCard({
  project,
  onClick,
}: {
  project: ProjectListItem;
  onClick: () => void;
}) {
  const { t } = useTranslation();
  const TypeIcon = project.project_type === "software" ? Code : Package;
  const typeLabelKey = project.project_type === "software" ? "projectType.software" : "projectType.nonSoftware";

  return (
    <button
      type="button"
      className="flex flex-col gap-3 rounded-lg border border-border bg-surface p-4 text-left transition-colors hover:bg-muted/60 hover:border-primary/30 cursor-pointer shadow-sm dark:shadow-md dark:shadow-black/20"
      onClick={onClick}
      data-testid="explore-card"
    >
      {/* Top row: type icon + title */}
      <div className="flex items-start gap-2.5">
        <TooltipProvider delayDuration={300}>
          <Tooltip>
            <TooltipTrigger asChild>
              <span className="mt-0.5 shrink-0 flex items-center justify-center rounded-md bg-primary/10 p-1.5 text-primary">
                <TypeIcon className="h-4 w-4" />
              </span>
            </TooltipTrigger>
            <TooltipContent>
              <p>{t(typeLabelKey)}</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-semibold text-foreground">
            {project.title || t("landing.untitled")}
          </p>
          <p className="truncate text-xs text-muted-foreground mt-0.5">
            {project.owner?.display_name || t("explore.unknownOwner", "Unknown")}
          </p>
        </div>
      </div>

      {/* Bottom row: badge + meta */}
      <div className="flex items-center gap-2">
        <Badge
          variant={project.state as "open" | "in_review" | "accepted" | "dropped" | "rejected"}
          className="shrink-0"
        >
          {STATE_LABELS[project.state] || project.state}
        </Badge>
        {project.collaborator_count > 0 && (
          <span className="flex items-center gap-1 text-xs text-muted-foreground">
            <Users className="h-3 w-3" />
            {project.collaborator_count}
          </span>
        )}
        <span className="ml-auto text-xs text-muted-foreground">
          {formatRelativeTime(project.updated_at)}
        </span>
      </div>
    </button>
  );
}

function ExploreCardSkeleton() {
  return (
    <div className="flex flex-col gap-3 rounded-lg border border-border bg-surface p-4 shadow-sm dark:shadow-md dark:shadow-black/20">
      <div className="flex items-start gap-2.5">
        <Skeleton className="h-7 w-7 rounded-md" />
        <div className="flex-1 space-y-1.5">
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-3 w-1/2" />
        </div>
      </div>
      <div className="flex items-center gap-2">
        <Skeleton className="h-5 w-16 rounded-full" />
        <Skeleton className="ml-auto h-3 w-20" />
      </div>
    </div>
  );
}
