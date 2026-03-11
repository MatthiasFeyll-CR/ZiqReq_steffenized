import { env } from "@/config/env";
import { authFetch } from "@/lib/auth-token";

export interface ReviewIdea {
  id: string;
  title: string;
  state: string;
  owner_id: string;
  co_owner_id: string | null;
  owner_name: string;
  submitted_at: string;
  reviewers: Array<{ id: string; display_name: string }>;
}

export interface ReviewListResponse {
  assigned_to_me: ReviewIdea[];
  unassigned: ReviewIdea[];
  accepted: ReviewIdea[];
  rejected: ReviewIdea[];
  dropped: ReviewIdea[];
}

export async function fetchReviews(): Promise<ReviewListResponse> {
  const res = await authFetch(`${env.apiBaseUrl}/reviews/`, {
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err = new Error(body.message || body.error || `Request failed (${res.status})`);
    (err as Error & { status: number }).status = res.status;
    throw err;
  }
  return res.json();
}

export async function assignReview(ideaId: string): Promise<{ message: string }> {
  const res = await authFetch(`${env.apiBaseUrl}/reviews/${ideaId}/assign`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({}),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err = new Error(body.message || body.error || `Request failed (${res.status})`);
    (err as Error & { status: number }).status = res.status;
    throw err;
  }
  return res.json();
}

export interface TimelineEntry {
  id: string;
  entry_type: "comment" | "state_change" | "resubmission";
  author: { id: string; display_name: string } | null;
  content: string | null;
  parent_entry_id: string | null;
  old_state: string | null;
  new_state: string | null;
  old_version_id: string | null;
  new_version_id: string | null;
  created_at: string;
}

export interface ReviewerInfo {
  id: string;
  display_name: string;
}

export async function fetchTimeline(ideaId: string): Promise<TimelineEntry[]> {
  const res = await authFetch(`${env.apiBaseUrl}/ideas/${ideaId}/review/timeline`, {
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err = new Error(body.message || body.error || `Request failed (${res.status})`);
    (err as Error & { status: number }).status = res.status;
    throw err;
  }
  return res.json();
}

export async function fetchIdeaReviewers(ideaId: string): Promise<{ reviewers: ReviewerInfo[] }> {
  const res = await authFetch(`${env.apiBaseUrl}/ideas/${ideaId}/review/reviewers`, {
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err = new Error(body.message || body.error || `Request failed (${res.status})`);
    (err as Error & { status: number }).status = res.status;
    throw err;
  }
  return res.json();
}

export async function postComment(
  ideaId: string,
  data: { content: string; parent_entry_id?: string },
): Promise<TimelineEntry> {
  const res = await authFetch(`${env.apiBaseUrl}/ideas/${ideaId}/review/timeline`, {
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

export interface ReviewerUser {
  id: string;
  display_name: string;
  email: string;
}

export async function fetchReviewerUsers(): Promise<ReviewerUser[]> {
  const res = await authFetch(`${env.apiBaseUrl}/reviews/reviewers`, {
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err = new Error(body.message || body.error || `Request failed (${res.status})`);
    (err as Error & { status: number }).status = res.status;
    throw err;
  }
  return res.json();
}

export async function unassignReview(ideaId: string): Promise<{ message: string }> {
  const res = await authFetch(`${env.apiBaseUrl}/reviews/${ideaId}/unassign`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({}),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err = new Error(body.message || body.error || `Request failed (${res.status})`);
    (err as Error & { status: number }).status = res.status;
    throw err;
  }
  return res.json();
}
