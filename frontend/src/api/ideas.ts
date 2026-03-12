import { env } from "@/config/env";
import { authFetch } from "@/lib/auth-token";

export interface MergeRequestPending {
  id: string;
  requesting_idea_id: string;
  requesting_owner_name: string;
  requesting_idea_title: string;
}

export interface IdeaRef {
  id: string;
  title: string;
  url: string;
}

export interface Idea {
  id: string;
  title: string;
  state: "open" | "in_review" | "accepted" | "dropped" | "rejected";
  agent_mode: "interactive" | "silent";
  visibility: "private" | "collaborating";
  owner_id: string;
  co_owner_id: string | null;
  created_at: string;
  updated_at: string;
  collaborators: Array<{ user_id: string; display_name: string }>;
  merge_request_pending: MergeRequestPending | null;
  merged_idea_ref: IdeaRef | null;
  appended_idea_ref: IdeaRef | null;
  read_only?: boolean;
}

export async function fetchIdea(id: string, token?: string): Promise<Idea> {
  const url = token
    ? `${env.apiBaseUrl}/ideas/${id}/?token=${encodeURIComponent(token)}`
    : `${env.apiBaseUrl}/ideas/${id}/`;
  const res = await authFetch(url);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err = new Error(body.message || body.error || `Request failed (${res.status})`);
    (err as Error & { status: number }).status = res.status;
    throw err;
  }
  return res.json();
}

export async function patchIdea(
  id: string,
  data: { title?: string; agent_mode?: "interactive" | "silent" },
): Promise<Idea> {
  const res = await authFetch(`${env.apiBaseUrl}/ideas/${id}/`, {
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

export interface CreateIdeaResponse {
  id: string;
  title: string;
  state: string;
  visibility: string;
  agent_mode: string;
  owner: { id: string; display_name: string } | null;
  co_owner: { id: string; display_name: string } | null;
  created_at: string;
}

export async function createIdea(
  firstMessage: string,
): Promise<CreateIdeaResponse> {
  const res = await authFetch(`${env.apiBaseUrl}/ideas/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ first_message: firstMessage }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }

  return res.json();
}

export interface IdeaListItem {
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

export interface IdeasListResponse {
  results: IdeaListItem[];
  count: number;
  next: string | null;
  previous: string | null;
}

export async function fetchIdeas(
  filter?: string,
  params?: Record<string, string>,
): Promise<IdeasListResponse> {
  const searchParams = new URLSearchParams();
  if (filter) searchParams.set("filter", filter);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value) searchParams.set(key, value);
    }
  }
  const qs = searchParams.toString();
  const url = `${env.apiBaseUrl}/ideas/${qs ? `?${qs}` : ""}`;

  const res = await authFetch(url, { credentials: "include" });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export interface InvitationListItem {
  id: string;
  idea_id: string;
  idea_title: string;
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

export async function deleteIdea(id: string): Promise<void> {
  const res = await authFetch(`${env.apiBaseUrl}/ideas/${id}/`, {
    method: "DELETE",
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
}

export async function restoreIdea(id: string): Promise<void> {
  const res = await authFetch(`${env.apiBaseUrl}/ideas/${id}/restore`, {
    method: "POST",
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
}

export interface SubmitIdeaResponse {
  version_number: number;
  pdf_url: string;
  state: string;
}

export async function submitIdea(
  ideaId: string,
  data: { message?: string; reviewer_ids?: string[] },
): Promise<SubmitIdeaResponse> {
  const res = await authFetch(`${env.apiBaseUrl}/ideas/${ideaId}/submit`, {
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

export async function fetchContextWindow(ideaId: string): Promise<ContextWindowData> {
  const res = await authFetch(`${env.apiBaseUrl}/ideas/${ideaId}/context-window`, {
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function consentMergeRequest(
  mergeRequestId: string,
  consent: "accept" | "decline",
): Promise<Record<string, unknown>> {
  const res = await authFetch(`${env.apiBaseUrl}/merge-requests/${mergeRequestId}/consent`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ consent }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}
