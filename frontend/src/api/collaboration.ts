import { env } from "@/config/env";
import { authFetch } from "@/lib/auth-token";

export interface UserSearchResult {
  id: string;
  display_name: string;
  email: string;
  roles: string[];
}

export interface CollaboratorUser {
  id: string;
  display_name: string;
  email: string;
  joined_at?: string;
}

export interface CollaboratorsResponse {
  owner: CollaboratorUser;
  collaborators: CollaboratorUser[];
}

export interface PendingInvitation {
  id: string;
  invitee: { id: string; display_name: string; email: string };
  created_at: string;
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err = new Error(body.message || body.error || `Request failed (${res.status})`);
    (err as Error & { status: number }).status = res.status;
    throw err;
  }
  return res.json();
}

export async function searchUsers(query: string): Promise<UserSearchResult[]> {
  const res = await authFetch(
    `${env.apiBaseUrl}/users/search?q=${encodeURIComponent(query)}`,
    { credentials: "include" },
  );
  return handleResponse<UserSearchResult[]>(res);
}

export async function sendInvitation(
  projectId: string,
  inviteeId: string,
): Promise<{ invitation_id: string; status: string }> {
  const res = await authFetch(
    `${env.apiBaseUrl}/projects/${projectId}/collaborators/invite`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ invitee_id: inviteeId }),
    },
  );
  return handleResponse(res);
}

export async function fetchCollaborators(
  projectId: string,
): Promise<CollaboratorsResponse> {
  const res = await authFetch(
    `${env.apiBaseUrl}/projects/${projectId}/collaborators`,
    { credentials: "include" },
  );
  return handleResponse<CollaboratorsResponse>(res);
}

export async function removeCollaborator(
  projectId: string,
  userId: string,
): Promise<void> {
  const res = await authFetch(
    `${env.apiBaseUrl}/projects/${projectId}/collaborators/${userId}`,
    { method: "DELETE", credentials: "include" },
  );
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err = new Error(body.message || body.error || `Request failed (${res.status})`);
    (err as Error & { status: number }).status = res.status;
    throw err;
  }
}

export async function transferOwnership(
  projectId: string,
  newOwnerId: string,
): Promise<{ message: string }> {
  const res = await authFetch(
    `${env.apiBaseUrl}/projects/${projectId}/transfer-ownership`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ new_owner_id: newOwnerId }),
    },
  );
  return handleResponse(res);
}

export async function fetchPendingInvitations(
  projectId: string,
): Promise<{ invitations: PendingInvitation[] }> {
  const res = await authFetch(
    `${env.apiBaseUrl}/projects/${projectId}/invitations`,
    { credentials: "include" },
  );
  return handleResponse(res);
}

export async function revokeInvitation(
  invitationId: string,
): Promise<{ message: string }> {
  const res = await authFetch(
    `${env.apiBaseUrl}/invitations/${invitationId}/revoke`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({}),
    },
  );
  return handleResponse(res);
}

export async function acceptInvitation(
  invitationId: string,
): Promise<{ message: string }> {
  const res = await authFetch(
    `${env.apiBaseUrl}/invitations/${invitationId}/accept`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({}),
    },
  );
  return handleResponse(res);
}

export async function leaveProject(
  projectId: string,
): Promise<{ message: string }> {
  const res = await authFetch(
    `${env.apiBaseUrl}/projects/${projectId}/leave`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({}),
    },
  );
  return handleResponse(res);
}

export async function declineInvitation(
  invitationId: string,
): Promise<{ message: string }> {
  const res = await authFetch(
    `${env.apiBaseUrl}/invitations/${invitationId}/decline`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({}),
    },
  );
  return handleResponse(res);
}

export interface BulkInviteResult {
  invitee_id: string;
  invitation_id?: string;
  status: string;
  message?: string;
}

export async function sendBulkInvitations(
  projectId: string,
  inviteeIds: string[],
): Promise<{ results: BulkInviteResult[] }> {
  const res = await authFetch(
    `${env.apiBaseUrl}/projects/${projectId}/collaborators/invite`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ invitee_ids: inviteeIds }),
    },
  );
  return handleResponse(res);
}

export async function generateShareLink(
  projectId: string,
): Promise<{ share_link_token: string; share_url: string }> {
  const res = await authFetch(
    `${env.apiBaseUrl}/projects/${projectId}/share-link`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({}),
    },
  );
  return handleResponse(res);
}
