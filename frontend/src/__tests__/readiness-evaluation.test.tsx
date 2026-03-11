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

import { fetchBrdDraft, patchBrdDraft } from "@/api/brd";
import type { BrdDraft } from "@/api/brd";
import { ReviewTab } from "@/components/workspace/ReviewTab";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

const IDEA_ID = "11111111-1111-1111-1111-111111111111";

function makeDraft(overrides: Partial<BrdDraft> = {}): BrdDraft {
  return {
    id: "22222222-2222-2222-2222-222222222222",
    idea_id: IDEA_ID,
    section_title: "Test Title",
    section_short_description: "Short desc",
    section_current_workflow: "Current workflow",
    section_affected_department: "IT",
    section_core_capabilities: "Capabilities",
    section_success_criteria: "Criteria",
    section_locks: {},
    allow_information_gaps: false,
    readiness_evaluation: {
      title: "ready",
      short_description: "insufficient",
      current_workflow: "insufficient",
      affected_department: "insufficient",
      core_capabilities: "insufficient",
      success_criteria: "insufficient",
    },
    last_evaluated_at: "2026-03-11T12:00:00Z",
    ...overrides,
  };
}

let queryClient: QueryClient;

beforeEach(() => {
  vi.mocked(fetchBrdDraft).mockReset();
  vi.mocked(patchBrdDraft).mockReset();
  vi.useFakeTimers({ shouldAdvanceTime: true });
  queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
});

function renderReviewTab() {
  return render(
    <QueryClientProvider client={queryClient}>
      <ReviewTab ideaId={IDEA_ID} />
    </QueryClientProvider>,
  );
}

async function openEditor(draft?: BrdDraft) {
  const d = draft ?? makeDraft();
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

describe("T-4.8.03: Progress bar reflects readiness", () => {
  it("shows 1 green segment and 5 gray for 1/6 ready", async () => {
    await openEditor();

    const titleSegment = screen.getByTestId("progress-segment-title");
    expect(titleSegment.className).toContain("bg-green-500");

    const grayKeys = [
      "short_description",
      "current_workflow",
      "affected_department",
      "core_capabilities",
      "success_criteria",
    ];
    for (const key of grayKeys) {
      const seg = screen.getByTestId(`progress-segment-${key}`);
      expect(seg.className).toContain("bg-gray-300");
    }
  });

  it("shows 4 green segments when 4/6 are ready", async () => {
    const draft = makeDraft({
      readiness_evaluation: {
        title: "ready",
        short_description: "ready",
        current_workflow: "insufficient",
        affected_department: "ready",
        core_capabilities: "insufficient",
        success_criteria: "ready",
      },
    });
    await openEditor(draft);

    const readyKeys = ["title", "short_description", "affected_department", "success_criteria"];
    for (const key of readyKeys) {
      expect(screen.getByTestId(`progress-segment-${key}`).className).toContain("bg-green-500");
    }

    const insufficientKeys = ["current_workflow", "core_capabilities"];
    for (const key of insufficientKeys) {
      expect(screen.getByTestId(`progress-segment-${key}`).className).toContain("bg-gray-300");
    }
  });

  it("shows all segments gray when allow_information_gaps is true", async () => {
    const draft = makeDraft({
      allow_information_gaps: true,
      readiness_evaluation: {
        title: "ready",
        short_description: "ready",
        current_workflow: "ready",
        affected_department: "ready",
        core_capabilities: "ready",
        success_criteria: "ready",
      },
    });
    await openEditor(draft);

    const allKeys = [
      "title",
      "short_description",
      "current_workflow",
      "affected_department",
      "core_capabilities",
      "success_criteria",
    ];
    for (const key of allKeys) {
      const seg = screen.getByTestId(`progress-segment-${key}`);
      expect(seg.className).toContain("bg-gray-300");
      expect(seg.className).not.toContain("bg-green-500");
    }
  });
});

describe("T-4.8.04: Label updates on readiness change", () => {
  it("shows '1/6 sections ready' when only 1 section is ready", async () => {
    await openEditor();
    expect(screen.getByTestId("progress-label")).toHaveTextContent("1/6 sections ready");
  });

  it("shows '4/6 sections ready' when 4 sections are ready", async () => {
    const draft = makeDraft({
      readiness_evaluation: {
        title: "ready",
        short_description: "ready",
        current_workflow: "insufficient",
        affected_department: "ready",
        core_capabilities: "insufficient",
        success_criteria: "ready",
      },
    });
    await openEditor(draft);
    expect(screen.getByTestId("progress-label")).toHaveTextContent("4/6 sections ready");
  });

  it("shows '6/6 sections ready' when all sections are ready", async () => {
    const draft = makeDraft({
      readiness_evaluation: {
        title: "ready",
        short_description: "ready",
        current_workflow: "ready",
        affected_department: "ready",
        core_capabilities: "ready",
        success_criteria: "ready",
      },
    });
    await openEditor(draft);
    expect(screen.getByTestId("progress-label")).toHaveTextContent("6/6 sections ready");
  });

  it("shows 'Gaps allowed' when allow_information_gaps is true", async () => {
    const draft = makeDraft({ allow_information_gaps: true });
    await openEditor(draft);
    expect(screen.getByTestId("progress-label")).toHaveTextContent("Gaps allowed");
  });
});

describe("UI-4.06: Progress indicator visible in editor", () => {
  it("renders progress indicator below editor header", async () => {
    await openEditor();
    expect(screen.getByTestId("progress-indicator")).toBeInTheDocument();
    expect(screen.getByTestId("progress-bar")).toBeInTheDocument();
    expect(screen.getByTestId("progress-label")).toBeInTheDocument();
  });

  it("renders 6 progress segments", async () => {
    await openEditor();
    const allKeys = [
      "title",
      "short_description",
      "current_workflow",
      "affected_department",
      "core_capabilities",
      "success_criteria",
    ];
    for (const key of allKeys) {
      expect(screen.getByTestId(`progress-segment-${key}`)).toBeInTheDocument();
    }
  });

  it("renders per-section status dots", async () => {
    await openEditor();

    // title is ready -> green dot
    const titleDot = screen.getByTestId("status-dot-title");
    expect(titleDot.className).toContain("bg-green-500");

    // short_description is insufficient -> gray dot
    const descDot = screen.getByTestId("status-dot-short_description");
    expect(descDot.className).toContain("bg-gray-300");
  });

  it("hides status dots when allow_information_gaps is true", async () => {
    const draft = makeDraft({ allow_information_gaps: true });
    await openEditor(draft);

    expect(screen.queryByTestId("status-dot-title")).not.toBeInTheDocument();
  });

  it("shows tooltip data on segments", async () => {
    await openEditor();

    const titleSegment = screen.getByTestId("progress-segment-title");
    expect(titleSegment.getAttribute("data-tooltip")).toBe("Title: Ready");

    const workflowSegment = screen.getByTestId("progress-segment-current_workflow");
    expect(workflowSegment.getAttribute("data-tooltip")).toBe(
      "Current Workflow & Pain Points: Insufficient",
    );
  });
});
