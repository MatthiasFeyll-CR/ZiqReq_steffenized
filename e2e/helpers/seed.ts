import { type APIRequestContext } from "@playwright/test";
import { DEV_USERS, type DevUserKey } from "./auth";
import {
  createIdea,
  submitIdea,
  assignReview,
  acceptReview,
  rejectReview,
  dropReview,
  sendInvitation,
  acceptInvitation,
  sendChatMessage,
} from "./api";

/**
 * Base URL — goes through the Vite proxy so cookies stay on the same origin.
 */
const BASE_URL = process.env.BASE_URL ?? "http://localhost:5173";

/**
 * Ensure the request context is authenticated as the given dev user.
 * Call this before seed operations that need a specific user session.
 */
export async function authenticateRequest(
  request: APIRequestContext,
  user: DevUserKey,
): Promise<void> {
  const devUser = DEV_USERS[user];
  const res = await request.post(`${BASE_URL}/api/auth/dev-login`, {
    data: { user_id: devUser.id },
  });
  if (!res.ok()) {
    throw new Error(`Seed auth failed for ${user}: ${res.status()}`);
  }
}

// ── Idea in specific states ──────────────────────────────────────

export interface SeededIdea {
  id: string;
  title: string;
  state: string;
}

/** Create an idea in the "open" state. */
export async function seedOpenIdea(
  request: APIRequestContext,
  message = "E2E test idea",
): Promise<SeededIdea> {
  const idea = await createIdea(request, message);
  return { id: idea.id, title: idea.title, state: "open" };
}

/** Create an idea and submit it for review ("in_review"). */
export async function seedInReviewIdea(
  request: APIRequestContext,
  message = "E2E test idea for review",
): Promise<SeededIdea> {
  const idea = await createIdea(request, message);
  await submitIdea(request, idea.id);
  return { id: idea.id, title: idea.title, state: "in_review" };
}

/**
 * Create an idea, submit it, assign a reviewer, and accept it.
 * Requires switching to a reviewer user for the accept step.
 *
 * Defaults: owner=user1 (basic), reviewer=user3 (reviewer role)
 */
export async function seedAcceptedIdea(
  request: APIRequestContext,
  opts?: { owner?: DevUserKey; reviewer?: DevUserKey; message?: string },
): Promise<SeededIdea> {
  const owner = opts?.owner ?? "user1";
  const reviewer = opts?.reviewer ?? "user3";

  // Create + submit as owner
  await authenticateRequest(request, owner);
  const idea = await createIdea(request, opts?.message ?? "E2E accepted idea");
  await submitIdea(request, idea.id);

  // Assign + accept as reviewer
  await authenticateRequest(request, reviewer);
  await assignReview(request, idea.id);
  await acceptReview(request, idea.id);

  // Re-auth as owner for subsequent operations
  await authenticateRequest(request, owner);
  return { id: idea.id, title: idea.title, state: "accepted" };
}

/** Create an idea, submit, assign, and reject it. */
export async function seedRejectedIdea(
  request: APIRequestContext,
  opts?: { owner?: DevUserKey; reviewer?: DevUserKey; message?: string },
): Promise<SeededIdea> {
  const owner = opts?.owner ?? "user1";
  const reviewer = opts?.reviewer ?? "user3";

  await authenticateRequest(request, owner);
  const idea = await createIdea(request, opts?.message ?? "E2E rejected idea");
  await submitIdea(request, idea.id);

  await authenticateRequest(request, reviewer);
  await assignReview(request, idea.id);
  await rejectReview(request, idea.id);

  await authenticateRequest(request, owner);
  return { id: idea.id, title: idea.title, state: "rejected" };
}

/** Create an idea, submit, assign, and drop it. */
export async function seedDroppedIdea(
  request: APIRequestContext,
  opts?: { owner?: DevUserKey; reviewer?: DevUserKey; message?: string },
): Promise<SeededIdea> {
  const owner = opts?.owner ?? "user1";
  const reviewer = opts?.reviewer ?? "user3";

  await authenticateRequest(request, owner);
  const idea = await createIdea(request, opts?.message ?? "E2E dropped idea");
  await submitIdea(request, idea.id);

  await authenticateRequest(request, reviewer);
  await assignReview(request, idea.id);
  await dropReview(request, idea.id);

  await authenticateRequest(request, owner);
  return { id: idea.id, title: idea.title, state: "dropped" };
}

// ── Ideas with content ───────────────────────────────────────────

/** Create an idea with chat messages. */
export async function seedIdeaWithChat(
  request: APIRequestContext,
  messages: string[],
): Promise<SeededIdea> {
  const idea = await createIdea(request, messages[0] ?? "E2E chat idea");
  for (const msg of messages.slice(1)) {
    await sendChatMessage(request, idea.id, msg);
  }
  return { id: idea.id, title: idea.title, state: "open" };
}

/** Create an idea and invite a collaborator. Returns the idea and invitation ID. */
export async function seedIdeaWithCollaborator(
  request: APIRequestContext,
  opts?: { owner?: DevUserKey; collaborator?: DevUserKey },
): Promise<SeededIdea & { invitationId: string }> {
  const owner = opts?.owner ?? "user1";
  const collaborator = opts?.collaborator ?? "user2";
  const idea = await createIdea(request, "E2E collab idea");
  const inv = await sendInvitation(request, idea.id, DEV_USERS[collaborator].id);

  // Accept invitation as the collaborator
  await authenticateRequest(request, collaborator);
  await acceptInvitation(request, inv.invitation_id);

  // Re-auth as owner
  await authenticateRequest(request, owner);
  return { id: idea.id, title: idea.title, state: "open", invitationId: inv.invitation_id };
}
