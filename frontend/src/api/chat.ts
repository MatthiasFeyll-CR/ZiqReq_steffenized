import { env } from "@/config/env";

export interface ChatMessage {
  id: string;
  idea_id: string;
  sender_type: "user" | "ai";
  sender_id: string | null;
  ai_agent: string | null;
  content: string;
  message_type: "regular" | "delegation";
  created_at: string;
}

export interface ChatMessagesResponse {
  messages: ChatMessage[];
  total: number;
  limit: number;
  offset: number;
}

export async function fetchChatMessages(
  ideaId: string,
  params?: { limit?: number; offset?: number },
): Promise<ChatMessagesResponse> {
  const searchParams = new URLSearchParams();
  if (params?.limit != null) searchParams.set("limit", String(params.limit));
  if (params?.offset != null) searchParams.set("offset", String(params.offset));
  const qs = searchParams.toString();
  const url = `${env.apiBaseUrl}/ideas/${ideaId}/chat/${qs ? `?${qs}` : ""}`;

  const res = await fetch(url, { credentials: "include" });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}
