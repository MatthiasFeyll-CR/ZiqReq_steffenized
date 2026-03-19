import { useState, useEffect, useCallback, useRef } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "react-toastify";
import { Play, Loader2, Clock, Timer, ChevronDown } from "lucide-react";
import { fetchJobs, triggerJob, type AdminJob } from "@/api/admin";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";

const POLL_INTERVAL_MS = 5000;

function formatRelativeTime(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();

  if (diffMs < 0) {
    const absDiff = Math.abs(diffMs);
    if (absDiff < 60_000) return `in ${Math.round(absDiff / 1000)}s`;
    if (absDiff < 3_600_000) return `in ${Math.round(absDiff / 60_000)}m`;
    if (absDiff < 86_400_000) return `in ${Math.round(absDiff / 3_600_000)}h`;
    return `in ${Math.round(absDiff / 86_400_000)}d`;
  }

  if (diffMs < 60_000) return `${Math.round(diffMs / 1000)}s ago`;
  if (diffMs < 3_600_000) return `${Math.round(diffMs / 60_000)}m ago`;
  if (diffMs < 86_400_000) return `${Math.round(diffMs / 3_600_000)}h ago`;
  return `${Math.round(diffMs / 86_400_000)}d ago`;
}

export function JobsTab() {
  const { t } = useTranslation();
  const [jobs, setJobs] = useState<AdminJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [triggeringJob, setTriggeringJob] = useState<string | null>(null);
  const [expandedJobs, setExpandedJobs] = useState<Set<string>>(new Set());
  const [overrides, setOverrides] = useState<Record<string, Record<string, string>>>({});
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const loadJobs = useCallback(async () => {
    try {
      const data = await fetchJobs();
      setJobs(data);
    } catch {
      // Only toast on initial load
    }
  }, []);

  useEffect(() => {
    fetchJobs()
      .then((data) => {
        setJobs(data);
      })
      .catch((err) => toast.error(`${t("admin.jobs.failedLoad")}: ${err.message}`))
      .finally(() => setLoading(false));

    intervalRef.current = setInterval(loadJobs, POLL_INTERVAL_MS);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [loadJobs, t]);

  const toggleAdvanced = useCallback((taskName: string) => {
    setExpandedJobs((prev) => {
      const next = new Set(prev);
      if (next.has(taskName)) {
        next.delete(taskName);
      } else {
        next.add(taskName);
      }
      return next;
    });
  }, []);

  const setOverrideValue = useCallback((taskName: string, paramKey: string, value: string) => {
    setOverrides((prev) => ({
      ...prev,
      [taskName]: {
        ...(prev[taskName] || {}),
        [paramKey]: value,
      },
    }));
  }, []);

  async function handleTrigger(taskName: string) {
    setTriggeringJob(taskName);
    try {
      const jobOverrides = overrides[taskName];
      // Only send overrides that differ from current values
      const job = jobs.find((j) => j.task_name === taskName);
      const effectiveOverrides: Record<string, string> = {};
      if (jobOverrides && job) {
        for (const param of job.override_params) {
          const val = jobOverrides[param.key];
          if (val !== undefined && val !== "" && val !== param.current_value) {
            effectiveOverrides[param.key] = val;
          }
        }
      }
      await triggerJob(taskName, Object.keys(effectiveOverrides).length > 0 ? effectiveOverrides : undefined);
      await loadJobs();
    } catch (err) {
      const message = (err as Error).message;
      if (message.includes("wait") || message.includes("COOLDOWN")) {
        toast.warning(t("admin.jobs.cooldownError"));
      } else if (message.includes("already") || message.includes("ALREADY_RUNNING")) {
        toast.warning(t("admin.jobs.alreadyRunning"));
      } else {
        toast.error(`${t("admin.jobs.triggerError")}: ${message}`);
      }
    } finally {
      setTriggeringJob(null);
    }
  }

  if (loading) {
    return (
      <div className="py-6">
        <p className="text-sm text-muted-foreground">{t("admin.jobs.loading")}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4 py-6">
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {jobs.map((job) => {
          const isRunning = job.status === "running";
          const isCooldown = job.status === "cooldown";
          const isTriggering = triggeringJob === job.task_name;
          const isDisabled = isRunning || isCooldown || isTriggering;
          const isAdvancedOpen = expandedJobs.has(job.task_name);
          const hasOverrideParams = job.override_params && job.override_params.length > 0;

          return (
            <div
              key={job.task_name}
              className="flex flex-col rounded-md border bg-card p-5"
            >
              {/* Header */}
              <div className="mb-3 flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <h4 className="text-sm font-medium leading-tight">
                    {t(job.name_key)}
                  </h4>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {t(job.description_key)}
                  </p>
                </div>
                <Badge
                  variant="default"
                  className="shrink-0 text-xs"
                >
                  {job.queue}
                </Badge>
              </div>

              {/* Schedule & timing */}
              <div className="mb-4 space-y-1.5 text-xs text-muted-foreground">
                <div className="flex items-center gap-1.5">
                  <Clock className="h-3.5 w-3.5" />
                  <span>{t(job.schedule_key)}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Timer className="h-3.5 w-3.5" />
                  <span>
                    {t("admin.jobs.lastRun")}:{" "}
                    {job.last_run
                      ? formatRelativeTime(job.last_run)
                      : t("admin.jobs.never")}
                  </span>
                </div>
                {job.next_run && (
                  <div className="flex items-center gap-1.5">
                    <Timer className="h-3.5 w-3.5" />
                    <span>
                      {t("admin.jobs.nextRun")}:{" "}
                      {formatRelativeTime(job.next_run)}
                    </span>
                  </div>
                )}
              </div>

              {/* Status indicator */}
              {isRunning && (
                <div className="mb-3 flex items-center gap-2 text-xs text-amber-600">
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  <span>{t("admin.jobs.running")}</span>
                </div>
              )}
              {isCooldown && !job.result && (
                <div className="mb-3 text-xs text-muted-foreground">
                  {t("admin.jobs.cooldownRemaining", {
                    seconds: job.cooldown_remaining,
                  })}
                </div>
              )}

              {/* Result display */}
              {job.result != null && (
                <div className="mb-3">
                  <p className="mb-1 text-xs font-medium">{t("admin.jobs.result")}:</p>
                  <pre className="max-h-40 overflow-auto rounded bg-muted p-2 text-xs">
                    {JSON.stringify(job.result, null, 2)}
                  </pre>
                </div>
              )}

              {/* Advanced Options — expandable */}
              {hasOverrideParams && (
                <div className="mb-3">
                  <button
                    type="button"
                    onClick={() => toggleAdvanced(job.task_name)}
                    className="flex w-full items-center gap-2 text-xs text-muted-foreground hover:text-foreground transition-colors"
                  >
                    <div className="flex-1 border-t border-border" />
                    <span className="whitespace-nowrap flex items-center gap-1">
                      {t("admin.jobs.advancedOptions", "Advanced Options")}
                      <ChevronDown
                        className={`h-3 w-3 transition-transform duration-200 ${isAdvancedOpen ? "rotate-180" : ""}`}
                      />
                    </span>
                    <div className="flex-1 border-t border-border" />
                  </button>
                  {isAdvancedOpen && (
                    <div className="mt-3 space-y-3">
                      {job.override_params.map((param) => {
                        const currentOverride = overrides[job.task_name]?.[param.key] ?? "";
                        return (
                          <div key={param.key}>
                            <label className="text-xs font-medium text-foreground">
                              {t(param.label_key, param.key)}
                            </label>
                            <p className="text-[10px] text-muted-foreground mb-1">
                              {param.description}
                            </p>
                            <Input
                              type={param.type === "integer" ? "number" : "text"}
                              value={currentOverride}
                              onChange={(e) => setOverrideValue(job.task_name, param.key, e.target.value)}
                              placeholder={`${t("admin.jobs.currentValue", "Current")}: ${param.current_value}`}
                              className="h-8 text-xs"
                              data-testid={`override-${job.task_name}-${param.key}`}
                            />
                          </div>
                        );
                      })}
                      <p className="text-[10px] text-muted-foreground italic">
                        {t("admin.jobs.overrideHint", "Override applies to this run only. Leave empty to use current parameter value.")}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Trigger button — pushed to bottom */}
              <div className="mt-auto pt-2">
                <button
                  type="button"
                  onClick={() => handleTrigger(job.task_name)}
                  disabled={isDisabled}
                  className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 disabled:pointer-events-none disabled:opacity-50"
                >
                  {isRunning || isTriggering ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Play className="h-4 w-4" />
                  )}
                  {isRunning
                    ? t("admin.jobs.running")
                    : isCooldown
                      ? t("admin.jobs.cooldownBtn", {
                          seconds: job.cooldown_remaining,
                        })
                      : t("admin.jobs.triggerNow")}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
