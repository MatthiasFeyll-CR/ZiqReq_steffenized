/**
 * In-memory flag for AI processing state per idea.
 *
 * Used to bridge the gap when AI processing is triggered before the client
 * subscribes to the idea's WebSocket group (e.g. on idea creation from the
 * landing page). Components check this on mount, then clear it once they
 * start listening for real-time WebSocket events.
 */

const _pending = new Set<string>();

export function markAiProcessing(ideaId: string): void {
  _pending.add(ideaId);
}

export function consumeAiProcessing(ideaId: string): boolean {
  return _pending.delete(ideaId);
}
