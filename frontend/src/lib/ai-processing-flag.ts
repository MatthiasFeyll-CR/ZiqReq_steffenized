/**
 * In-memory flag for AI processing state per project.
 *
 * Used to bridge the gap when AI processing is triggered before the client
 * subscribes to the project's WebSocket group (e.g. on project creation from the
 * landing page). Components check this on mount, then clear it once they
 * start listening for real-time WebSocket events.
 */

const _pending = new Set<string>();

export function markAiProcessing(projectId: string): void {
  _pending.add(projectId);
}

export function consumeAiProcessing(projectId: string): boolean {
  return _pending.delete(projectId);
}
