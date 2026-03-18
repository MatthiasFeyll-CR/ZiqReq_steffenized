import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import i18n from "@/i18n/config";

const mockListAttachmentsIncludeDeleted = vi.fn();
const mockDeleteAttachment = vi.fn();
const mockRestoreAttachment = vi.fn();
const mockGetAttachmentUrl = vi.fn();
const mockToastSuccess = vi.fn();
const mockToastError = vi.fn();

vi.mock("@/api/attachments", () => ({
  listAttachmentsIncludeDeleted: (...args: unknown[]) => mockListAttachmentsIncludeDeleted(...args),
  deleteAttachment: (...args: unknown[]) => mockDeleteAttachment(...args),
  restoreAttachment: (...args: unknown[]) => mockRestoreAttachment(...args),
  getAttachmentUrl: (...args: unknown[]) => mockGetAttachmentUrl(...args),
}));

vi.mock("react-toastify", () => ({
  toast: {
    success: (...args: unknown[]) => mockToastSuccess(...args),
    error: (...args: unknown[]) => mockToastError(...args),
    info: vi.fn(),
    warning: vi.fn(),
  },
}));

import { AttachmentsModal } from "@/components/workspace/AttachmentsModal";

const PROJECT_ID = "11111111-1111-1111-1111-111111111111";

const MOCK_ATTACHMENTS = [
  {
    id: "att-1",
    filename: "active-file.pdf",
    content_type: "application/pdf",
    size_bytes: 1048576,
    extraction_status: "completed",
    created_at: "2026-01-15T10:00:00Z",
    deleted_at: null,
    message_id: "msg-1",
  },
  {
    id: "att-2",
    filename: "deleted-file.png",
    content_type: "image/png",
    size_bytes: 204800,
    extraction_status: "completed",
    created_at: "2026-01-14T10:00:00Z",
    deleted_at: new Date().toISOString(),
    message_id: "msg-1",
  },
];

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

beforeEach(() => {
  vi.clearAllMocks();
  mockListAttachmentsIncludeDeleted.mockResolvedValue(MOCK_ATTACHMENTS);
});

describe("AttachmentsModal", () => {
  it("renders active and deleted sections", async () => {
    render(
      <AttachmentsModal projectId={PROJECT_ID} open={true} onOpenChange={vi.fn()} />,
    );
    await waitFor(() => {
      expect(screen.getByText("active-file.pdf")).toBeInTheDocument();
      expect(screen.getByText("deleted-file.png")).toBeInTheDocument();
    });
    // Section headers with counts
    expect(screen.getByText(/Active.*\(1\)/)).toBeInTheDocument();
    expect(screen.getByText(/Deleted.*\(1\)/)).toBeInTheDocument();
  });

  it("shows delete note info box", async () => {
    render(
      <AttachmentsModal projectId={PROJECT_ID} open={true} onOpenChange={vi.fn()} />,
    );
    await waitFor(() => {
      expect(screen.getByText(/permanently removed after/i)).toBeInTheDocument();
    });
  });

  it("shows restore button for deleted attachments", async () => {
    render(
      <AttachmentsModal projectId={PROJECT_ID} open={true} onOpenChange={vi.fn()} />,
    );
    await waitFor(() => {
      expect(screen.getByText("deleted-file.png")).toBeInTheDocument();
    });
    expect(screen.getByText(/Restore/)).toBeInTheDocument();
  });

  it("calls restoreAttachment on restore click", async () => {
    const restored = { ...MOCK_ATTACHMENTS[1], deleted_at: null };
    mockRestoreAttachment.mockResolvedValue(restored);

    render(
      <AttachmentsModal projectId={PROJECT_ID} open={true} onOpenChange={vi.fn()} />,
    );
    await waitFor(() => {
      expect(screen.getByText("deleted-file.png")).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText(/Restore/));

    await waitFor(() => {
      expect(mockRestoreAttachment).toHaveBeenCalledWith(PROJECT_ID, "att-2");
      expect(mockToastSuccess).toHaveBeenCalled();
    });
  });

  it("shows delete confirmation on trash click for active attachment", async () => {
    render(
      <AttachmentsModal projectId={PROJECT_ID} open={true} onOpenChange={vi.fn()} />,
    );
    await waitFor(() => {
      expect(screen.getByText("active-file.pdf")).toBeInTheDocument();
    });

    // Click delete button
    const deleteBtn = screen.getByRole("button", { name: /delete attachment/i });
    await userEvent.click(deleteBtn);

    expect(screen.getByText(/Confirm/)).toBeInTheDocument();
  });

  it("calls deleteAttachment on confirm", async () => {
    mockDeleteAttachment.mockResolvedValue(undefined);

    render(
      <AttachmentsModal projectId={PROJECT_ID} open={true} onOpenChange={vi.fn()} />,
    );
    await waitFor(() => {
      expect(screen.getByText("active-file.pdf")).toBeInTheDocument();
    });

    const deleteBtn = screen.getByRole("button", { name: /delete attachment/i });
    await userEvent.click(deleteBtn);
    await userEvent.click(screen.getByText(/Confirm/));

    await waitFor(() => {
      expect(mockDeleteAttachment).toHaveBeenCalledWith(PROJECT_ID, "att-1");
      expect(mockToastSuccess).toHaveBeenCalled();
    });
  });

  it("shows countdown for deleted attachments", async () => {
    render(
      <AttachmentsModal projectId={PROJECT_ID} open={true} onOpenChange={vi.fn()} />,
    );
    await waitFor(() => {
      expect(screen.getByText(/permanently deleted in/i)).toBeInTheDocument();
    });
  });

  it("shows loading state", () => {
    mockListAttachmentsIncludeDeleted.mockReturnValue(new Promise(() => {}));
    render(
      <AttachmentsModal projectId={PROJECT_ID} open={true} onOpenChange={vi.fn()} />,
    );
    // Loader should be visible
    expect(document.querySelector(".animate-spin")).toBeTruthy();
  });

  it("shows empty state when no active attachments", async () => {
    mockListAttachmentsIncludeDeleted.mockResolvedValue([]);
    render(
      <AttachmentsModal projectId={PROJECT_ID} open={true} onOpenChange={vi.fn()} />,
    );
    await waitFor(() => {
      expect(screen.getByText(/no active attachments/i)).toBeInTheDocument();
    });
  });

  it("does not fetch when closed", () => {
    render(
      <AttachmentsModal projectId={PROJECT_ID} open={false} onOpenChange={vi.fn()} />,
    );
    expect(mockListAttachmentsIncludeDeleted).not.toHaveBeenCalled();
  });

  it("shows error toast on restore failure", async () => {
    mockRestoreAttachment.mockRejectedValue(new Error("Restore window has expired"));

    render(
      <AttachmentsModal projectId={PROJECT_ID} open={true} onOpenChange={vi.fn()} />,
    );
    await waitFor(() => {
      expect(screen.getByText("deleted-file.png")).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText(/Restore/));

    await waitFor(() => {
      expect(mockToastError).toHaveBeenCalledWith("Restore window has expired");
    });
  });

  it("shows error toast on delete failure", async () => {
    mockDeleteAttachment.mockRejectedValue(new Error("Delete failed"));

    render(
      <AttachmentsModal projectId={PROJECT_ID} open={true} onOpenChange={vi.fn()} />,
    );
    await waitFor(() => {
      expect(screen.getByText("active-file.pdf")).toBeInTheDocument();
    });

    const deleteBtn = screen.getByRole("button", { name: /delete attachment/i });
    await userEvent.click(deleteBtn);
    await userEvent.click(screen.getByText(/Confirm/));

    await waitFor(() => {
      expect(mockToastError).toHaveBeenCalledWith("Delete failed");
    });
  });
});
