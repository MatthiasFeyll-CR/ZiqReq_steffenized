import { env } from "@/config/env";

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
  const res = await fetch(`${env.apiBaseUrl}/admin/ai-context/facilitator`, {
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function patchFacilitatorContext(content: string): Promise<FacilitatorContext> {
  const res = await fetch(`${env.apiBaseUrl}/admin/ai-context/facilitator`, {
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
  const res = await fetch(`${env.apiBaseUrl}/admin/ai-context/company`, {
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
  const res = await fetch(`${env.apiBaseUrl}/admin/ai-context/company`, {
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
  const res = await fetch(`${env.apiBaseUrl}/admin/parameters`, {
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function patchParameter(key: string, value: string): Promise<AdminParameter> {
  const res = await fetch(`${env.apiBaseUrl}/admin/parameters/${encodeURIComponent(key)}`, {
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
