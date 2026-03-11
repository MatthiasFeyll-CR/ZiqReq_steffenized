import { env } from "@/config/env";

export interface UnreadCountResponse {
  unread_count: number;
}

export async function fetchUnreadCount(): Promise<UnreadCountResponse> {
  const res = await fetch(`${env.apiBaseUrl}/notifications/unread-count`, {
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}
