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
