import { env } from "@/config/env";
import { authFetch } from "@/lib/auth-token";

// ---------- AI Context ----------

export type ContextType = "global" | "software" | "non_software";

export interface FacilitatorContext {
  id: string;
  context_type: ContextType;
  content: string;
  updated_by: string | null;
  updated_at: string;
}

export interface CompanyContext {
  id: string;
  context_type: ContextType;
  sections: Record<string, unknown>;
  free_text: string;
  updated_by: string | null;
  updated_at: string;
}

export async function fetchFacilitatorContext(
  type: ContextType = "global",
): Promise<FacilitatorContext> {
  const res = await authFetch(
    `${env.apiBaseUrl}/admin/ai-context/facilitator?type=${type}`,
    { credentials: "include" },
  );
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function patchFacilitatorContext(
  content: string,
  type: ContextType = "global",
): Promise<FacilitatorContext> {
  const res = await authFetch(
    `${env.apiBaseUrl}/admin/ai-context/facilitator?type=${type}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ content }),
    },
  );
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function fetchCompanyContext(
  type: ContextType = "global",
): Promise<CompanyContext> {
  const res = await authFetch(
    `${env.apiBaseUrl}/admin/ai-context/company?type=${type}`,
    { credentials: "include" },
  );
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function patchCompanyContext(
  sections: Record<string, unknown>,
  free_text: string,
  type: ContextType = "global",
): Promise<CompanyContext> {
  const res = await authFetch(
    `${env.apiBaseUrl}/admin/ai-context/company?type=${type}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ sections, free_text }),
    },
  );
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
  projects_by_state: {
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
  project_count: number;
  review_count: number;
  contribution_count: number;
}

// ---------- Projects (Admin) ----------

export interface AdminProject {
  id: string;
  title: string;
  state: "open" | "in_review" | "accepted" | "dropped" | "rejected";
  keywords: string[];
  owner: { id: string; display_name: string };
  created_at: string;
  updated_at: string;
}

export interface AdminProjectsResponse {
  results: AdminProject[];
  count: number;
  next: number | null;
  previous: number | null;
}

export async function fetchAdminProjects(params?: {
  page?: number;
  page_size?: number;
  state?: string;
  search?: string;
}): Promise<AdminProjectsResponse> {
  const searchParams = new URLSearchParams();
  if (params?.page) searchParams.set("page", String(params.page));
  if (params?.page_size) searchParams.set("page_size", String(params.page_size));
  if (params?.state) searchParams.set("state", params.state);
  if (params?.search) searchParams.set("search", params.search);

  const qs = searchParams.toString();
  const res = await authFetch(`${env.apiBaseUrl}/admin/projects${qs ? `?${qs}` : ""}`, {
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

// ---------- Attachments (Admin) ----------

export interface AdminAttachment {
  id: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  extraction_status: string;
  created_at: string;
  deleted_at: string | null;
  message_id: string | null;
  project: { id: string; title: string };
}

export interface AdminAttachmentsResponse {
  results: AdminAttachment[];
  count: number;
  next: number | null;
  previous: number | null;
  stats: { total_size_bytes: number; total_count: number };
}

export async function fetchAdminAttachments(params?: {
  page?: number;
  page_size?: number;
  filter?: "active" | "deleted" | "all";
  search?: string;
}): Promise<AdminAttachmentsResponse> {
  const searchParams = new URLSearchParams();
  if (params?.page) searchParams.set("page", String(params.page));
  if (params?.page_size) searchParams.set("page_size", String(params.page_size));
  if (params?.filter) searchParams.set("filter", params.filter);
  if (params?.search) searchParams.set("search", params.search);

  const qs = searchParams.toString();
  const res = await authFetch(`${env.apiBaseUrl}/admin/attachments${qs ? `?${qs}` : ""}`, {
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function deleteAdminAttachment(id: string): Promise<void> {
  const res = await authFetch(`${env.apiBaseUrl}/admin/attachments/${id}`, {
    method: "DELETE",
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
}

export async function restoreAdminAttachment(id: string): Promise<void> {
  const res = await authFetch(`${env.apiBaseUrl}/admin/attachments/${id}/restore/`, {
    method: "POST",
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
}

// ---------- Users ----------

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
