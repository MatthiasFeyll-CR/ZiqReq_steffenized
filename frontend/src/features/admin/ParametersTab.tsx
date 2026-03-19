import { useState, useEffect, useRef, useMemo } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "react-toastify";
import { Search, X, RotateCcw } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { fetchParameters, patchParameter, type AdminParameter } from "@/api/admin";
import { cn } from "@/lib/utils";

export function ParametersTab() {
  const { t } = useTranslation();
  const [parameters, setParameters] = useState<AdminParameter[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingKey, setEditingKey] = useState<string | null>(null);
  const [editValue, setEditValue] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchParameters()
      .then(setParameters)
      .catch((err) => toast.error(`${t("admin.failedLoadParameters")}: ${err.message}`))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (editingKey && inputRef.current) {
      inputRef.current.focus();
    }
  }, [editingKey]);

  // Group parameters by category and apply search filter
  const { groups, filteredCount } = useMemo(() => {
    const query = searchQuery.toLowerCase().trim();
    const filtered = query
      ? parameters.filter(
          (p) =>
            p.key.toLowerCase().includes(query) ||
            p.description.toLowerCase().includes(query) ||
            p.category.toLowerCase().includes(query),
        )
      : parameters;

    const map = new Map<string, AdminParameter[]>();
    for (const param of filtered) {
      const cat = param.category || "General";
      if (!map.has(cat)) map.set(cat, []);
      map.get(cat)!.push(param);
    }

    // Sort categories alphabetically, but "General" first
    const sorted = [...map.entries()].sort(([a], [b]) => {
      if (a === "General") return -1;
      if (b === "General") return 1;
      return a.localeCompare(b);
    });

    return { groups: sorted, filteredCount: filtered.length };
  }, [parameters, searchQuery]);

  function startEditing(param: AdminParameter) {
    setEditingKey(param.key);
    setEditValue(param.value);
  }

  async function saveEdit(key: string) {
    try {
      const updated = await patchParameter(key, editValue);
      setParameters((prev) => prev.map((p) => (p.key === key ? updated : p)));
      setEditingKey(null);
      toast.success(t("admin.parameterUpdated", { key }));
    } catch (err) {
      toast.error(`${t("admin.failedUpdateParameter")}: ${(err as Error).message}`);
    }
  }

  async function resetToDefault(param: AdminParameter) {
    try {
      const updated = await patchParameter(param.key, param.default_value);
      setParameters((prev) => prev.map((p) => (p.key === param.key ? updated : p)));
      toast.success(t("admin.parameterUpdated", { key: param.key }));
    } catch (err) {
      toast.error(`${t("admin.failedUpdateParameter")}: ${(err as Error).message}`);
    }
  }

  function cancelEdit() {
    setEditingKey(null);
  }

  function handleKeyDown(e: React.KeyboardEvent, key: string) {
    if (e.key === "Enter") {
      e.preventDefault();
      saveEdit(key);
    } else if (e.key === "Escape") {
      cancelEdit();
    }
  }

  if (loading) {
    return (
      <div className="py-6">
        <p className="text-sm text-muted-foreground">{t("admin.loadingParameters")}</p>
      </div>
    );
  }

  const modifiedCount = parameters.filter((p) => p.value !== p.default_value).length;

  return (
    <div className="space-y-4 py-6">
      {/* Search & summary */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t("admin.parameters.searchPlaceholder", "Search parameters...")}
            className="pl-9 pr-8"
            data-testid="parameters-search"
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
        <div className="flex items-center gap-3 text-sm text-muted-foreground whitespace-nowrap">
          <span>
            {filteredCount} {t("admin.parameters.parameters", "parameters")}
          </span>
          {modifiedCount > 0 && (
            <span className="inline-flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-primary" />
              {modifiedCount} {t("admin.parameters.modified", "modified")}
            </span>
          )}
        </div>
      </div>

      {/* Grouped parameters */}
      {groups.length === 0 ? (
        <p className="text-sm text-muted-foreground py-8 text-center">
          {t("common.noResults")}
        </p>
      ) : (
        <div className="space-y-6" data-testid="parameters-table">
          {groups.map(([category, params]) => (
            <div key={category}>
              <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 px-1">
                {category}
              </h3>
              <div className="rounded-lg border border-border divide-y divide-border overflow-hidden">
                {params.map((param) => {
                  const isModified = param.value !== param.default_value;
                  const isEditing = editingKey === param.key;

                  return (
                    <div
                      key={param.key}
                      className={cn(
                        "px-4 py-3 transition-colors",
                        isModified && "bg-primary/3",
                      )}
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            {isModified && (
                              <span
                                className="inline-block h-2 w-2 rounded-full bg-primary shrink-0"
                                data-testid={`modified-indicator-${param.key}`}
                                title={t("admin.modifiedFromDefault")}
                              />
                            )}
                            <code className="text-xs font-mono font-medium text-foreground">
                              {param.key}
                            </code>
                          </div>
                          <p className="text-xs text-muted-foreground mt-0.5">
                            {param.description}
                          </p>
                        </div>
                        <div className="flex items-center gap-2 shrink-0">
                          {isEditing ? (
                            <input
                              ref={inputRef}
                              type="text"
                              value={editValue}
                              onChange={(e) => setEditValue(e.target.value)}
                              onKeyDown={(e) => handleKeyDown(e, param.key)}
                              onBlur={cancelEdit}
                              className="w-40 rounded border border-border bg-background px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                              data-testid={`edit-input-${param.key}`}
                            />
                          ) : (
                            <span
                              className="cursor-pointer rounded px-2 py-1 text-sm font-mono bg-muted hover:bg-muted/80 transition-colors min-w-[60px] text-right"
                              onDoubleClick={() => startEditing(param)}
                              data-testid={`value-${param.key}`}
                              role="button"
                              tabIndex={0}
                              title={t("admin.parameters.doubleClickEdit", "Double-click to edit")}
                            >
                              {param.value}
                            </span>
                          )}
                          {isModified && !isEditing && (
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-7 w-7"
                              onClick={() => void resetToDefault(param)}
                              aria-label={t("admin.parameters.resetDefault", "Reset to default")}
                              title={`${t("admin.tableDefault")}: ${param.default_value}`}
                            >
                              <RotateCcw className="h-3.5 w-3.5" />
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
