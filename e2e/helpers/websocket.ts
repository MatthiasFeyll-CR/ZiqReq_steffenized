import { WebSocket as WS } from "ws";

const WS_URL = process.env.WS_URL ?? "ws://localhost:8000/ws";

export interface WsMessage {
  type: string;
  idea_id?: string;
  payload?: Record<string, unknown>;
}

/**
 * E2E WebSocket client for verifying real-time events.
 * Uses the raw `ws` library (Node.js) to connect to the gateway
 * independently of the browser.
 *
 * Note: `ws` is a transitive dependency of Playwright.
 */
export class TestWebSocket {
  private ws: WS | null = null;
  private messages: WsMessage[] = [];
  private waiters: Array<{
    predicate: (msg: WsMessage) => boolean;
    resolve: (msg: WsMessage) => void;
    reject: (err: Error) => void;
    timer: ReturnType<typeof setTimeout>;
  }> = [];

  /** Connect as a dev user (token = user UUID in bypass mode). */
  async connect(userId: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.ws = new WS(`${WS_URL}/?token=${userId}`);

      this.ws.on("open", () => resolve());
      this.ws.on("error", (err) => reject(err));

      this.ws.on("message", (raw) => {
        try {
          const msg = JSON.parse(raw.toString()) as WsMessage;
          this.messages.push(msg);
          this.checkWaiters(msg);
        } catch {
          // ignore non-JSON frames
        }
      });
    });
  }

  /** Send a JSON message to the server. */
  send(msg: Record<string, unknown>): void {
    if (!this.ws || this.ws.readyState !== WS.OPEN) {
      throw new Error("WebSocket is not connected");
    }
    this.ws.send(JSON.stringify(msg));
  }

  /** Subscribe to an idea channel. */
  subscribeIdea(ideaId: string): void {
    this.send({ type: "subscribe_idea", idea_id: ideaId });
  }

  /** Unsubscribe from an idea channel. */
  unsubscribeIdea(ideaId: string): void {
    this.send({ type: "unsubscribe_idea", idea_id: ideaId });
  }

  /**
   * Wait for a message matching the predicate.
   * Checks already-received messages first, then waits for new ones.
   */
  async waitForMessage(
    predicate: (msg: WsMessage) => boolean,
    timeoutMs = 10_000,
  ): Promise<WsMessage> {
    // Check buffered messages first
    const existing = this.messages.find(predicate);
    if (existing) return existing;

    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.waiters = this.waiters.filter((w) => w.resolve !== resolve);
        reject(new Error(`WebSocket: timed out waiting for message (${timeoutMs}ms)`));
      }, timeoutMs);

      this.waiters.push({ predicate, resolve, reject, timer });
    });
  }

  /** Wait for a specific event type on a specific idea. */
  async waitForEvent(type: string, ideaId?: string, timeoutMs = 10_000): Promise<WsMessage> {
    return this.waitForMessage(
      (msg) => msg.type === type && (ideaId == null || msg.idea_id === ideaId),
      timeoutMs,
    );
  }

  /** Get all received messages (for debugging). */
  getMessages(): WsMessage[] {
    return [...this.messages];
  }

  /** Clear the message buffer. */
  clearMessages(): void {
    this.messages = [];
  }

  /** Disconnect. */
  disconnect(): void {
    for (const w of this.waiters) {
      clearTimeout(w.timer);
      w.reject(new Error("WebSocket disconnected"));
    }
    this.waiters = [];
    this.ws?.close();
    this.ws = null;
  }

  private checkWaiters(msg: WsMessage): void {
    const matched: typeof this.waiters = [];
    this.waiters = this.waiters.filter((w) => {
      if (w.predicate(msg)) {
        matched.push(w);
        return false;
      }
      return true;
    });
    for (const w of matched) {
      clearTimeout(w.timer);
      w.resolve(msg);
    }
  }
}
