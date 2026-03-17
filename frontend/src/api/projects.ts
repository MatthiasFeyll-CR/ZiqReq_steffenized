import { env } from "@/config/env";
import { authFetch } from "@/lib/auth-token";

export type ProjectType = "software" | "non_software";

export interface Project {
  id: string;
  title: string;
  project_type: ProjectType;
  state: "open" | "in_review" | "accepted" | "dropped" | "rejected" | "deleted";
  agent_mode: "interactive" | "silent";
  visibility: "private" | "collaborating";
  owner_id: string;
  created_at: string;
  updated_at: string;
  collaborators: Array<{ user_id: string; display_name: string }>;
  read_only?: boolean;
}

export async function fetchProject(id: string, token?: string): Promise<Project> {
  const url = token
    ? `${env.apiBaseUrl}/projects/${id}/?token=${encodeURIComponent(token)}`
    : `${env.apiBaseUrl}/projects/${id}/`;
  const res = await authFetch(url);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err = new Error(body.message || body.error || `Request failed (${res.status})`);
    (err as Error & { status: number }).status = res.status;
    throw err;
  }
  return res.json();
}

export async function patchProject(
  id: string,
  data: { title?: string; agent_mode?: "interactive" | "silent" },
): Promise<Project> {
  const res = await authFetch(`${env.apiBaseUrl}/projects/${id}/`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err = new Error(body.message || body.error || `Request failed (${res.status})`);
    (err as Error & { status: number }).status = res.status;
    throw err;
  }
  return res.json();
}

export interface CreateProjectResponse {
  id: string;
  title: string;
  project_type: ProjectType;
  state: string;
  visibility: string;
  agent_mode: string;
  owner: { id: string; display_name: string } | null;
  created_at: string;
}

export async function createProject(
  projectType: ProjectType,
): Promise<CreateProjectResponse> {
  const res = await authFetch(`${env.apiBaseUrl}/projects/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ project_type: projectType }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }

  return res.json();
}

export interface ProjectListItem {
  id: string;
  title: string;
  state: string;
  visibility: string;
  role: string;
  owner: { id: string; display_name: string } | null;
  collaborator_count: number;
  updated_at: string;
  deleted_at: string | null;
}

export interface ProjectsListResponse {
  results: ProjectListItem[];
  count: number;
  next: string | null;
  previous: string | null;
}

export async function fetchProjects(
  filter?: string,
  params?: Record<string, string>,
): Promise<ProjectsListResponse> {
  const searchParams = new URLSearchParams();
  if (filter) searchParams.set("filter", filter);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value) searchParams.set(key, value);
    }
  }
  const qs = searchParams.toString();
  const url = `${env.apiBaseUrl}/projects/${qs ? `?${qs}` : ""}`;

  const res = await authFetch(url, { credentials: "include" });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export interface InvitationListItem {
  id: string;
  project_id: string;
  project_title: string;
  inviter: { id: string; display_name: string };
  created_at: string;
}

export interface InvitationsListResponse {
  invitations: InvitationListItem[];
}

export async function fetchInvitations(): Promise<InvitationsListResponse> {
  const res = await authFetch(`${env.apiBaseUrl}/invitations/`, {
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function deleteProject(id: string): Promise<void> {
  const res = await authFetch(`${env.apiBaseUrl}/projects/${id}/`, {
    method: "DELETE",
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
}

export async function restoreProject(id: string): Promise<void> {
  const res = await authFetch(`${env.apiBaseUrl}/projects/${id}/restore`, {
    method: "POST",
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
}

export interface SubmitProjectResponse {
  version_number: number;
  pdf_url: string;
  state: string;
}

export async function submitProject(
  projectId: string,
  data: { message?: string; reviewer_ids?: string[] },
): Promise<SubmitProjectResponse> {
  const res = await authFetch(`${env.apiBaseUrl}/projects/${projectId}/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err = new Error(body.message || body.error || `Request failed (${res.status})`);
    (err as Error & { status: number }).status = res.status;
    throw err;
  }
  return res.json();
}

export interface ContextWindowData {
  usage_percentage: number;
  message_count: number;
  compression_iterations: number;
  recent_message_count: number;
}

export async function fetchContextWindow(projectId: string): Promise<ContextWindowData> {
  const res = await authFetch(`${env.apiBaseUrl}/projects/${projectId}/context-window`, {
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

