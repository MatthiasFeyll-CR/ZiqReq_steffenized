import { env } from "@/config/env";

export interface BoardNode {
  id: string;
  node_type: "box" | "group" | "free_text";
  title?: string;
  body?: string;
  position_x: number;
  position_y: number;
  width?: number;
  height?: number;
  parent_id?: string | null;
  is_locked: boolean;
  created_by: "user" | "ai";
  ai_modified_indicator: boolean;
  created_at: string;
  updated_at: string;
}

export async function updateBoardNode(
  ideaId: string,
  nodeId: string,
  updates: Partial<Pick<BoardNode, "position_x" | "position_y" | "parent_id" | "is_locked" | "ai_modified_indicator" | "title" | "body" | "width" | "height">>,
): Promise<BoardNode> {
  const res = await fetch(
    `${env.apiBaseUrl}/ideas/${ideaId}/board/nodes/${nodeId}/`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(updates),
    },
  );
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err = new Error(body.message || body.error || `Request failed (${res.status})`);
    (err as Error & { status: number }).status = res.status;
    throw err;
  }
  return res.json();
}

export async function deleteBoardNode(
  ideaId: string,
  nodeId: string,
): Promise<void> {
  const res = await fetch(
    `${env.apiBaseUrl}/ideas/${ideaId}/board/nodes/${nodeId}/`,
    {
      method: "DELETE",
      credentials: "include",
    },
  );
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err = new Error(body.message || body.error || `Request failed (${res.status})`);
    (err as Error & { status: number }).status = res.status;
    throw err;
  }
}
