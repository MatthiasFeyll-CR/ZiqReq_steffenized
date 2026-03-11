import { env } from "@/config/env";
import { authFetch } from "@/lib/auth-token";

// ---------- AI Context ----------

export interface FacilitatorContext {
  id: string;
  content: string;
  updated_by: string | null;
  updated_at: string;
}

export interface CompanyContext {
  id: string;
  sections: Record<string, unknown>;
  free_text: string;
  updated_by: string | null;
  updated_at: string;
}

export async function fetchFacilitatorContext(): Promise<FacilitatorContext> {
  const res = await authFetch(`${env.apiBaseUrl}/admin/ai-context/facilitator`, {
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function patchFacilitatorContext(content: string): Promise<FacilitatorContext> {
  const res = await authFetch(`${env.apiBaseUrl}/admin/ai-context/facilitator`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ content }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function fetchCompanyContext(): Promise<CompanyContext> {
  const res = await authFetch(`${env.apiBaseUrl}/admin/ai-context/company`, {
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function patchCompanyContext(
  sections: Record<string, unknown>,
  free_text: string,
): Promise<CompanyContext> {
  const res = await authFetch(`${env.apiBaseUrl}/admin/ai-context/company`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ sections, free_text }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

// ---------- Parameters ----------

export interface AdminParameter {
  key: string;
  value: string;
  default_value: string;
  description: string;
  data_type: "string" | "integer" | "float" | "boolean";
  category: string;
  updated_by: string | null;
  updated_at: string;
}

export async function fetchParameters(): Promise<AdminParameter[]> {
  const res = await authFetch(`${env.apiBaseUrl}/admin/parameters`, {
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function patchParameter(key: string, value: string): Promise<AdminParameter> {
  const res = await authFetch(`${env.apiBaseUrl}/admin/parameters/${encodeURIComponent(key)}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ value }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

// ---------- Monitoring ----------

export interface ServiceHealth {
  status: "healthy" | "unhealthy";
  last_check: string;
}

export interface MonitoringData {
  active_connections: number;
  ideas_by_state: {
    open: number;
    in_review: number;
    accepted: number;
    dropped: number;
    rejected: number;
  };
  active_users: number;
  online_users: number;
  ai_processing: {
    request_count: number;
    success_count: number;
    failure_count: number;
  };
  system_health: Record<string, ServiceHealth>;
}

export interface AlertConfig {
  user_id: string;
  is_active: boolean;
}

export async function fetchMonitoringData(): Promise<MonitoringData> {
  const res = await authFetch(`${env.apiBaseUrl}/admin/monitoring`, {
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function fetchAlertConfig(): Promise<AlertConfig> {
  const res = await authFetch(`${env.apiBaseUrl}/admin/monitoring/alerts`, {
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function patchAlertConfig(is_active: boolean): Promise<AlertConfig> {
  const res = await authFetch(`${env.apiBaseUrl}/admin/monitoring/alerts`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ is_active }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

// ---------- Users ----------

export interface AdminUser {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  display_name: string;
  roles: string[];
  idea_count: number;
  review_count: number;
  contribution_count: number;
}

export async function searchUsers(query: string): Promise<AdminUser[]> {
  const params = query ? `?q=${encodeURIComponent(query)}` : "";
  const res = await authFetch(`${env.apiBaseUrl}/admin/users/search${params}`, {
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}
