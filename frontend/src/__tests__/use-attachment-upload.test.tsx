import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useAttachmentUpload } from "@/hooks/use-attachment-upload";

vi.mock("react-toastify", () => ({
  toast: {
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn(),
    success: vi.fn(),
  },
}));

vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (_key: string, fallback: string) => fallback }),
}));

vi.mock("@/api/attachments", () => ({
  uploadAttachment: vi.fn(),
  deleteAttachment: vi.fn(),
}));

import { toast } from "react-toastify";
import { uploadAttachment, deleteAttachment } from "@/api/attachments";

const PROJECT_ID = "11111111-1111-1111-1111-111111111111";

function makeFile(name: string, size: number, type: string): File {
  const buf = new ArrayBuffer(Math.min(size, 64));
  return new File([buf], name, { type });
}

describe("useAttachmentUpload", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("rejects files with disallowed type", () => {
    const { result } = renderHook(() => useAttachmentUpload(PROJECT_ID, 0));

    act(() => {
      result.current.addFiles([makeFile("test.exe", 1024, "application/x-msdownload")]);
    });

    expect(toast.error).toHaveBeenCalledWith(expect.stringContaining("not allowed"));
    expect(result.current.pending).toHaveLength(0);
  });

  it("rejects files exceeding 100 MB", () => {
    const { result } = renderHook(() => useAttachmentUpload(PROJECT_ID, 0));

    const bigFile = makeFile("big.png", 101 * 1024 * 1024, "image/png");
    // Override size since File constructor doesn't actually allocate that much
    Object.defineProperty(bigFile, "size", { value: 101 * 1024 * 1024 });

    act(() => {
      result.current.addFiles([bigFile]);
    });

    expect(toast.error).toHaveBeenCalledWith(expect.stringContaining("too large"));
    expect(result.current.pending).toHaveLength(0);
  });

  it("rejects when staging more than 3 files", () => {
    const { result } = renderHook(() => useAttachmentUpload(PROJECT_ID, 0));
    vi.mocked(uploadAttachment).mockReturnValue(new Promise(() => {})); // never resolves

    act(() => {
      result.current.addFiles([
        makeFile("a.png", 100, "image/png"),
        makeFile("b.png", 100, "image/png"),
        makeFile("c.png", 100, "image/png"),
      ]);
    });

    // Now adding a 4th should be rejected
    act(() => {
      result.current.addFiles([makeFile("d.png", 100, "image/png")]);
    });

    expect(toast.error).toHaveBeenCalledWith(expect.stringContaining("3 attachments"));
  });

  it("rejects when project attachment limit would be exceeded", () => {
    const { result } = renderHook(() => useAttachmentUpload(PROJECT_ID, 9));

    act(() => {
      result.current.addFiles([
        makeFile("a.png", 100, "image/png"),
        makeFile("b.png", 100, "image/png"),
      ]);
    });

    expect(toast.error).toHaveBeenCalledWith(expect.stringContaining("10 attachments"));
  });

  it("uploads valid file and reports progress", async () => {
    const mockAttachment = {
      id: "att-1",
      filename: "test.png",
      content_type: "image/png",
      size_bytes: 1024,
      extraction_status: "pending" as const,
      created_at: "2026-01-01T00:00:00Z",
      deleted_at: null,
      message_id: null,
    };

    vi.mocked(uploadAttachment).mockImplementation((_pid, _file, _onProgress) => {
      return Promise.resolve(mockAttachment);
    });

    const { result } = renderHook(() => useAttachmentUpload(PROJECT_ID, 0));

    await act(async () => {
      result.current.addFiles([makeFile("test.png", 1024, "image/png")]);
    });

    expect(uploadAttachment).toHaveBeenCalledWith(
      PROJECT_ID,
      expect.any(File),
      expect.any(Function),
    );

    expect(result.current.stagedAttachmentIds).toContain("att-1");
  });

  it("removes staged attachment and calls delete API", async () => {
    const mockAttachment = {
      id: "att-2",
      filename: "doc.pdf",
      content_type: "application/pdf",
      size_bytes: 2048,
      extraction_status: "pending" as const,
      created_at: "2026-01-01T00:00:00Z",
      deleted_at: null,
      message_id: null,
    };

    vi.mocked(uploadAttachment).mockResolvedValue(mockAttachment);
    vi.mocked(deleteAttachment).mockResolvedValue(undefined);

    const { result } = renderHook(() => useAttachmentUpload(PROJECT_ID, 0));

    await act(async () => {
      result.current.addFiles([makeFile("doc.pdf", 2048, "application/pdf")]);
    });

    const pendingId = result.current.pending[0]?.id;
    expect(pendingId).toBeDefined();

    act(() => {
      result.current.removeAttachment(pendingId!);
    });

    expect(deleteAttachment).toHaveBeenCalledWith(PROJECT_ID, "att-2");
    expect(result.current.pending).toHaveLength(0);
  });

  it("clears all staged on clearStaged", async () => {
    vi.mocked(uploadAttachment).mockResolvedValue({
      id: "att-3",
      filename: "img.jpeg",
      content_type: "image/jpeg",
      size_bytes: 512,
      extraction_status: "pending" as const,
      created_at: "2026-01-01T00:00:00Z",
      deleted_at: null,
      message_id: null,
    });

    const { result } = renderHook(() => useAttachmentUpload(PROJECT_ID, 0));

    await act(async () => {
      result.current.addFiles([makeFile("img.jpeg", 512, "image/jpeg")]);
    });

    expect(result.current.pending).toHaveLength(1);

    act(() => {
      result.current.clearStaged();
    });

    expect(result.current.pending).toHaveLength(0);
    expect(result.current.stagedAttachmentIds).toHaveLength(0);
  });

  it("handles upload failure gracefully", async () => {
    vi.mocked(uploadAttachment).mockRejectedValue(new Error("Server error"));

    const { result } = renderHook(() => useAttachmentUpload(PROJECT_ID, 0));

    await act(async () => {
      result.current.addFiles([makeFile("fail.png", 100, "image/png")]);
    });

    expect(toast.error).toHaveBeenCalledWith(expect.stringContaining("Upload failed"));
    expect(result.current.pending).toHaveLength(0);
  });
});
