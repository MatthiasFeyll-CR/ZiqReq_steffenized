import { env } from "@/config/env";
import { authFetch } from "@/lib/auth-token";

export type ProjectType = "software" | "non_software";

export interface Project {
  id: string;
  title: string;
  project_type: ProjectType;
  state: "open" | "in_review" | "accepted" | "dropped" | "rejected" | "deleted";
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
  data: { title?: string },
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
  project_type: ProjectType;
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

// --- Requirements API (US-002) ---

export interface RequirementsChild {
  id: string;
  type: "user_story" | "work_package";
  title: string;
  description: string;
  acceptance_criteria?: string[];
  deliverables?: string[];
  dependencies?: string[];
  priority?: "high" | "medium" | "low";
  metadata?: Record<string, unknown>;
}

export interface RequirementsItem {
  id: string;
  type: "epic" | "milestone";
  title: string;
  description: string;
  children: RequirementsChild[];
  metadata?: Record<string, unknown>;
}

export interface RequirementsDraft {
  title: string | null;
  short_description: string | null;
  structure: RequirementsItem[];
  item_locks: Record<string, boolean>;
  allow_information_gaps: boolean;
  readiness_evaluation: Record<string, unknown>;
}

export async function fetchRequirements(projectId: string): Promise<RequirementsDraft> {
  const res = await authFetch(
    `${env.apiBaseUrl}/projects/${projectId}/requirements/`,
    { credentials: "include" },
  );
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function patchRequirements(
  projectId: string,
  data: { title?: string; short_description?: string },
): Promise<RequirementsDraft> {
  const res = await authFetch(
    `${env.apiBaseUrl}/projects/${projectId}/requirements/`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(data),
    },
  );
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function addRequirementsItem(
  projectId: string,
  data: { title: string; description?: string; type: "epic" | "milestone" },
): Promise<RequirementsItem> {
  const res = await authFetch(
    `${env.apiBaseUrl}/projects/${projectId}/requirements/items`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(data),
    },
  );
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function patchRequirementsItem(
  projectId: string,
  itemId: string,
  data: { title?: string; description?: string },
): Promise<RequirementsItem> {
  const res = await authFetch(
    `${env.apiBaseUrl}/projects/${projectId}/requirements/items/${itemId}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(data),
    },
  );
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function deleteRequirementsItem(
  projectId: string,
  itemId: string,
): Promise<void> {
  const res = await authFetch(
    `${env.apiBaseUrl}/projects/${projectId}/requirements/items/${itemId}`,
    {
      method: "DELETE",
      credentials: "include",
    },
  );
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
}

export async function addRequirementsChild(
  projectId: string,
  itemId: string,
  data: {
    title: string;
    description?: string;
    acceptance_criteria?: string[];
    deliverables?: string[];
    dependencies?: string[];
    priority?: "high" | "medium" | "low";
  },
): Promise<RequirementsChild> {
  const res = await authFetch(
    `${env.apiBaseUrl}/projects/${projectId}/requirements/items/${itemId}/children`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(data),
    },
  );
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function patchRequirementsChild(
  projectId: string,
  itemId: string,
  childId: string,
  data: {
    title?: string;
    description?: string;
    acceptance_criteria?: string[];
    deliverables?: string[];
    dependencies?: string[];
    priority?: "high" | "medium" | "low";
  },
): Promise<RequirementsChild> {
  const res = await authFetch(
    `${env.apiBaseUrl}/projects/${projectId}/requirements/items/${itemId}/children/${childId}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(data),
    },
  );
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function deleteRequirementsChild(
  projectId: string,
  itemId: string,
  childId: string,
): Promise<void> {
  const res = await authFetch(
    `${env.apiBaseUrl}/projects/${projectId}/requirements/items/${itemId}/children/${childId}`,
    {
      method: "DELETE",
      credentials: "include",
    },
  );
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
}

export async function reorderRequirements(
  projectId: string,
  itemIds: string[],
): Promise<RequirementsDraft> {
  const res = await authFetch(
    `${env.apiBaseUrl}/projects/${projectId}/requirements/reorder`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ item_ids: itemIds }),
    },
  );
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function generateRequirements(
  projectId: string,
  data: { mode: "full" | "selective" | "item"; locked_item_ids?: string[] },
): Promise<{ status: string; generation_id: string }> {
  const res = await authFetch(
    `${env.apiBaseUrl}/projects/${projectId}/requirements/generate`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(data),
    },
  );
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

