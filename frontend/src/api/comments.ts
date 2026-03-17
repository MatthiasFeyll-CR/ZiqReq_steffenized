import { env } from "@/config/env";
import { authFetch } from "@/lib/auth-token";

export interface CommentAuthor {
  id: string;
  display_name: string;
}

export interface CommentReaction {
  emoji: string;
  users: string[];
  count: number;
}

export interface ProjectComment {
  id: string;
  project_id: string;
  author: CommentAuthor | null;
  parent_id: string | null;
  content: string;
  is_system_event: boolean;
  system_event_type: string | null;
  reactions: CommentReaction[];
  created_at: string;
  updated_at: string;
  is_edited: boolean;
  deleted_at: string | null;
}

export interface CommentsListResponse {
  results: ProjectComment[];
  count: number;
  next: number | null;
  previous: number | null;
}

function appendToken(url: string, token?: string | null): string {
  if (!token) return url;
  const sep = url.includes("?") ? "&" : "?";
  return `${url}${sep}token=${encodeURIComponent(token)}`;
}

export async function fetchComments(
  projectId: string,
  params?: { page?: number; page_size?: number; token?: string | null },
): Promise<CommentsListResponse> {
  const sp = new URLSearchParams();
  if (params?.page) sp.set("page", String(params.page));
  if (params?.page_size) sp.set("page_size", String(params.page_size));
  if (params?.token) sp.set("token", params.token);
  const qs = sp.toString();
  const url = `${env.apiBaseUrl}/projects/${projectId}/comments/${qs ? `?${qs}` : ""}`;

  const res = await authFetch(url);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function createComment(
  projectId: string,
  data: { content: string; parent_id?: string | null },
  token?: string | null,
): Promise<ProjectComment> {
  const url = appendToken(`${env.apiBaseUrl}/projects/${projectId}/comments/`, token);
  const res = await authFetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function updateComment(
  projectId: string,
  commentId: string,
  data: { content: string },
  token?: string | null,
): Promise<ProjectComment> {
  const url = appendToken(`${env.apiBaseUrl}/projects/${projectId}/comments/${commentId}/`, token);
  const res = await authFetch(url, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function deleteComment(
  projectId: string,
  commentId: string,
  token?: string | null,
): Promise<void> {
  const url = appendToken(`${env.apiBaseUrl}/projects/${projectId}/comments/${commentId}/`, token);
  const res = await authFetch(url, {
    method: "DELETE",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
}

export async function addReaction(
  projectId: string,
  commentId: string,
  emoji: string,
  token?: string | null,
): Promise<void> {
  const url = appendToken(`${env.apiBaseUrl}/projects/${projectId}/comments/${commentId}/react`, token);
  const res = await authFetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ emoji }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
}

export async function removeReaction(
  projectId: string,
  commentId: string,
  emoji: string,
  token?: string | null,
): Promise<void> {
  const url = appendToken(`${env.apiBaseUrl}/projects/${projectId}/comments/${commentId}/react`, token);
  const res = await authFetch(url, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ emoji }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
}

export async function markCommentsRead(
  projectId: string,
  token?: string | null,
): Promise<void> {
  const url = appendToken(`${env.apiBaseUrl}/projects/${projectId}/comments/mark-read`, token);
  const res = await authFetch(url, {
    method: "POST",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
}

export async function fetchUnreadCommentCount(
  projectId: string,
  token?: string | null,
): Promise<number> {
  const url = appendToken(`${env.apiBaseUrl}/projects/${projectId}/comments/unread-count`, token);
  const res = await authFetch(url);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  const data = await res.json();
  return data.unread_count;
}

export interface ProjectSearchResult {
  id: string;
  title: string;
}

export async function searchProjectsForReference(query: string): Promise<ProjectSearchResult[]> {
  const res = await authFetch(
    `${env.apiBaseUrl}/projects/search-ref?q=${encodeURIComponent(query)}`,
  );
  if (!res.ok) {
    return [];
  }
  const data = await res.json();
  return data.results;
}
