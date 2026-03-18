import { useState, useEffect, useCallback } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "react-toastify";
import {
  Search,
  ChevronLeft,
  ChevronRight,
  X,
  ExternalLink,
  Trash2,
  FileText,
  Image,
  File,
  RotateCcw,
} from "lucide-react";
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
import { KPICard } from "@/components/admin/KPICard";
import {
  fetchAdminAttachments,
  deleteAdminAttachment,
  restoreAdminAttachment,
  type AdminAttachment,
} from "@/api/admin";
import { env } from "@/config/env";
import { cn } from "@/lib/utils";

const PAGE_SIZE = 35;

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
}

function getFileIcon(contentType: string) {
  if (contentType === "application/pdf") return FileText;
  if (contentType.startsWith("image/")) return Image;
  return File;
}

export function AttachmentsTab() {
  const { t } = useTranslation();
  const [attachments, setAttachments] = useState<AdminAttachment[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const [stats, setStats] = useState({ total_size_bytes: 0, total_count: 0 });
  const [page, setPage] = useState(1);
  const [filterValue, setFilterValue] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(searchQuery), 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const loadAttachments = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchAdminAttachments({
        page,
        page_size: PAGE_SIZE,
        filter: filterValue as "active" | "deleted" | "all",
        search: debouncedSearch || undefined,
      });
      setAttachments(data.results);
      setTotalCount(data.count);
      setStats(data.stats);
    } catch (err) {
      toast.error(`${t("admin.attachments.failedLoad")}: ${(err as Error).message}`);
    } finally {
      setLoading(false);
    }
  }, [page, filterValue, debouncedSearch, t]);

  useEffect(() => {
    void loadAttachments();
  }, [loadAttachments]);

  // Reset page when filters change
  useEffect(() => {
    setPage(1);
  }, [filterValue, debouncedSearch]);

  const handleDelete = useCallback(
    async (id: string) => {
      try {
        await deleteAdminAttachment(id);
        toast.success(t("admin.attachments.deleteSuccess"));
        setConfirmDeleteId(null);
        void loadAttachments();
      } catch (err) {
        toast.error(`${t("admin.attachments.failedDelete")}: ${(err as Error).message}`);
      }
    },
    [loadAttachments, t],
  );

  const handleRestore = useCallback(
    async (id: string) => {
      try {
        await restoreAdminAttachment(id);
        toast.success(t("admin.attachments.restoreSuccess"));
        void loadAttachments();
      } catch (err) {
        toast.error(`${t("admin.attachments.failedRestore")}: ${(err as Error).message}`);
      }
    },
    [loadAttachments, t],
  );

  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE));

  return (
    <div className="space-y-4 py-6">
      {/* Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 mb-6">
        <KPICard label={t("admin.attachments.totalStorage")} value={formatFileSize(stats.total_size_bytes)} />
        <KPICard label={t("admin.attachments.totalFiles")} value={String(stats.total_count)} />
      </div>

      {/* Filters */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t("admin.attachments.searchPlaceholder")}
            className="pl-9 pr-8"
            data-testid="admin-attachments-search"
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
          value={filterValue}
          onValueChange={setFilterValue}
        >
          <SelectTrigger className="w-full sm:w-44" data-testid="admin-attachments-filter">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">{t("admin.attachments.filterAll")}</SelectItem>
            <SelectItem value="active">{t("admin.attachments.filterActive")}</SelectItem>
            <SelectItem value="deleted">{t("admin.attachments.filterDeleted")}</SelectItem>
          </SelectContent>
        </Select>
        <span className="text-sm text-muted-foreground whitespace-nowrap">
          {t("admin.attachments.totalCount", { count: totalCount })}
        </span>
      </div>

      {/* Attachment list */}
      {loading ? (
        <p className="text-sm text-muted-foreground py-8 text-center">
          {t("common.loading")}
        </p>
      ) : attachments.length === 0 ? (
        <p className="text-sm text-muted-foreground py-8 text-center">
          {t("admin.attachments.noResults")}
        </p>
      ) : (
        <div className="space-y-2">
          {attachments.map((att) => {
            const isDeleted = !!att.deleted_at;
            const Icon = getFileIcon(att.content_type);
            return (
              <div
                key={att.id}
                className={cn(
                  "flex flex-col gap-2 rounded-lg border border-border bg-card p-4 transition-colors hover:bg-accent/30",
                  isDeleted && "opacity-60",
                )}
                data-testid={`admin-attachment-row-${att.id}`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <Icon className="h-5 w-5 flex-shrink-0 text-muted-foreground" />
                      <h4 className={cn("text-sm font-medium truncate", isDeleted && "line-through text-muted-foreground")}>
                        {att.filename}
                      </h4>
                      {isDeleted && (
                        <Badge variant="deleted" className="flex-shrink-0 text-[10px]">
                          {t("admin.attachments.filterDeleted")}
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {att.project.title}
                      <span className="mx-1.5">&middot;</span>
                      {att.content_type.split("/").pop()?.toUpperCase()}
                      <span className="mx-1.5">&middot;</span>
                      {formatFileSize(att.size_bytes)}
                      <span className="mx-1.5">&middot;</span>
                      {t("admin.attachments.uploaded")} {new Date(att.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-1 flex-shrink-0">
                    {isDeleted ? (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => void handleRestore(att.id)}
                        aria-label={t("admin.attachments.restore")}
                      >
                        <RotateCcw className="h-4 w-4 mr-1" />
                        {t("admin.attachments.restore")}
                      </Button>
                    ) : (
                      <>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => {
                            const url = `${env.apiBaseUrl}/projects/${att.project.id}/attachments/${att.id}/download/`;
                            window.open(url, "_blank");
                          }}
                          aria-label={t("admin.attachments.open")}
                        >
                          <ExternalLink className="h-4 w-4" />
                        </Button>
                        {confirmDeleteId === att.id ? (
                          <div className="flex items-center gap-1">
                            <Button
                              variant="destructive"
                              size="sm"
                              onClick={() => void handleDelete(att.id)}
                            >
                              {t("common.confirm")}
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setConfirmDeleteId(null)}
                            >
                              {t("common.cancel")}
                            </Button>
                          </div>
                        ) : (
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 text-destructive hover:text-destructive"
                            onClick={() => setConfirmDeleteId(att.id)}
                            aria-label={t("admin.attachments.deleteConfirm")}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
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
            {t("admin.attachments.next")}
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      )}
    </div>
  );
}
