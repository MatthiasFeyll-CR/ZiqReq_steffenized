import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import i18n from "@/i18n/config";

// Mock dependencies
vi.mock("react-toastify", () => ({
  toast: { error: vi.fn(), warning: vi.fn(), info: vi.fn(), success: vi.fn() },
}));

vi.mock("@/api/chat", () => ({
  sendChatMessage: vi.fn(),
}));

vi.mock("@/api/attachments", () => ({
  uploadAttachment: vi.fn(),
  deleteAttachment: vi.fn(),
}));

vi.mock("@/hooks/use-lazy-project", () => ({
  useLazyProject: () => ({
    ensureProject: vi.fn().mockResolvedValue("proj-1"),
  }),
}));

vi.mock("@/api/projects", () => ({
  fetchContextWindow: vi.fn().mockResolvedValue({
    usage_percentage: 30,
    message_count: 5,
    compression_iterations: 0,
    recent_message_count: 5,
  }),
}));

import { ChatInput } from "@/components/chat/ChatInput";
import { sendChatMessage } from "@/api/chat";
import { uploadAttachment } from "@/api/attachments";

const PROJECT_ID = "11111111-1111-1111-1111-111111111111";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

beforeEach(() => {
  vi.clearAllMocks();
});

describe("ChatInput with attachments", () => {
  it("renders paperclip button", () => {
    render(<ChatInput projectId={PROJECT_ID} onMessageSent={vi.fn()} />);
    expect(screen.getByTestId("attachment-paperclip")).toBeInTheDocument();
  });

  it("has hidden file input with correct accept attribute", () => {
    render(<ChatInput projectId={PROJECT_ID} onMessageSent={vi.fn()} />);
    const input = screen.getByTestId("attachment-file-input");
    expect(input).toHaveAttribute("accept", ".png,.jpg,.jpeg,.webp,.pdf");
    expect(input).toHaveAttribute("type", "file");
    expect(input.className).toContain("hidden");
  });

  it("clicking paperclip triggers file input click", async () => {
    render(<ChatInput projectId={PROJECT_ID} onMessageSent={vi.fn()} />);
    const input = screen.getByTestId("attachment-file-input") as HTMLInputElement;
    const clickSpy = vi.spyOn(input, "click");
    const paperclip = screen.getByTestId("attachment-paperclip");

    await userEvent.click(paperclip);
    expect(clickSpy).toHaveBeenCalled();
  });

  it("shows staging area when files are being uploaded", async () => {
    // uploadAttachment never resolves to keep items in pending state
    vi.mocked(uploadAttachment).mockReturnValue(new Promise(() => {}));

    render(<ChatInput projectId={PROJECT_ID} onMessageSent={vi.fn()} />);
    const input = screen.getByTestId("attachment-file-input");

    const file = new File(["test"], "test.png", { type: "image/png" });
    fireEvent.change(input, { target: { files: [file] } });

    expect(await screen.findByTestId("attachment-staging-area")).toBeInTheDocument();
    expect(screen.getByText("test.png")).toBeInTheDocument();
  });

  it("sends message with attachment_ids when attachments are staged", async () => {
    const mockAttachment = {
      id: "att-1",
      filename: "test.png",
      content_type: "image/png",
      size_bytes: 100,
      extraction_status: "pending" as const,
      created_at: "2026-01-01T00:00:00Z",
      deleted_at: null,
      message_id: null,
    };

    vi.mocked(uploadAttachment).mockResolvedValue(mockAttachment);
    vi.mocked(sendChatMessage).mockResolvedValue({
      id: "msg-1",
      project_id: PROJECT_ID,
      sender_type: "user",
      sender_id: "user-1",
      ai_agent: null,
      content: "hello",
      message_type: "regular",
      created_at: "2026-01-01T00:00:00Z",
      attachments: [mockAttachment],
    });

    const onSent = vi.fn();
    render(<ChatInput projectId={PROJECT_ID} onMessageSent={onSent} />);

    // Upload a file
    const input = screen.getByTestId("attachment-file-input");
    const file = new File(["test"], "test.png", { type: "image/png" });
    fireEvent.change(input, { target: { files: [file] } });

    // Wait for upload to finish
    await screen.findByTestId("attachment-staging-area");

    // Type a message and send
    const textarea = screen.getByTestId("chat-input-textarea");
    await userEvent.type(textarea, "hello");
    const sendBtn = screen.getByTestId("chat-send-button");
    await userEvent.click(sendBtn);

    // Verify sendChatMessage was called with attachment_ids
    await vi.waitFor(() => {
      expect(sendChatMessage).toHaveBeenCalledWith("proj-1", "hello", ["att-1"]);
    });
  });
});

describe("ChatDropZone", () => {
  it("shows overlay on drag enter and hides on drop", async () => {
    // We test the ChatDropZone in isolation
    const { ChatDropZone } = await import("@/components/chat/ChatDropZone");
    const onFiles = vi.fn();

    render(
      <ChatDropZone onFiles={onFiles}>
        <div>Content</div>
      </ChatDropZone>,
    );

    const zone = screen.getByTestId("chat-drop-zone");

    // Simulate drag enter
    fireEvent.dragEnter(zone, { dataTransfer: { files: [] } });
    expect(screen.getByTestId("drop-overlay")).toBeInTheDocument();

    // Simulate drop
    const file = new File(["test"], "test.pdf", { type: "application/pdf" });
    const dt = { files: [file] };
    fireEvent.drop(zone, { dataTransfer: dt });

    expect(onFiles).toHaveBeenCalledWith(dt.files);
    expect(screen.queryByTestId("drop-overlay")).not.toBeInTheDocument();
  });
});
