import { type APIRequestContext } from "@playwright/test";

/**
 * Base URL for API calls — goes through the Vite proxy so cookies
 * stay on the same origin as the page (localhost:5173).
 */
const BASE_URL = process.env.BASE_URL ?? "http://localhost:5173";

/**
 * Low-level JSON request helper. Routes through the Vite proxy so the
 * session cookie (set on localhost:5173) is included automatically.
 */
async function apiRequest<T = unknown>(
  request: APIRequestContext,
  method: string,
  path: string,
  data?: Record<string, unknown>,
): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const response = await request.fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    data: data ? JSON.stringify(data) : undefined,
  });

  if (!response.ok()) {
    const body = await response.text();
    throw new Error(`API ${method} ${path} failed: ${response.status()} — ${body}`);
  }

  const text = await response.text();
  return text ? (JSON.parse(text) as T) : (undefined as T);
}

// ── Ideas ────────────────────────────────────────────────────────

export interface CreateIdeaResponse {
  id: string;
  title: string;
  state: string;
}

export async function createIdea(
  request: APIRequestContext,
  firstMessage: string,
): Promise<CreateIdeaResponse> {
  return apiRequest<CreateIdeaResponse>(request, "POST", "/api/ideas/", {
    first_message: firstMessage,
  });
}

export async function deleteIdea(
  request: APIRequestContext,
  ideaId: string,
): Promise<void> {
  await apiRequest(request, "DELETE", `/api/ideas/${ideaId}`);
}

export async function restoreIdea(
  request: APIRequestContext,
  ideaId: string,
): Promise<void> {
  await apiRequest(request, "POST", `/api/ideas/${ideaId}/restore`);
}

// ── Review ───────────────────────────────────────────────────────

export async function submitIdea(
  request: APIRequestContext,
  ideaId: string,
  opts?: { message?: string; reviewer_ids?: string[] },
): Promise<{ version_number: number; pdf_url: string; state: string }> {
  return apiRequest(request, "POST", `/api/ideas/${ideaId}/submit`, opts);
}

export async function assignReview(
  request: APIRequestContext,
  ideaId: string,
): Promise<{ message: string }> {
  return apiRequest(request, "POST", `/api/reviews/${ideaId}/assign`, {});
}

export async function acceptReview(
  request: APIRequestContext,
  ideaId: string,
): Promise<void> {
  await apiRequest(request, "POST", `/api/ideas/${ideaId}/review/accept`, {});
}

export async function rejectReview(
  request: APIRequestContext,
  ideaId: string,
): Promise<void> {
  await apiRequest(request, "POST", `/api/ideas/${ideaId}/review/reject`, {});
}

export async function dropReview(
  request: APIRequestContext,
  ideaId: string,
): Promise<void> {
  await apiRequest(request, "POST", `/api/ideas/${ideaId}/review/drop`, {});
}

// ── Collaboration ────────────────────────────────────────────────

export async function sendInvitation(
  request: APIRequestContext,
  ideaId: string,
  inviteeId: string,
): Promise<{ invitation_id: string; status: string }> {
  return apiRequest(request, "POST", `/api/ideas/${ideaId}/collaborators/invite`, {
    invitee_id: inviteeId,
  });
}

export async function acceptInvitation(
  request: APIRequestContext,
  invitationId: string,
): Promise<{ message: string }> {
  return apiRequest(request, "POST", `/api/invitations/${invitationId}/accept`, {});
}

export async function declineInvitation(
  request: APIRequestContext,
  invitationId: string,
): Promise<{ message: string }> {
  return apiRequest(request, "POST", `/api/invitations/${invitationId}/decline`, {});
}

// ── Chat ─────────────────────────────────────────────────────────

export async function sendChatMessage(
  request: APIRequestContext,
  ideaId: string,
  content: string,
): Promise<unknown> {
  return apiRequest(request, "POST", `/api/ideas/${ideaId}/chat`, {
    content,
  });
}

// ── BRD ──────────────────────────────────────────────────────────

export async function generateBrd(
  request: APIRequestContext,
  ideaId: string,
): Promise<unknown> {
  return apiRequest(request, "POST", `/api/ideas/${ideaId}/brd/generate`, {});
}

// ── Notifications ────────────────────────────────────────────────

export async function fetchNotifications(
  request: APIRequestContext,
): Promise<{ results: unknown[]; count: number }> {
  return apiRequest(request, "GET", "/api/notifications/");
}

export async function markAllNotificationsRead(
  request: APIRequestContext,
): Promise<void> {
  await apiRequest(request, "POST", "/api/notifications/mark-all-read", {});
}
