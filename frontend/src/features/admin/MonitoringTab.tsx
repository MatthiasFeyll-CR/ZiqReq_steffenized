import { useState, useEffect } from "react";
import { toast } from "react-toastify";
import { KPICard } from "@/components/admin/KPICard";
import { ServiceHealthTable } from "@/components/admin/ServiceHealthTable";
import {
  fetchMonitoringData,
  fetchAlertConfig,
  patchAlertConfig,
  type MonitoringData,
  type AlertConfig,
} from "@/api/admin";

export function MonitoringTab() {
  const [data, setData] = useState<MonitoringData | null>(null);
  const [alertConfig, setAlertConfig] = useState<AlertConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState(false);

  useEffect(() => {
    Promise.all([fetchMonitoringData(), fetchAlertConfig()])
      .then(([monData, alertData]) => {
        setData(monData);
        setAlertConfig(alertData);
      })
      .catch((err) => toast.error(`Failed to load monitoring data: ${err.message}`))
      .finally(() => setLoading(false));

    const interval = setInterval(() => {
      fetchMonitoringData()
        .then(setData)
        .catch(() => {});
    }, 15000);

    return () => clearInterval(interval);
  }, []);

  async function handleAlertToggle() {
    if (!alertConfig) return;
    setToggling(true);
    try {
      const updated = await patchAlertConfig(!alertConfig.is_active);
      setAlertConfig(updated);
      toast.success(updated.is_active ? "Alert notifications enabled" : "Alert notifications disabled");
    } catch (err) {
      toast.error(`Failed to update alert config: ${(err as Error).message}`);
    } finally {
      setToggling(false);
    }
  }

  if (loading) {
    return (
      <div className="py-6">
        <p className="text-sm text-muted-foreground">Loading monitoring data...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="py-6">
        <p className="text-sm text-muted-foreground">Failed to load monitoring data.</p>
      </div>
    );
  }

  const totalIdeas = Object.values(data.ideas_by_state).reduce((a, b) => a + b, 0);

  return (
    <div className="space-y-6 py-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard label="Active Connections" value={data.active_connections} />
        <KPICard label="Ideas by State" value={totalIdeas} />
        <KPICard label="Active Users" value={data.active_users} />
        <KPICard label="AI Requests" value={data.ai_processing.request_count} />
      </div>

      {/* Ideas by state breakdown */}
      <div className="rounded-md border bg-card p-4">
        <h4 className="mb-3 text-sm font-medium">Ideas by State</h4>
        <div className="flex flex-wrap gap-4 text-sm">
          {Object.entries(data.ideas_by_state).map(([state, count]) => (
            <span key={state} className="flex items-center gap-1.5">
              <span className="capitalize text-muted-foreground">{state.replace("_", " ")}:</span>
              <span className="font-medium">{count}</span>
            </span>
          ))}
        </div>
      </div>

      {/* Service Health Table */}
      <section>
        <h4 className="mb-3 text-sm font-medium">Service Health</h4>
        <ServiceHealthTable health={data.system_health} />
      </section>

      {/* Alert Configuration */}
      <section className="rounded-md border bg-card p-4">
        <h4 className="mb-3 text-sm font-medium">Alert Configuration</h4>
        <label className="flex items-center gap-3" data-testid="alert-toggle">
          <button
            type="button"
            role="switch"
            aria-checked={alertConfig?.is_active ?? false}
            onClick={handleAlertToggle}
            disabled={toggling}
            className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors ${
              alertConfig?.is_active ? "bg-primary" : "bg-muted"
            }`}
            data-testid="alert-toggle-switch"
          >
            <span
              className={`pointer-events-none inline-block h-5 w-5 rounded-full bg-background shadow-lg transition-transform ${
                alertConfig?.is_active ? "translate-x-5" : "translate-x-0"
              }`}
            />
          </button>
          <span className="text-sm">Receive monitoring alerts</span>
        </label>
      </section>
    </div>
  );
}
