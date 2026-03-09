export interface Idea {
  id: string;
  title: string;
  state: "open" | "in_review" | "accepted" | "dropped" | "rejected";
  visibility: "private" | "collaborating";
  agentMode: "interactive" | "silent";
  ownerId: string;
  coOwnerId: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface ChatMessage {
  id: string;
  ideaId: string;
  senderType: "user" | "ai";
  senderId: string | null;
  aiAgent: string | null;
  content: string;
  messageType: "regular" | "delegation";
  createdAt: string;
}

export interface BoardNode {
  id: string;
  ideaId: string;
  nodeType: "box" | "group" | "free_text";
  title: string | null;
  body: string | null;
  positionX: number;
  positionY: number;
  width: number | null;
  height: number | null;
  parentId: string | null;
  isLocked: boolean;
  createdBy: "user" | "ai";
  createdAt: string;
}

export interface BoardConnection {
  id: string;
  sourceNodeId: string;
  targetNodeId: string;
  label: string | null;
}
