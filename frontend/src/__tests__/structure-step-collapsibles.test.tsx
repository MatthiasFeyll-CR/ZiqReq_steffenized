import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import i18n from "@/i18n/config";

const mockFetchRequirements = vi.fn();
const mockGenerateRequirements = vi.fn();
const mockPatchRequirements = vi.fn();
const mockListAttachments = vi.fn();

vi.mock("@/api/projects", () => ({
  fetchRequirements: (...args: unknown[]) => mockFetchRequirements(...args),
  generateRequirements: (...args: unknown[]) => mockGenerateRequirements(...args),
  patchRequirements: (...args: unknown[]) => mockPatchRequirements(...args),
}));

vi.mock("@/api/attachments", () => ({
  listAttachments: (...args: unknown[]) => mockListAttachments(...args),
}));

vi.mock("react-toastify", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
    warning: vi.fn(),
  },
}));

vi.mock("@/components/workspace/RequirementsPanel", () => ({
  RequirementsPanel: () => <div data-testid="requirements-panel">Requirements</div>,
}));

vi.mock("@/components/workspace/PDFPreviewPanel", () => ({
  PDFPreviewPanel: () => <div data-testid="pdf-preview-panel">PDF Preview</div>,
}));

vi.mock("@/components/review/SubmitArea", () => ({
  SubmitArea: () => <div data-testid="submit-area">Submit Area</div>,
}));

import { StructureStepView } from "@/pages/ProjectWorkspace/StructureStepView";

const PROJECT_ID = "11111111-1111-1111-1111-111111111111";

const MOCK_DRAFT = {
  structure: [
    { id: "item-1", title: "Epic 1", description: "Desc 1" },
    { id: "item-2", title: "Epic 2", description: "Desc 2" },
  ],
  item_locks: { "item-1": false, "item-2": false },
  allow_information_gaps: false,
  readiness_evaluation: { "item-1": "ready", "item-2": "ready" },
};

const MOCK_ATTACHMENTS = [
  {
    id: "att-1",
    filename: "report.pdf",
    content_type: "application/pdf",
    size_bytes: 1024,
    extraction_status: "completed",
    created_at: "2026-01-15T10:00:00Z",
    deleted_at: null,
    message_id: "msg-1",
  },
];

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

beforeEach(() => {
  vi.clearAllMocks();
  mockFetchRequirements.mockResolvedValue(MOCK_DRAFT);
  mockListAttachments.mockResolvedValue(MOCK_ATTACHMENTS);
});

describe("StructureStepView — collapsible sections", () => {
  const defaultProps = {
    projectId: PROJECT_ID,
    projectType: "software" as const,
    projectState: "open",
    onStepChange: vi.fn(),
  };

  it("renders the structure step view", async () => {
    render(<StructureStepView {...defaultProps} />);
    await waitFor(() => {
      expect(screen.getByTestId("structure-step-view")).toBeInTheDocument();
    });
  });

  it("renders generate button", async () => {
    render(<StructureStepView {...defaultProps} />);
    await waitFor(() => {
      expect(screen.getByTestId("generate-requirements-button")).toBeInTheDocument();
    });
  });

  it("shows Advanced Options collapsible when draft has content", async () => {
    render(<StructureStepView {...defaultProps} />);
    await waitFor(() => {
      expect(screen.getByText(/Advanced Options/)).toBeInTheDocument();
    });
  });

  it("Advanced Options is collapsed by default", async () => {
    render(<StructureStepView {...defaultProps} />);
    await waitFor(() => {
      expect(screen.getByText(/Advanced Options/)).toBeInTheDocument();
    });
    // Find the button that toggles Advanced Options
    const advancedButton = screen.getByText(/Advanced Options/).closest("button");
    expect(advancedButton).toHaveAttribute("aria-expanded", "false");
  });

  it("expands Advanced Options on click", async () => {
    render(<StructureStepView {...defaultProps} />);
    await waitFor(() => {
      expect(screen.getByText(/Advanced Options/)).toBeInTheDocument();
    });

    const advancedButton = screen.getByText(/Advanced Options/).closest("button")!;
    await userEvent.click(advancedButton);
    expect(advancedButton).toHaveAttribute("aria-expanded", "true");
  });

  it("shows Submit section collapsible when project can submit", async () => {
    render(<StructureStepView {...defaultProps} />);
    await waitFor(() => {
      expect(screen.getByText(/Ready to submit/)).toBeInTheDocument();
    });
  });

  it("auto-expands submit section when content appears", async () => {
    render(<StructureStepView {...defaultProps} />);
    await waitFor(() => {
      expect(screen.getByTestId("structure-submit-area")).toBeInTheDocument();
    });
    // The submit section should auto-expand
    const submitButton = screen.getByText(/Ready to submit/).closest("button");
    expect(submitButton).toHaveAttribute("aria-expanded", "true");
  });

  it("does not show Advanced Options when read-only", async () => {
    render(<StructureStepView {...defaultProps} readOnly={true} />);
    await waitFor(() => {
      expect(screen.getByTestId("structure-step-view")).toBeInTheDocument();
    });
    expect(screen.queryByText(/Advanced Options/)).not.toBeInTheDocument();
  });

  it("does not show submit section for non-open state", async () => {
    mockFetchRequirements.mockResolvedValue(MOCK_DRAFT);
    render(<StructureStepView {...defaultProps} projectState="in_review" />);
    await waitFor(() => {
      expect(screen.getByTestId("structure-step-view")).toBeInTheDocument();
    });
    expect(screen.queryByText(/Ready to submit/)).not.toBeInTheDocument();
  });

  it("shows readiness indicator when evaluation exists", async () => {
    render(<StructureStepView {...defaultProps} />);
    await waitFor(() => {
      expect(screen.getByText(/2\/2/)).toBeInTheDocument();
    });
  });

  it("shows attachment selection summary in Advanced Options", async () => {
    render(<StructureStepView {...defaultProps} />);
    await waitFor(() => {
      // After attachments load, summary should show count
      expect(screen.getByText(/Advanced Options/)).toBeInTheDocument();
    });
    // Wait for attachment selector to load and auto-select
    await waitFor(() => {
      expect(screen.getByText(/1 attachments selected/)).toBeInTheDocument();
    });
  });

  it("does not show Advanced Options when draft has no content", async () => {
    mockFetchRequirements.mockResolvedValue({
      ...MOCK_DRAFT,
      structure: [],
    });
    render(<StructureStepView {...defaultProps} />);
    await waitFor(() => {
      expect(screen.getByTestId("structure-step-view")).toBeInTheDocument();
    });
    expect(screen.queryByText(/Advanced Options/)).not.toBeInTheDocument();
  });
});
