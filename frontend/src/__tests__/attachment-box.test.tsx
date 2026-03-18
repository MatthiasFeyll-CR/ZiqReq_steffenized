import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import i18n from "@/i18n/config";
import type { Attachment } from "@/api/attachments";

const mockGetAttachmentUrl = vi.fn();
const mockToastInfo = vi.fn();
const mockToastError = vi.fn();

vi.mock("@/api/attachments", () => ({
  getAttachmentUrl: (...args: unknown[]) => mockGetAttachmentUrl(...args),
}));

vi.mock("react-toastify", () => ({
  toast: {
    info: (...args: unknown[]) => mockToastInfo(...args),
    error: (...args: unknown[]) => mockToastError(...args),
    warning: vi.fn(),
    success: vi.fn(),
  },
}));

import { AttachmentBox } from "@/components/chat/AttachmentBox";

const PROJECT_ID = "11111111-1111-1111-1111-111111111111";

const imageAttachment: Attachment = {
  id: "att-1",
  filename: "screenshot.png",
  content_type: "image/png",
  size_bytes: 204800,
  extraction_status: "completed",
  created_at: "2026-01-01T00:00:00Z",
  message_id: "msg-1",
};

const pdfAttachment: Attachment = {
  id: "att-2",
  filename: "requirements.pdf",
  content_type: "application/pdf",
  size_bytes: 1048576,
  extraction_status: "completed",
  created_at: "2026-01-01T00:00:00Z",
  message_id: "msg-1",
};

const pendingAttachment: Attachment = {
  id: "att-3",
  filename: "diagram.png",
  content_type: "image/png",
  size_bytes: 512000,
  extraction_status: "processing",
  created_at: "2026-01-01T00:00:00Z",
  message_id: "msg-1",
};

const failedAttachment: Attachment = {
  id: "att-4",
  filename: "corrupt.pdf",
  content_type: "application/pdf",
  size_bytes: 100,
  extraction_status: "failed",
  created_at: "2026-01-01T00:00:00Z",
  message_id: "msg-1",
};

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

beforeEach(() => {
  vi.clearAllMocks();
});

describe("AttachmentBox", () => {
  it("renders filename and size", () => {
    render(
      <AttachmentBox attachment={imageAttachment} projectId={PROJECT_ID} clickable={true} />,
    );
    expect(screen.getByText("screenshot.png")).toBeInTheDocument();
    expect(screen.getByText("200 KB")).toBeInTheDocument();
  });

  it("renders PDF size in MB", () => {
    render(
      <AttachmentBox attachment={pdfAttachment} projectId={PROJECT_ID} clickable={true} />,
    );
    expect(screen.getByText("requirements.pdf")).toBeInTheDocument();
    expect(screen.getByText("1.0 MB")).toBeInTheDocument();
  });

  it("shows processing indicator for pending/processing attachments", () => {
    render(
      <AttachmentBox attachment={pendingAttachment} projectId={PROJECT_ID} clickable={true} />,
    );
    expect(screen.getByTestId("attachment-processing")).toBeInTheDocument();
    expect(screen.getByText("Processing...")).toBeInTheDocument();
  });

  it("shows extraction failed for failed attachments", () => {
    render(
      <AttachmentBox attachment={failedAttachment} projectId={PROJECT_ID} clickable={true} />,
    );
    expect(screen.getByTestId("attachment-failed")).toBeInTheDocument();
    expect(screen.getByText("Extraction failed")).toBeInTheDocument();
  });

  it("opens presigned URL on click when clickable", async () => {
    const mockOpen = vi.fn();
    vi.stubGlobal("open", mockOpen);
    mockGetAttachmentUrl.mockResolvedValue("https://minio.local/presigned-url");

    render(
      <AttachmentBox attachment={imageAttachment} projectId={PROJECT_ID} clickable={true} />,
    );

    await userEvent.click(screen.getByTestId("attachment-box"));
    await vi.waitFor(() => {
      expect(mockGetAttachmentUrl).toHaveBeenCalledWith(PROJECT_ID, "att-1");
      expect(mockOpen).toHaveBeenCalledWith("https://minio.local/presigned-url", "_blank");
    });

    vi.unstubAllGlobals();
  });

  it("shows toast when clicked in read-only mode", async () => {
    render(
      <AttachmentBox attachment={imageAttachment} projectId={PROJECT_ID} clickable={false} />,
    );

    await userEvent.click(screen.getByTestId("attachment-box"));
    expect(mockToastInfo).toHaveBeenCalledWith("Download not available in read-only mode");
    expect(mockGetAttachmentUrl).not.toHaveBeenCalled();
  });

  it("shows remove button when onRemove is provided", () => {
    const onRemove = vi.fn();
    render(
      <AttachmentBox
        attachment={imageAttachment}
        projectId={PROJECT_ID}
        clickable={true}
        onRemove={onRemove}
      />,
    );
    expect(screen.getByTestId("attachment-remove")).toBeInTheDocument();
  });

  it("does not show remove button when onRemove is not provided", () => {
    render(
      <AttachmentBox attachment={imageAttachment} projectId={PROJECT_ID} clickable={true} />,
    );
    expect(screen.queryByTestId("attachment-remove")).not.toBeInTheDocument();
  });

  it("calls onRemove when remove button clicked", async () => {
    const onRemove = vi.fn();
    render(
      <AttachmentBox
        attachment={imageAttachment}
        projectId={PROJECT_ID}
        clickable={true}
        onRemove={onRemove}
      />,
    );

    await userEvent.click(screen.getByTestId("attachment-remove"));
    expect(onRemove).toHaveBeenCalled();
    // Should not trigger download
    expect(mockGetAttachmentUrl).not.toHaveBeenCalled();
  });

  it("shows thumbnail when showThumbnail is true for image and thumbnailUrl provided", () => {
    render(
      <AttachmentBox
        attachment={imageAttachment}
        projectId={PROJECT_ID}
        clickable={true}
        showThumbnail={true}
        thumbnailUrl="blob:test-url"
      />,
    );
    expect(screen.getByTestId("attachment-thumbnail")).toBeInTheDocument();
  });
});
