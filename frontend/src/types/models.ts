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
