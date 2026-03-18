import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import i18n from "@/i18n/config";

const mockFetchAdminAttachments = vi.fn();
const mockDeleteAdminAttachment = vi.fn();
const mockRestoreAdminAttachment = vi.fn();
const mockToastSuccess = vi.fn();
const mockToastError = vi.fn();

vi.mock("@/api/admin", () => ({
  fetchAdminAttachments: (...args: unknown[]) => mockFetchAdminAttachments(...args),
  deleteAdminAttachment: (...args: unknown[]) => mockDeleteAdminAttachment(...args),
  restoreAdminAttachment: (...args: unknown[]) => mockRestoreAdminAttachment(...args),
}));

vi.mock("react-toastify", () => ({
  toast: {
    success: (...args: unknown[]) => mockToastSuccess(...args),
    error: (...args: unknown[]) => mockToastError(...args),
    info: vi.fn(),
    warning: vi.fn(),
  },
}));

vi.mock("@/config/env", () => ({
  env: { apiBaseUrl: "http://localhost/api" },
}));

import { AttachmentsTab } from "@/features/admin/AttachmentsTab";

const MOCK_RESPONSE = {
  results: [
    {
      id: "att-1",
      filename: "report.pdf",
      content_type: "application/pdf",
      size_bytes: 1048576,
      extraction_status: "completed",
      created_at: "2026-01-15T10:00:00Z",
      deleted_at: null,
      message_id: null,
      project: { id: "proj-1", title: "Project Alpha" },
    },
    {
      id: "att-2",
      filename: "screenshot.png",
      content_type: "image/png",
      size_bytes: 204800,
      extraction_status: "completed",
      created_at: "2026-01-14T10:00:00Z",
      deleted_at: "2026-01-16T10:00:00Z",
      message_id: "msg-1",
      project: { id: "proj-1", title: "Project Alpha" },
    },
  ],
  count: 2,
  next: null,
  previous: null,
  stats: { total_size_bytes: 1253376, total_count: 2 },
};

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

beforeEach(() => {
  vi.clearAllMocks();
  mockFetchAdminAttachments.mockResolvedValue(MOCK_RESPONSE);
});

describe("AttachmentsTab", () => {
  it("renders stats cards", async () => {
    render(<AttachmentsTab />);
    await waitFor(() => {
      expect(screen.getByText("2")).toBeInTheDocument(); // total_count
    });
  });

  it("renders attachment rows after loading", async () => {
    render(<AttachmentsTab />);
    await waitFor(() => {
      expect(screen.getByText("report.pdf")).toBeInTheDocument();
      expect(screen.getByText("screenshot.png")).toBeInTheDocument();
    });
  });

  it("shows deleted badge for soft-deleted attachments", async () => {
    render(<AttachmentsTab />);
    await waitFor(() => {
      expect(screen.getByText("screenshot.png")).toBeInTheDocument();
    });
    // screenshot.png is deleted, should have a badge
    const row = screen.getByTestId("admin-attachment-row-att-2");
    expect(row).toBeInTheDocument();
    expect(row.querySelector(".line-through")).toBeTruthy();
  });

  it("renders search input", async () => {
    render(<AttachmentsTab />);
    await waitFor(() => {
      expect(screen.getByTestId("admin-attachments-search")).toBeInTheDocument();
    });
  });

  it("renders filter select", async () => {
    render(<AttachmentsTab />);
    await waitFor(() => {
      expect(screen.getByTestId("admin-attachments-filter")).toBeInTheDocument();
    });
  });

  it("shows restore button for deleted attachments", async () => {
    render(<AttachmentsTab />);
    await waitFor(() => {
      expect(screen.getByText("screenshot.png")).toBeInTheDocument();
    });
    // The deleted row should have a Restore button
    const restoreBtn = screen.getByRole("button", { name: /restore/i });
    expect(restoreBtn).toBeInTheDocument();
  });

  it("calls restore API on restore click", async () => {
    mockRestoreAdminAttachment.mockResolvedValue(undefined);
    render(<AttachmentsTab />);
    await waitFor(() => {
      expect(screen.getByText("screenshot.png")).toBeInTheDocument();
    });

    const restoreBtn = screen.getByRole("button", { name: /restore/i });
    await userEvent.click(restoreBtn);

    await waitFor(() => {
      expect(mockRestoreAdminAttachment).toHaveBeenCalledWith("att-2");
      expect(mockToastSuccess).toHaveBeenCalled();
    });
  });

  it("shows delete confirmation on trash click", async () => {
    render(<AttachmentsTab />);
    await waitFor(() => {
      expect(screen.getByText("report.pdf")).toBeInTheDocument();
    });

    // Click the delete icon button for the active attachment
    const deleteBtn = screen.getByRole("button", { name: /delete/i });
    await userEvent.click(deleteBtn);

    // Confirm button should appear
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /confirm/i })).toBeInTheDocument();
    });
  });

  it("calls delete API on confirm", async () => {
    mockDeleteAdminAttachment.mockResolvedValue(undefined);
    render(<AttachmentsTab />);
    await waitFor(() => {
      expect(screen.getByText("report.pdf")).toBeInTheDocument();
    });

    const deleteBtn = screen.getByRole("button", { name: /delete/i });
    await userEvent.click(deleteBtn);

    const confirmBtn = await screen.findByRole("button", { name: /confirm/i });
    await userEvent.click(confirmBtn);

    await waitFor(() => {
      expect(mockDeleteAdminAttachment).toHaveBeenCalledWith("att-1");
      expect(mockToastSuccess).toHaveBeenCalled();
    });
  });

  it("shows loading state initially", () => {
    mockFetchAdminAttachments.mockReturnValue(new Promise(() => {})); // never resolves
    render(<AttachmentsTab />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it("shows empty state when no results", async () => {
    mockFetchAdminAttachments.mockResolvedValue({
      results: [],
      count: 0,
      next: null,
      previous: null,
      stats: { total_size_bytes: 0, total_count: 0 },
    });
    render(<AttachmentsTab />);
    await waitFor(() => {
      expect(screen.getByText(/no attachments found/i)).toBeInTheDocument();
    });
  });

  it("shows pagination when more than one page", async () => {
    mockFetchAdminAttachments.mockResolvedValue({
      ...MOCK_RESPONSE,
      count: 70,
      next: 2,
    });
    render(<AttachmentsTab />);
    await waitFor(() => {
      expect(screen.getByText("1 / 2")).toBeInTheDocument();
    });
  });
});
