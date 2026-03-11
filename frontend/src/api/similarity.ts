import { env } from "@/config/env";
import { authFetch } from "@/lib/auth-token";

export interface SimilarIdea {
  id: string;
  title: string;
  keywords: string[];
  similarity_type: "declined_merge" | "near_threshold";
  similarity_score?: number;
}

export interface SimilarIdeasResponse {
  results: SimilarIdea[];
  count: number;
  next: string | null;
  previous: string | null;
}

export async function getSimilarIdeas(ideaId: string): Promise<SimilarIdeasResponse> {
  const res = await authFetch(`${env.apiBaseUrl}/ideas/${ideaId}/similar`, {
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export interface CreateMergeRequestResponse {
  id: string;
  requesting_idea_id: string;
  target_idea_id: string;
  merge_type: "merge" | "append";
  status: string;
}

export async function createManualMergeRequest(
  ideaId: string,
  target: { target_idea_id?: string; target_idea_url?: string },
): Promise<CreateMergeRequestResponse> {
  const res = await authFetch(`${env.apiBaseUrl}/ideas/${ideaId}/merge-request`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(target),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err = new Error(body.message || body.error || `Request failed (${res.status})`);
    (err as Error & { status: number }).status = res.status;
    throw err;
  }
  return res.json();
}
