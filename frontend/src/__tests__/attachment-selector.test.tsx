import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import i18n from "@/i18n/config";

const mockListAttachments = vi.fn();

vi.mock("@/api/attachments", () => ({
  listAttachments: (...args: unknown[]) => mockListAttachments(...args),
}));

import { AttachmentSelector } from "@/components/workspace/AttachmentSelector";

const PROJECT_ID = "11111111-1111-1111-1111-111111111111";

const MOCK_ATTACHMENTS = [
  {
    id: "att-1",
    filename: "report.pdf",
    content_type: "application/pdf",
    size_bytes: 1048576,
    extraction_status: "completed",
    created_at: "2026-01-15T10:00:00Z",
    deleted_at: null,
    message_id: "msg-1",
  },
  {
    id: "att-2",
    filename: "screenshot.png",
    content_type: "image/png",
    size_bytes: 204800,
    extraction_status: "completed",
    created_at: "2026-01-14T10:00:00Z",
    deleted_at: null,
    message_id: "msg-1",
  },
];

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

beforeEach(() => {
  vi.clearAllMocks();
  mockListAttachments.mockResolvedValue(MOCK_ATTACHMENTS);
});

describe("AttachmentSelector", () => {
  it("renders attachment list after loading", async () => {
    render(
      <AttachmentSelector
        projectId={PROJECT_ID}
        selectedIds={new Set(["att-1", "att-2"])}
        onSelectionChange={vi.fn()}
      />,
    );
    await waitFor(() => {
      expect(screen.getByText("report.pdf")).toBeInTheDocument();
      expect(screen.getByText("screenshot.png")).toBeInTheDocument();
    });
  });

  it("shows select all checkbox", async () => {
    render(
      <AttachmentSelector
        projectId={PROJECT_ID}
        selectedIds={new Set(["att-1", "att-2"])}
        onSelectionChange={vi.fn()}
      />,
    );
    await waitFor(() => {
      expect(screen.getByLabelText("Select All")).toBeInTheDocument();
    });
  });

  it("shows selected count", async () => {
    render(
      <AttachmentSelector
        projectId={PROJECT_ID}
        selectedIds={new Set(["att-1"])}
        onSelectionChange={vi.fn()}
      />,
    );
    await waitFor(() => {
      expect(screen.getByText("(1 selected)")).toBeInTheDocument();
    });
  });

  it("calls onSelectionChange when toggling individual item", async () => {
    const onSelectionChange = vi.fn();
    render(
      <AttachmentSelector
        projectId={PROJECT_ID}
        selectedIds={new Set(["att-1", "att-2"])}
        onSelectionChange={onSelectionChange}
      />,
    );
    await waitFor(() => {
      expect(screen.getByText("report.pdf")).toBeInTheDocument();
    });

    // Uncheck report.pdf
    const checkbox = screen.getByLabelText("report.pdf");
    await userEvent.click(checkbox);

    expect(onSelectionChange).toHaveBeenCalledWith(new Set(["att-2"]));
  });

  it("deselects all when select all is clicked while all selected", async () => {
    const onSelectionChange = vi.fn();
    render(
      <AttachmentSelector
        projectId={PROJECT_ID}
        selectedIds={new Set(["att-1", "att-2"])}
        onSelectionChange={onSelectionChange}
      />,
    );
    await waitFor(() => {
      expect(screen.getByLabelText("Select All")).toBeInTheDocument();
    });

    await userEvent.click(screen.getByLabelText("Select All"));
    expect(onSelectionChange).toHaveBeenCalledWith(new Set());
  });

  it("selects all when select all is clicked while not all selected", async () => {
    const onSelectionChange = vi.fn();
    render(
      <AttachmentSelector
        projectId={PROJECT_ID}
        selectedIds={new Set(["att-1"])}
        onSelectionChange={onSelectionChange}
      />,
    );
    await waitFor(() => {
      expect(screen.getByLabelText("Select All")).toBeInTheDocument();
    });

    await userEvent.click(screen.getByLabelText("Select All"));
    expect(onSelectionChange).toHaveBeenCalledWith(new Set(["att-1", "att-2"]));
  });

  it("calls onAttachmentsLoaded after fetch", async () => {
    const onAttachmentsLoaded = vi.fn();
    render(
      <AttachmentSelector
        projectId={PROJECT_ID}
        selectedIds={new Set()}
        onSelectionChange={vi.fn()}
        onAttachmentsLoaded={onAttachmentsLoaded}
      />,
    );
    await waitFor(() => {
      expect(onAttachmentsLoaded).toHaveBeenCalledWith(MOCK_ATTACHMENTS);
    });
  });

  it("shows empty state when no attachments", async () => {
    mockListAttachments.mockResolvedValue([]);
    render(
      <AttachmentSelector
        projectId={PROJECT_ID}
        selectedIds={new Set()}
        onSelectionChange={vi.fn()}
      />,
    );
    await waitFor(() => {
      expect(screen.getByText(/no attachments uploaded/i)).toBeInTheDocument();
    });
  });

  it("shows loading state", () => {
    mockListAttachments.mockReturnValue(new Promise(() => {}));
    render(
      <AttachmentSelector
        projectId={PROJECT_ID}
        selectedIds={new Set()}
        onSelectionChange={vi.fn()}
      />,
    );
    expect(document.querySelector(".animate-spin")).toBeTruthy();
  });
});
