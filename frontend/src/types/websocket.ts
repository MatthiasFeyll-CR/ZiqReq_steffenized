export type WebSocketEventType =
  | "chat.message"
  | "chat.reaction"
  | "presence.update"
  | "notification.new";

export interface WebSocketEvent {
  type: WebSocketEventType;
  payload: unknown;
}
