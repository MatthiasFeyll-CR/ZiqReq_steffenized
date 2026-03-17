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

import { fetchBrdDraft, triggerBrdGeneration, patchBrdDraft } from "@/api/brd";
import type { BrdDraft } from "@/api/brd";
import { ReviewTab } from "@/components/workspace/ReviewTab";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

const PROJECT_ID = "11111111-1111-1111-1111-111111111111";

function populatedDraft(): BrdDraft {
  return {
    id: "22222222-2222-2222-2222-222222222222",
    project_id: PROJECT_ID,
    section_title: "Test BRD Title",
    section_short_description: "Short description",
    section_current_workflow: "Current workflow",
    section_affected_department: "IT Department",
    section_core_capabilities: "Core capabilities",
    section_success_criteria: "Success criteria",
    section_locks: { title: true, short_description: false },
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
  };
}

let queryClient: QueryClient;

beforeEach(() => {
  vi.mocked(fetchBrdDraft).mockReset();
  vi.mocked(triggerBrdGeneration).mockReset();
  vi.mocked(patchBrdDraft).mockReset();
  vi.useFakeTimers({ shouldAdvanceTime: true });
  queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
});

function renderReviewTab(projectId = PROJECT_ID) {
  return render(
    <QueryClientProvider client={queryClient}>
      <ReviewTab projectId={projectId} />
    </QueryClientProvider>,
  );
}

async function openEditor() {
  vi.mocked(fetchBrdDraft).mockResolvedValue(populatedDraft());
  vi.mocked(patchBrdDraft).mockResolvedValue(populatedDraft());

  renderReviewTab();

  await waitFor(() => {
    expect(screen.getByTestId("edit-document-button")).toBeInTheDocument();
  });

  fireEvent.click(screen.getByTestId("edit-document-button"));

  await waitFor(() => {
    expect(screen.getByTestId("brd-section-editor")).toBeInTheDocument();
  });
}

describe("UI-4.03: Editor slides in", () => {
  it("opens BRD section editor when Edit Document is clicked", async () => {
    await openEditor();
    expect(screen.getByTestId("brd-section-editor")).toBeInTheDocument();
  });

  it("shows Edit Document button only when BRD has content", async () => {
    vi.mocked(fetchBrdDraft).mockResolvedValue(populatedDraft());

    renderReviewTab();

    await waitFor(() => {
      expect(screen.getByTestId("edit-document-button")).toBeInTheDocument();
    });
  });

  it("closes editor when close button is clicked", async () => {
    await openEditor();

    fireEvent.click(screen.getByTestId("editor-close-button"));

    await waitFor(() => {
      expect(screen.queryByTestId("brd-section-editor")).not.toBeInTheDocument();
    });
  });
});

describe("UI-4.04: Section fields render with labels", () => {
  it("shows all 6 section fields with labels", async () => {
    await openEditor();

    expect(screen.getByTestId("section-field-title")).toBeInTheDocument();
    expect(screen.getByTestId("section-field-short_description")).toBeInTheDocument();
    expect(screen.getByTestId("section-field-current_workflow")).toBeInTheDocument();
    expect(screen.getByTestId("section-field-affected_department")).toBeInTheDocument();
    expect(screen.getByTestId("section-field-core_capabilities")).toBeInTheDocument();
    expect(screen.getByTestId("section-field-success_criteria")).toBeInTheDocument();

    expect(screen.getByText("1. Title")).toBeInTheDocument();
    expect(screen.getByText("2. Short Description")).toBeInTheDocument();
    expect(screen.getByText("3. Current Workflow & Pain Points")).toBeInTheDocument();
    expect(screen.getByText("4. Affected Department")).toBeInTheDocument();
    expect(screen.getByText("5. Core Capabilities")).toBeInTheDocument();
    expect(screen.getByText("6. Success Criteria")).toBeInTheDocument();
  });
});

describe("T-4.4.04: Lock toggle updates section_locks", () => {
  it("calls PATCH when lock icon is toggled", async () => {
    await openEditor();

    // short_description is unlocked, click to lock it
    const lockToggle = screen.getByTestId("lock-toggle-short_description");
    fireEvent.click(lockToggle);

    await waitFor(() => {
      expect(patchBrdDraft).toHaveBeenCalledWith(
        PROJECT_ID,
        expect.objectContaining({
          section_locks: expect.objectContaining({ short_description: true }),
        }),
      );
    });
  });
});

describe("T-4.4.05: Regenerate triggers section_regeneration", () => {
  it("calls POST /generate with section_regeneration when regenerate clicked", async () => {
    vi.mocked(triggerBrdGeneration).mockResolvedValue(undefined);
    await openEditor();

    // short_description is unlocked and has content, so regenerate icon should show
    const regenButton = screen.getByTestId("regenerate-short_description");
    fireEvent.click(regenButton);

    await waitFor(() => {
      expect(triggerBrdGeneration).toHaveBeenCalledWith(
        PROJECT_ID,
        "section_regeneration",
        "short_description",
      );
    });
  });

  it("does not show regenerate icon for locked sections", async () => {
    await openEditor();

    // title is locked — no regenerate button
    expect(screen.queryByTestId("regenerate-title")).not.toBeInTheDocument();
  });
});

describe("T-4.4.06: Auto-save on blur", () => {
  it("calls PATCH on textarea blur", async () => {
    await openEditor();

    const textarea = screen.getByTestId("section-textarea-title");
    fireEvent.change(textarea, { target: { value: "Updated Title" } });

    // Advance timer past debounce
    vi.advanceTimersByTime(400);

    fireEvent.blur(textarea);

    await waitFor(() => {
      expect(patchBrdDraft).toHaveBeenCalledWith(
        PROJECT_ID,
        expect.objectContaining({ section_title: "Updated Title" }),
      );
    });
  });
});

describe("T-4.8.02: Progress indicator updates", () => {
  it("shows progress indicator with correct readiness count", async () => {
    await openEditor();

    expect(screen.getByTestId("progress-indicator")).toBeInTheDocument();
    expect(screen.getByTestId("progress-label")).toHaveTextContent("4/6 sections ready");
  });

  it("shows green segments for ready sections", async () => {
    await openEditor();

    const titleSegment = screen.getByTestId("progress-segment-title");
    expect(titleSegment.className).toContain("bg-green-500");

    const workflowSegment = screen.getByTestId("progress-segment-current_workflow");
    expect(workflowSegment.className).toContain("bg-gray-300");
  });
});

describe("T-4.9.03: Gaps toggle works", () => {
  it("shows Allow information gaps toggle", async () => {
    await openEditor();

    expect(screen.getByTestId("gaps-toggle")).toBeInTheDocument();
    expect(screen.getByText("Allow information gaps")).toBeInTheDocument();
  });

  it("calls PATCH with allow_information_gaps when toggled", async () => {
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
