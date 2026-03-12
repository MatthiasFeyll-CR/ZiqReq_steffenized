import { env } from "@/config/env";
import { authFetch } from "@/lib/auth-token";

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

export interface BoardConnection {
  id: string;
  idea_id: string;
  source_node_id: string;
  target_node_id: string;
  label?: string;
  created_at: string;
  updated_at: string;
}

export async function fetchBoardNodes(ideaId: string): Promise<BoardNode[]> {
  const res = await authFetch(
    `${env.apiBaseUrl}/ideas/${ideaId}/board/nodes`,
    { credentials: "include" },
  );
  if (!res.ok) return [];
  const data = await res.json();
  return data.nodes ?? [];
}

export async function fetchBoardConnections(ideaId: string): Promise<BoardConnection[]> {
  const res = await authFetch(
    `${env.apiBaseUrl}/ideas/${ideaId}/board/connections`,
    { credentials: "include" },
  );
  if (!res.ok) return [];
  const data = await res.json();
  return data.connections ?? [];
}

export async function createBoardNode(
  ideaId: string,
  node: {
    id?: string;
    node_type: BoardNode["node_type"];
    title?: string;
    body?: string;
    position_x: number;
    position_y: number;
    width?: number;
    height?: number;
    parent_id?: string | null;
    created_by?: "user" | "ai";
  },
): Promise<BoardNode> {
  const res = await authFetch(
    `${env.apiBaseUrl}/ideas/${ideaId}/board/nodes`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(node),
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

export async function updateBoardNode(
  ideaId: string,
  nodeId: string,
  updates: Partial<Pick<BoardNode, "position_x" | "position_y" | "parent_id" | "is_locked" | "ai_modified_indicator" | "title" | "body" | "width" | "height">>,
): Promise<BoardNode> {
  const res = await authFetch(
    `${env.apiBaseUrl}/ideas/${ideaId}/board/nodes/${nodeId}`,
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
  const res = await authFetch(
    `${env.apiBaseUrl}/ideas/${ideaId}/board/nodes/${nodeId}`,
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
