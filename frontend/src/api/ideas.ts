import { env } from "@/config/env";

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
  const res = await fetch(`${env.apiBaseUrl}/ideas/`, {
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

  const res = await fetch(url, { credentials: "include" });
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
  const res = await fetch(`${env.apiBaseUrl}/invitations/`, {
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function deleteIdea(id: string): Promise<void> {
  const res = await fetch(`${env.apiBaseUrl}/ideas/${id}/`, {
    method: "DELETE",
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
}

export async function restoreIdea(id: string): Promise<void> {
  const res = await fetch(`${env.apiBaseUrl}/ideas/${id}/restore/`, {
    method: "POST",
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
}
