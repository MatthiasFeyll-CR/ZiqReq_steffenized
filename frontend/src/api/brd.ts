import { env } from "@/config/env";

export interface BrdDraft {
  id: string;
  idea_id: string;
  section_title: string | null;
  section_short_description: string | null;
  section_current_workflow: string | null;
  section_affected_department: string | null;
  section_core_capabilities: string | null;
  section_success_criteria: string | null;
  section_locks: Record<string, boolean>;
  allow_information_gaps: boolean;
  readiness_evaluation: Record<string, "ready" | "insufficient">;
  last_evaluated_at: string | null;
}

export type GenerationMode =
  | "full_generation"
  | "selective_regeneration"
  | "section_regeneration";

export async function fetchBrdDraft(ideaId: string): Promise<BrdDraft> {
  const res = await fetch(`${env.apiBaseUrl}/ideas/${ideaId}/brd`, {
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err = new Error(body.message || body.error || `Request failed (${res.status})`);
    (err as Error & { status: number }).status = res.status;
    throw err;
  }
  return res.json();
}

export async function triggerBrdGeneration(
  ideaId: string,
  mode: GenerationMode,
  sectionName?: string,
): Promise<void> {
  const body: Record<string, string> = { mode };
  if (sectionName) body.section_name = sectionName;

  const res = await fetch(`${env.apiBaseUrl}/ideas/${ideaId}/brd/generate`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const resBody = await res.json().catch(() => ({}));
    const err = new Error(resBody.message || resBody.error || `Request failed (${res.status})`);
    (err as Error & { status: number }).status = res.status;
    throw err;
  }
}

export async function patchBrdDraft(
  ideaId: string,
  data: Partial<Pick<BrdDraft, "section_title" | "section_short_description" | "section_current_workflow" | "section_affected_department" | "section_core_capabilities" | "section_success_criteria" | "section_locks" | "allow_information_gaps">>,
): Promise<BrdDraft> {
  const res = await fetch(`${env.apiBaseUrl}/ideas/${ideaId}/brd`, {
    method: "PATCH",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err = new Error(body.message || body.error || `Request failed (${res.status})`);
    (err as Error & { status: number }).status = res.status;
    throw err;
  }
  return res.json();
}

export async function fetchBrdPdf(ideaId: string): Promise<Blob> {
  const res = await fetch(`${env.apiBaseUrl}/ideas/${ideaId}/brd/versions/latest/pdf`, {
    credentials: "include",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const err = new Error(body.message || body.error || `Request failed (${res.status})`);
    (err as Error & { status: number }).status = res.status;
    throw err;
  }
  return res.blob();
}
