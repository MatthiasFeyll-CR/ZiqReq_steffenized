import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import i18n from "@/i18n/config";

vi.mock("@/api/brd", () => ({
  fetchBrdDraft: vi.fn(),
  triggerBrdGeneration: vi.fn(),
  fetchBrdPdf: vi.fn(),
}));

import { fetchBrdDraft, triggerBrdGeneration } from "@/api/brd";
import type { BrdDraft } from "@/api/brd";
import { ReviewTab } from "@/components/workspace/ReviewTab";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

const PROJECT_ID = "11111111-1111-1111-1111-111111111111";

function emptyDraft(): BrdDraft {
  return {
    id: "22222222-2222-2222-2222-222222222222",
    project_id: PROJECT_ID,
    section_title: null,
    section_short_description: null,
    section_current_workflow: null,
    section_affected_department: null,
    section_core_capabilities: null,
    section_success_criteria: null,
    section_locks: {},
    allow_information_gaps: false,
    readiness_evaluation: {},
    last_evaluated_at: null,
  };
}

function populatedDraft(): BrdDraft {
  return {
    ...emptyDraft(),
    section_title: "Test BRD Title",
    section_short_description: "Short description of the BRD",
    section_current_workflow: "Current workflow description",
    section_affected_department: "IT Department",
    section_core_capabilities: "Core capabilities here",
    section_success_criteria: "Success criteria defined",
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

describe("T-4.5.01: PDF preview renders", () => {
  it("shows BRD content state when draft has content", async () => {
    vi.mocked(fetchBrdDraft).mockResolvedValue(populatedDraft());

    renderReviewTab();

    await waitFor(() => {
      expect(screen.getByTestId("brd-content-preview")).toBeInTheDocument();
    });
  });
});

describe("T-4.5.02: action bar visible", () => {
  it("shows Download PDF and Generate buttons", async () => {
    vi.mocked(fetchBrdDraft).mockResolvedValue(emptyDraft());

    renderReviewTab();

    await waitFor(() => {
      expect(screen.getByTestId("review-action-bar")).toBeInTheDocument();
    });

    expect(screen.getByTestId("download-pdf-button")).toBeInTheDocument();
    expect(screen.getByTestId("generate-brd-button")).toBeInTheDocument();
  });

  it("disables Download PDF when no BRD content exists", async () => {
    vi.mocked(fetchBrdDraft).mockResolvedValue(emptyDraft());

    renderReviewTab();

    await waitFor(() => {
      expect(screen.getByTestId("download-pdf-button")).toBeInTheDocument();
    });

    expect(screen.getByTestId("download-pdf-button")).toBeDisabled();
  });

  it("enables Download PDF when BRD content exists", async () => {
    vi.mocked(fetchBrdDraft).mockResolvedValue(populatedDraft());

    renderReviewTab();

    await waitFor(() => {
      expect(screen.getByTestId("download-pdf-button")).toBeInTheDocument();
    });

    expect(screen.getByTestId("download-pdf-button")).not.toBeDisabled();
  });
});

describe("T-4.5.03: Generate button triggers full_generation", () => {
  it("calls triggerBrdGeneration on click", async () => {
    vi.mocked(fetchBrdDraft).mockResolvedValue(emptyDraft());
    vi.mocked(triggerBrdGeneration).mockResolvedValue(undefined);

    renderReviewTab();

    await waitFor(() => {
      expect(screen.getByTestId("generate-brd-button")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId("generate-brd-button"));

    await waitFor(() => {
      expect(triggerBrdGeneration).toHaveBeenCalledWith(PROJECT_ID, "full_generation");
    });
  });
});

describe("UI-4.01: Review tab appears in workspace", () => {
  it("renders the review tab container", async () => {
    vi.mocked(fetchBrdDraft).mockResolvedValue(emptyDraft());

    renderReviewTab();

    await waitFor(() => {
      expect(screen.getByTestId("review-tab")).toBeInTheDocument();
    });
  });
});

describe("UI-4.02: empty state when no BRD", () => {
  it("shows empty state message when no BRD content exists", async () => {
    vi.mocked(fetchBrdDraft).mockResolvedValue(emptyDraft());

    renderReviewTab();

    await waitFor(() => {
      expect(screen.getByText("No BRD generated yet")).toBeInTheDocument();
    });

    expect(
      screen.getByText("Click Generate to create your first BRD."),
    ).toBeInTheDocument();
  });
});

describe("ReviewTab loading state", () => {
  it("shows loading skeleton while fetching draft", () => {
    vi.mocked(fetchBrdDraft).mockReturnValue(new Promise(() => {}));

    renderReviewTab();

    expect(screen.getByTestId("review-tab-loading")).toBeInTheDocument();
  });
});
