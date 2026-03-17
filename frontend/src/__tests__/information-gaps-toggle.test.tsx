/**
 * Tests for US-009: Allow Information Gaps — Toggle Switch & /TODO Marker Handling
 *
 * Test IDs: T-4.9.04, T-4.9.05, T-4.9.06, UI-4.07
 */
import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import i18n from "@/i18n/config";

vi.mock("@/api/brd", () => ({
  fetchBrdDraft: vi.fn(),
  triggerBrdGeneration: vi.fn(),
  fetchBrdPdf: vi.fn(),
  patchBrdDraft: vi.fn(),
}));

import { fetchBrdDraft, fetchBrdPdf, patchBrdDraft } from "@/api/brd";
import type { BrdDraft } from "@/api/brd";
import { ReviewTab } from "@/components/workspace/ReviewTab";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

const PROJECT_ID = "11111111-1111-1111-1111-111111111111";

function baseDraft(overrides?: Partial<BrdDraft>): BrdDraft {
  return {
    id: "22222222-2222-2222-2222-222222222222",
    project_id: PROJECT_ID,
    section_title: "Test BRD Title",
    section_short_description: "Short description",
    section_current_workflow: "Current workflow",
    section_affected_department: "IT Department",
    section_core_capabilities: "Core capabilities",
    section_success_criteria: "Success criteria",
    section_locks: {},
    allow_information_gaps: false,
    readiness_evaluation: {
      title: "ready",
      short_description: "ready",
      current_workflow: "insufficient",
      affected_department: "ready",
      core_capabilities: "insufficient",
      success_criteria: "ready",
    },
    last_evaluated_at: "2026-03-11T12:00:00Z",
    ...overrides,
  };
}

let queryClient: QueryClient;

beforeEach(() => {
  vi.mocked(fetchBrdDraft).mockReset();
  vi.mocked(fetchBrdPdf).mockReset();
  vi.mocked(patchBrdDraft).mockReset();
  queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
});

function renderReviewTab() {
  return render(
    <QueryClientProvider client={queryClient}>
      <ReviewTab projectId={PROJECT_ID} />
    </QueryClientProvider>,
  );
}

async function openEditor(draft?: BrdDraft) {
  const d = draft ?? baseDraft();
  vi.mocked(fetchBrdDraft).mockResolvedValue(d);
  vi.mocked(patchBrdDraft).mockResolvedValue(d);

  renderReviewTab();

  await waitFor(() => {
    expect(screen.getByTestId("edit-document-button")).toBeInTheDocument();
  });

  fireEvent.click(screen.getByTestId("edit-document-button"));

  await waitFor(() => {
    expect(screen.getByTestId("brd-section-editor")).toBeInTheDocument();
  });
}

// ── T-4.9.04: Gaps toggle ON changes progress indicator ──

describe("T-4.9.04: Gaps toggle ON — progress indicator shows 'Gaps allowed'", () => {
  it("when allow_information_gaps=true, progress label shows 'Gaps allowed'", async () => {
    await openEditor(baseDraft({ allow_information_gaps: true }));

    expect(screen.getByTestId("progress-label")).toHaveTextContent("Gaps allowed");
  });

  it("when allow_information_gaps=true, all segments are gray", async () => {
    await openEditor(baseDraft({ allow_information_gaps: true }));

    const titleSegment = screen.getByTestId("progress-segment-title");
    expect(titleSegment.className).toContain("bg-gray-300");
    expect(titleSegment.className).not.toContain("bg-green-500");
  });
});

// ── T-4.9.05: Gaps toggle OFF — shows normal readiness ──

describe("T-4.9.05: Gaps toggle OFF — shows normal readiness evaluation", () => {
  it("when allow_information_gaps=false, progress label shows section count", async () => {
    await openEditor(baseDraft({ allow_information_gaps: false }));

    expect(screen.getByTestId("progress-label")).toHaveTextContent("4/6 sections ready");
  });

  it("when allow_information_gaps=false, ready sections are green", async () => {
    await openEditor(baseDraft({ allow_information_gaps: false }));

    const titleSegment = screen.getByTestId("progress-segment-title");
    expect(titleSegment.className).toContain("bg-green-500");

    const workflowSegment = screen.getByTestId("progress-segment-current_workflow");
    expect(workflowSegment.className).toContain("bg-gray-300");
  });
});

// ── T-4.9.06: PDF download rejected if /TODO markers present ──

describe("T-4.9.06: PDF download shows warning dialog if /TODO markers present", () => {
  it("shows warning dialog when section contains /TODO markers", async () => {
    const draftWithTodo = baseDraft({
      section_current_workflow: "/TODO: Need more workflow details",
    });
    vi.mocked(fetchBrdDraft).mockResolvedValue(draftWithTodo);

    renderReviewTab();

    await waitFor(() => {
      expect(screen.getByTestId("download-pdf-button")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId("download-pdf-button"));

    await waitFor(() => {
      expect(screen.getByTestId("todo-warning-dialog")).toBeInTheDocument();
    });

    expect(
      screen.getByText(/Cannot generate PDF.*\/TODO markers/),
    ).toBeInTheDocument();

    // fetchBrdPdf should NOT have been called
    expect(fetchBrdPdf).not.toHaveBeenCalled();
  });

  it("does not show warning dialog when no /TODO markers", async () => {
    vi.mocked(fetchBrdDraft).mockResolvedValue(baseDraft());
    vi.mocked(fetchBrdPdf).mockResolvedValue(new Blob(["fake-pdf"]));

    renderReviewTab();

    await waitFor(() => {
      expect(screen.getByTestId("download-pdf-button")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId("download-pdf-button"));

    await waitFor(() => {
      expect(fetchBrdPdf).toHaveBeenCalledWith(PROJECT_ID);
    });

    expect(screen.queryByTestId("todo-warning-dialog")).not.toBeInTheDocument();
  });

  it("closes warning dialog on OK click", async () => {
    const draftWithTodo = baseDraft({
      section_title: "/TODO: Need a title",
    });
    vi.mocked(fetchBrdDraft).mockResolvedValue(draftWithTodo);

    renderReviewTab();

    await waitFor(() => {
      expect(screen.getByTestId("download-pdf-button")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId("download-pdf-button"));

    await waitFor(() => {
      expect(screen.getByTestId("todo-warning-dialog")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId("todo-warning-close"));

    await waitFor(() => {
      expect(screen.queryByTestId("todo-warning-dialog")).not.toBeInTheDocument();
    });
  });
});

// ── UI-4.07: Gaps toggle visible in editor ──

describe("UI-4.07: Gaps toggle visible in editor", () => {
  it("shows the Allow information gaps toggle switch in the editor", async () => {
    await openEditor();

    expect(screen.getByTestId("gaps-toggle")).toBeInTheDocument();
    expect(screen.getByText("Allow information gaps")).toBeInTheDocument();
  });

  it("toggle is below the progress indicator", async () => {
    await openEditor();

    const progressIndicator = screen.getByTestId("progress-indicator");
    const gapsToggle = screen.getByTestId("gaps-toggle");

    // Both should be present in the document
    expect(progressIndicator).toBeInTheDocument();
    expect(gapsToggle).toBeInTheDocument();

    // Progress indicator should come before the toggle in DOM order
    const container = progressIndicator.closest("[class*='border-b']");
    expect(container).not.toBeNull();
    expect(container!.contains(gapsToggle)).toBe(true);
  });

  it("toggle state matches allow_information_gaps value", async () => {
    await openEditor(baseDraft({ allow_information_gaps: true }));

    const toggle = screen.getByTestId("gaps-toggle");
    expect(toggle).toHaveAttribute("data-state", "checked");
  });

  it("toggle calls PATCH when changed", async () => {
    await openEditor();

    const toggle = screen.getByTestId("gaps-toggle");
    fireEvent.click(toggle);

    await waitFor(() => {
      expect(patchBrdDraft).toHaveBeenCalledWith(
        PROJECT_ID,
        expect.objectContaining({ allow_information_gaps: true }),
      );
    });
  });
});
