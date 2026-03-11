import { env } from "@/config/env";

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
  const res = await fetch(`${env.apiBaseUrl}/reviews/`, {
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
  const res = await fetch(`${env.apiBaseUrl}/reviews/${ideaId}/assign`, {
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

export async function unassignReview(ideaId: string): Promise<{ message: string }> {
  const res = await fetch(`${env.apiBaseUrl}/reviews/${ideaId}/unassign`, {
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
