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

export interface IdeaComment {
  id: string;
  idea_id: string;
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
  results: IdeaComment[];
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
  ideaId: string,
  params?: { page?: number; page_size?: number; token?: string | null },
): Promise<CommentsListResponse> {
  const sp = new URLSearchParams();
  if (params?.page) sp.set("page", String(params.page));
  if (params?.page_size) sp.set("page_size", String(params.page_size));
  if (params?.token) sp.set("token", params.token);
  const qs = sp.toString();
  const url = `${env.apiBaseUrl}/ideas/${ideaId}/comments/${qs ? `?${qs}` : ""}`;

  const res = await authFetch(url);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function createComment(
  ideaId: string,
  data: { content: string; parent_id?: string | null },
  token?: string | null,
): Promise<IdeaComment> {
  const url = appendToken(`${env.apiBaseUrl}/ideas/${ideaId}/comments/`, token);
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
  ideaId: string,
  commentId: string,
  data: { content: string },
  token?: string | null,
): Promise<IdeaComment> {
  const url = appendToken(`${env.apiBaseUrl}/ideas/${ideaId}/comments/${commentId}/`, token);
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
  ideaId: string,
  commentId: string,
  token?: string | null,
): Promise<void> {
  const url = appendToken(`${env.apiBaseUrl}/ideas/${ideaId}/comments/${commentId}/`, token);
  const res = await authFetch(url, {
    method: "DELETE",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
}

export async function addReaction(
  ideaId: string,
  commentId: string,
  emoji: string,
  token?: string | null,
): Promise<void> {
  const url = appendToken(`${env.apiBaseUrl}/ideas/${ideaId}/comments/${commentId}/react`, token);
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
  ideaId: string,
  commentId: string,
  emoji: string,
  token?: string | null,
): Promise<void> {
  const url = appendToken(`${env.apiBaseUrl}/ideas/${ideaId}/comments/${commentId}/react`, token);
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
  ideaId: string,
  token?: string | null,
): Promise<void> {
  const url = appendToken(`${env.apiBaseUrl}/ideas/${ideaId}/comments/mark-read`, token);
  const res = await authFetch(url, {
    method: "POST",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
}

export async function fetchUnreadCommentCount(
  ideaId: string,
  token?: string | null,
): Promise<number> {
  const url = appendToken(`${env.apiBaseUrl}/ideas/${ideaId}/comments/unread-count`, token);
  const res = await authFetch(url);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  const data = await res.json();
  return data.unread_count;
}

export interface IdeaSearchResult {
  id: string;
  title: string;
}

export async function searchIdeasForReference(query: string): Promise<IdeaSearchResult[]> {
  const res = await authFetch(
    `${env.apiBaseUrl}/ideas/search-ref?q=${encodeURIComponent(query)}`,
  );
  if (!res.ok) {
    return [];
  }
  const data = await res.json();
  return data.results;
}
