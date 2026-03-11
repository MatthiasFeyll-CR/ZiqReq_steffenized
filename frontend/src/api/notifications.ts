import { env } from "@/config/env";
import { authFetch } from "@/lib/auth-token";

export interface UnreadCountResponse {
  unread_count: number;
}

export interface Notification {
  id: string;
  user_id: string;
  event_type: string;
  title: string;
  body: string;
  reference_id: string | null;
  reference_type: string | null;
  is_read: boolean;
  action_taken: boolean;
  created_at: string;
}

export interface NotificationsResponse {
  notifications: Notification[];
  unread_count: number;
  count: number;
  page: number;
  page_size: number;
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message || body.error || `Request failed (${res.status})`);
  }
  return res.json();
}

export async function fetchUnreadCount(): Promise<UnreadCountResponse> {
  const res = await authFetch(`${env.apiBaseUrl}/notifications/unread-count`, {
    credentials: "include",
  });
  return handleResponse(res);
}

export async function fetchNotifications(
  page = 1,
  pageSize = 20,
): Promise<NotificationsResponse> {
  const res = await authFetch(
    `${env.apiBaseUrl}/notifications?page=${page}&page_size=${pageSize}`,
    { credentials: "include" },
  );
  return handleResponse(res);
}

export async function markNotificationActioned(
  notificationId: string,
): Promise<Notification> {
  const res = await authFetch(
    `${env.apiBaseUrl}/notifications/${notificationId}`,
    {
      method: "PATCH",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action_taken: true }),
    },
  );
  return handleResponse(res);
}

export interface EmailPreferencesCategory {
  label: string;
  preferences: Record<string, boolean>;
}

export interface EmailPreferencesResponse {
  categories: Record<string, EmailPreferencesCategory>;
}

export async function fetchEmailPreferences(): Promise<EmailPreferencesResponse> {
  const res = await authFetch(
    `${env.apiBaseUrl}/users/me/notification-preferences`,
    { credentials: "include" },
  );
  return handleResponse(res);
}

export async function updateEmailPreferences(
  preferences: Record<string, boolean>,
): Promise<EmailPreferencesResponse> {
  const res = await authFetch(
    `${env.apiBaseUrl}/users/me/notification-preferences`,
    {
      method: "PATCH",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(preferences),
    },
  );
  return handleResponse(res);
}
