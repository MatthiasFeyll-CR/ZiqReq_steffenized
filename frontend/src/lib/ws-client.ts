const WS_BASE = import.meta.env.VITE_WS_BASE_URL ?? "/ws";

export class WebSocketClient {
  private ws: WebSocket | null = null;

  connect(token: string) {
    this.ws = new WebSocket(`${WS_BASE}/?token=${token}`);
  }

  disconnect() {
    this.ws?.close();
    this.ws = null;
  }
}
