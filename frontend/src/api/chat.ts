import { env } from "@/config/env";
import { authFetch } from "@/lib/auth-token";
import type { Attachment } from "@/api/attachments";

export interface ChatMessage {
  id: string;
  project_id: string;
  sender_type: "user" | "ai";
  sender_id: string | null;
  ai_agent: string | null;
  content: string;
  message_type: "regular" | "delegation";
  created_at: string;
  attachments?: Attachment[];
}

export interface ChatMessagesResponse {
  messages: ChatMessage[];
  total: number;
  limit: number;
  offset: number;
}

export async function sendChatMessage(
  projectId: string,
  content: string,
  attachment_ids?: string[],
): Promise<ChatMessage> {
  const url = `${env.apiBaseUrl}/projects/${projectId}/chat/`;
  const body: Record<string, unknown> = { content };
  if (attachment_ids && attachment_ids.length > 0) {
    body.attachment_ids = attachment_ids;
  }
  const res = await authFetch(url, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function fetchChatMessages(
  projectId: string,
  params?: { limit?: number; offset?: number },
): Promise<ChatMessagesResponse> {
  const searchParams = new URLSearchParams();
  if (params?.limit != null) searchParams.set("limit", String(params.limit));
  if (params?.offset != null) searchParams.set("offset", String(params.offset));
  const qs = searchParams.toString();
  const url = `${env.apiBaseUrl}/projects/${projectId}/chat/${qs ? `?${qs}` : ""}`;

  const res = await authFetch(url, { credentials: "include" });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}
