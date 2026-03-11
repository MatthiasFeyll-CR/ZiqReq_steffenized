import { env } from "@/config/env";

export interface ReviewIdea {
  id: string;
  title: string;
  state: string;
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
