export type WebSocketEventType =
  | "chat.message"
  | "chat.reaction"
  | "board.node_updated"
  | "board.connection_updated"
  | "presence.update"
  | "notification.new";

export interface WebSocketEvent {
  type: WebSocketEventType;
  payload: unknown;
}
