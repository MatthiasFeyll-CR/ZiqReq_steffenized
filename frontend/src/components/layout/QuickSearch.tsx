import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import { Search, Star, Users, X } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { fetchProjects, type ProjectListItem } from "@/api/projects";
import type { ProjectState } from "@/components/landing/ProjectCard";

const STATE_LABELS: Record<string, string> = {
  open: "Open",
  in_review: "In Review",
  accepted: "Accepted",
  dropped: "Dropped",
  rejected: "Rejected",
  deleted: "Deleted",
};

const TYPE_LABELS: Record<string, string> = {
  software: "Software",
  non_software: "Non-Software",
};

interface QuickSearchProps {
  open: boolean;
  onClose: () => void;
}

export function QuickSearch({ open, onClose }: QuickSearchProps) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const [query, setQuery] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);

  // Fetch own projects and collaborating projects in parallel
  const { data: ownData, isLoading: ownLoading } = useQuery({
    queryKey: ["projects", "quick-search", "my_projects"],
    queryFn: () => fetchProjects("my_projects"),
    enabled: open,
    staleTime: 30_000,
  });

  const { data: collabData, isLoading: collabLoading } = useQuery({
    queryKey: ["projects", "quick-search", "collaborating"],
    queryFn: () => fetchProjects("collaborating"),
    enabled: open,
    staleTime: 30_000,
  });

  const isLoading = ownLoading || collabLoading;

  const ownProjects = ownData?.results ?? [];
  const collabProjects = collabData?.results ?? [];

  // Client-side filter
  const matchesQuery = useCallback(
    (p: ProjectListItem) => {
      const q = query.toLowerCase().trim();
      if (!q) return true;
      return (
        p.title.toLowerCase().includes(q) ||
        p.id.toLowerCase().includes(q) ||
        (p.state && p.state.toLowerCase().includes(q)) ||
        (p.project_type &&
          p.project_type.toLowerCase().replace("_", " ").includes(q))
      );
    },
    [query],
  );

  // Sort: highlighted first, then by updated_at descending
  const sortProjects = useCallback((list: ProjectListItem[]) => {
    return [...list].sort((a, b) => {
      if (a.is_highlighted && !b.is_highlighted) return -1;
      if (!a.is_highlighted && b.is_highlighted) return 1;
      return (
        new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
      );
    });
  }, []);

  const filteredOwn = useMemo(
    () => sortProjects(ownProjects.filter(matchesQuery)),
    [ownProjects, matchesQuery, sortProjects],
  );

  // Deduplicate collab list (exclude any that appear in own)
  const filteredCollab = useMemo(() => {
    const ownIds = new Set(ownProjects.map((p) => p.id));
    return sortProjects(
      collabProjects.filter((p) => !ownIds.has(p.id) && matchesQuery(p)),
    );
  }, [collabProjects, ownProjects, matchesQuery, sortProjects]);

  // Flat list for keyboard navigation
  const flatList = useMemo(
    () => [...filteredOwn, ...filteredCollab],
    [filteredOwn, filteredCollab],
  );

  // Reset active index when results change
  useEffect(() => {
    setActiveIndex(0);
  }, [flatList.length, query]);

  // Close on Escape via document listener (reliable regardless of focus)
  useEffect(() => {
    if (!open) return;
    function handleEscape(e: KeyboardEvent) {
      if (e.key === "Escape") {
        e.preventDefault();
        onClose();
      }
    }
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [open, onClose]);

  // Focus input when opened
  useEffect(() => {
    if (open) {
      setQuery("");
      setActiveIndex(0);
      requestAnimationFrame(() => {
        inputRef.current?.focus();
      });
    }
  }, [open]);

  // Scroll active item into view
  useEffect(() => {
    if (!listRef.current) return;
    const activeEl = listRef.current.querySelector(
      `[data-index="${activeIndex}"]`,
    );
    activeEl?.scrollIntoView({ block: "nearest" });
  }, [activeIndex]);

  const handleSelect = useCallback(
    (project: ProjectListItem) => {
      onClose();
      navigate(`/project/${project.id}`);
    },
    [navigate, onClose],
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      const isDown = e.key === "ArrowDown" || (e.altKey && e.key === "j");
      const isUp = e.key === "ArrowUp" || (e.altKey && e.key === "k");

      if (isDown) {
        e.preventDefault();
        setActiveIndex((prev) =>
          prev < flatList.length - 1 ? prev + 1 : prev,
        );
      } else if (isUp) {
        e.preventDefault();
        setActiveIndex((prev) => (prev > 0 ? prev - 1 : 0));
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (flatList[activeIndex]) {
          handleSelect(flatList[activeIndex]);
        }
      }
    },
    [flatList, activeIndex, handleSelect],
  );

  if (!open) return null;

  // Running index for keyboard navigation across both sections
  let runningIndex = 0;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden
      />

      {/* Panel */}
      <div
        className="relative z-10 w-full max-w-lg rounded-xl border border-border bg-surface shadow-2xl dark:shadow-black/60"
        role="combobox"
        aria-expanded={open}
        aria-haspopup="listbox"
        aria-label={t("quickSearch.title", "Quick Search")}
        onKeyDown={handleKeyDown}
      >
        {/* Search input */}
        <div className="flex items-center gap-3 border-b border-border px-4 py-3">
          <Search className="h-5 w-5 shrink-0 text-muted-foreground" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t(
              "quickSearch.placeholder",
              "Search projects by title, ID, or type...",
            )}
            className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground outline-none"
            aria-label={t(
              "quickSearch.placeholder",
              "Search projects by title, ID, or type...",
            )}
            autoComplete="off"
          />
          {query && (
            <button
              type="button"
              onClick={() => setQuery("")}
              className="shrink-0 rounded-md p-1 text-muted-foreground hover:text-foreground transition-colors"
              aria-label={t("landing.filter.clearSearch")}
            >
              <X className="h-4 w-4" />
            </button>
          )}
          <kbd className="hidden sm:inline-flex shrink-0 items-center rounded border border-border bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
            ESC
          </kbd>
        </div>

        {/* Results list */}
        <div ref={listRef} className="max-h-80 overflow-y-auto py-1" role="listbox">
          {isLoading && (
            <p className="px-4 py-6 text-center text-sm text-muted-foreground">
              {t("common.loading")}
            </p>
          )}

          {!isLoading && flatList.length === 0 && (
            <p className="px-4 py-6 text-center text-sm text-muted-foreground">
              {query
                ? t("common.noResults")
                : t("quickSearch.hint", "Start typing to search...")}
            </p>
          )}

          {!isLoading && filteredOwn.length > 0 && (
            <>
              <SectionHeader label={t("quickSearch.myProjects", "My Projects")} />
              {filteredOwn.map((project) => {
                const idx = runningIndex++;
                return (
                  <ResultItem
                    key={project.id}
                    project={project}
                    index={idx}
                    isActive={idx === activeIndex}
                    onSelect={handleSelect}
                    onHover={setActiveIndex}
                  />
                );
              })}
            </>
          )}

          {!isLoading && filteredCollab.length > 0 && (
            <>
              <SectionHeader
                label={t("quickSearch.collaborating", "Collaborating")}
                icon={<Users className="h-3 w-3" />}
              />
              {filteredCollab.map((project) => {
                const idx = runningIndex++;
                return (
                  <ResultItem
                    key={project.id}
                    project={project}
                    index={idx}
                    isActive={idx === activeIndex}
                    onSelect={handleSelect}
                    onHover={setActiveIndex}
                    showOwner
                  />
                );
              })}
            </>
          )}
        </div>

        {/* Footer hint */}
        <div className="border-t border-border px-4 py-2 flex items-center gap-4 text-[11px] text-muted-foreground">
          <span className="flex items-center gap-1">
            <kbd className="rounded border border-border bg-muted px-1 py-0.5 text-[10px]">
              &uarr;
            </kbd>
            <kbd className="rounded border border-border bg-muted px-1 py-0.5 text-[10px]">
              &darr;
            </kbd>
            <kbd className="rounded border border-border bg-muted px-1 py-0.5 text-[10px]">
              alt+j/k
            </kbd>
            {t("quickSearch.navigate", "navigate")}
          </span>
          <span className="flex items-center gap-1">
            <kbd className="rounded border border-border bg-muted px-1 py-0.5 text-[10px]">
              &crarr;
            </kbd>
            {t("quickSearch.open", "open")}
          </span>
          <span className="flex items-center gap-1">
            <kbd className="rounded border border-border bg-muted px-1 py-0.5 text-[10px]">
              esc
            </kbd>
            {t("quickSearch.close", "close")}
          </span>
        </div>
      </div>
    </div>
  );
}

function SectionHeader({
  label,
  icon,
}: {
  label: string;
  icon?: React.ReactNode;
}) {
  return (
    <div className="flex items-center gap-2 px-4 pt-2.5 pb-1">
      {icon && <span className="text-muted-foreground">{icon}</span>}
      <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
        {label}
      </span>
      <div className="flex-1 border-t border-border" />
    </div>
  );
}

function ResultItem({
  project,
  index,
  isActive,
  onSelect,
  onHover,
  showOwner,
}: {
  project: ProjectListItem;
  index: number;
  isActive: boolean;
  onSelect: (p: ProjectListItem) => void;
  onHover: (i: number) => void;
  showOwner?: boolean;
}) {
  const { t } = useTranslation();
  return (
    <button
      type="button"
      data-index={index}
      role="option"
      aria-selected={isActive}
      className={`flex w-full items-center gap-3 px-4 py-2.5 text-left transition-colors ${
        isActive ? "bg-primary/10 dark:bg-primary/15" : "hover:bg-muted"
      }`}
      onClick={() => onSelect(project)}
      onMouseEnter={() => onHover(index)}
    >
      {/* Title + subtitle */}
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-foreground">
          {project.title || t("landing.untitled")}
        </p>
        <p className="truncate text-xs text-muted-foreground">
          <span className="font-mono">{project.id.slice(0, 8)}</span>
          {showOwner && project.owner && (
            <span>
              {" \u00b7 "}
              {project.owner.display_name}
            </span>
          )}
        </p>
      </div>

      {/* Labels */}
      <div className="flex items-center gap-1.5 shrink-0">
        {project.is_highlighted && (
          <Star className="h-3.5 w-3.5 fill-yellow-400 text-yellow-400 shrink-0" />
        )}
        <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
          {TYPE_LABELS[project.project_type] ?? project.project_type}
        </span>
        <Badge
          variant={project.state as ProjectState}
          className="text-[10px] px-1.5 py-0"
        >
          {STATE_LABELS[project.state] ?? project.state}
        </Badge>
      </div>
    </button>
  );
}
