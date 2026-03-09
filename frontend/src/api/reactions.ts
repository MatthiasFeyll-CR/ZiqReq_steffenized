import { env } from "@/config/env";

export type ReactionType = "thumbs_up" | "thumbs_down" | "heart";

export interface Reaction {
  id: string;
  message_id: string;
  user_id: string;
  reaction_type: ReactionType;
  created_at: string;
}

export async function addReaction(
  ideaId: string,
  messageId: string,
  reactionType: ReactionType,
): Promise<Reaction> {
  const url = `${env.apiBaseUrl}/ideas/${ideaId}/chat/${messageId}/reactions`;
  const res = await fetch(url, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reaction_type: reactionType }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.code || body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function removeReaction(
  ideaId: string,
  messageId: string,
): Promise<void> {
  const url = `${env.apiBaseUrl}/ideas/${ideaId}/chat/${messageId}/reactions`;
  const res = await fetch(url, {
    method: "DELETE",
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.code || body.message || body.error || `Request failed (${res.status})`);
  }
}
