import { useState, useEffect, useCallback } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { Search, ChevronLeft, ChevronRight, X, ExternalLink } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { fetchAdminProjects, type AdminProject } from "@/api/admin";

const PROJECT_STATES = ["open", "in_review", "accepted", "dropped", "rejected"] as const;
const PAGE_SIZE = 15;

export function ProjectsTab() {
  const { t } = useTranslation();
  const [projects, setProjects] = useState<AdminProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [stateFilter, setStateFilter] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(searchQuery), 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const loadProjects = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchAdminProjects({
        page,
        page_size: PAGE_SIZE,
        state: stateFilter || undefined,
        search: debouncedSearch || undefined,
      });
      setProjects(data.results);
      setTotalCount(data.count);
    } catch (err) {
      toast.error(`${t("admin.projects.failedLoad")}: ${(err as Error).message}`);
    } finally {
      setLoading(false);
    }
  }, [page, stateFilter, debouncedSearch, t]);

  useEffect(() => {
    void loadProjects();
  }, [loadProjects]);

  // Reset page when filters change
  useEffect(() => {
    setPage(1);
  }, [stateFilter, debouncedSearch]);

  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE));

  return (
    <div className="space-y-4 py-6">
      {/* Filters */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t("admin.projects.searchPlaceholder")}
            className="pl-9 pr-8"
            data-testid="admin-projects-search"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => setSearchQuery("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
        <Select
          value={stateFilter}
          onValueChange={(val) => setStateFilter(val === "all" ? "" : val)}
        >
          <SelectTrigger className="w-full sm:w-44" data-testid="admin-projects-state-filter">
            <SelectValue placeholder={t("admin.projects.allStates")} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">{t("admin.projects.allStates")}</SelectItem>
            {PROJECT_STATES.map((state) => (
              <SelectItem key={state} value={state}>
                {t(`review.stateLabels.${state}`)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <span className="text-sm text-muted-foreground whitespace-nowrap">
          {t("admin.projects.totalCount", { count: totalCount })}
        </span>
      </div>

      {/* Projects list */}
      {loading ? (
        <p className="text-sm text-muted-foreground py-8 text-center">
          {t("common.loading")}
        </p>
      ) : projects.length === 0 ? (
        <p className="text-sm text-muted-foreground py-8 text-center">
          {t("common.noResults")}
        </p>
      ) : (
        <div className="space-y-2">
          {projects.map((p) => (
            <ProjectRow key={p.id} project={p} />
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            {t("common.back")}
          </Button>
          <span className="text-sm text-muted-foreground">
            {page} / {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages}
          >
            {t("admin.projects.next")}
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      )}
    </div>
  );
}

function ProjectRow({ project }: { project: AdminProject }) {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const stateVariant = project.state as "open" | "in_review" | "accepted" | "dropped" | "rejected";

  return (
    <div
      className="flex flex-col gap-2 rounded-lg border border-border bg-card p-4 transition-colors hover:bg-accent/30 cursor-pointer group"
      data-testid={`admin-project-row-${project.id}`}
      onClick={() => navigate(`/project/${project.id}`)}
      role="link"
      tabIndex={0}
      onKeyDown={(e) => { if (e.key === "Enter") navigate(`/project/${project.id}`); }}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <h4 className="text-sm font-medium truncate group-hover:text-primary transition-colors">
              {project.title || t("landing.untitled")}
            </h4>
            <Badge variant={stateVariant} className="flex-shrink-0">
              {t(`review.stateLabels.${project.state}`)}
            </Badge>
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">
            {project.owner.display_name}
            <span className="mx-1.5">&middot;</span>
            {new Date(project.updated_at).toLocaleDateString()}
          </p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <code className="text-[10px] text-muted-foreground font-mono hidden sm:block">
            {project.id.slice(0, 8)}
          </code>
          <ExternalLink className="h-3.5 w-3.5 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>
      </div>

      {project.keywords && project.keywords.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {project.keywords.map((kw) => (
            <span
              key={kw}
              className="inline-flex items-center rounded-md bg-muted px-2 py-0.5 text-[11px] font-medium text-muted-foreground"
            >
              {kw}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
