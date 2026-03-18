import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import i18n from "@/i18n/config";
import type { ChatMessage } from "@/api/chat";

const mockGetAttachmentUrl = vi.fn();
const mockToastInfo = vi.fn();

vi.mock("@/api/attachments", () => ({
  getAttachmentUrl: (...args: unknown[]) => mockGetAttachmentUrl(...args),
}));

vi.mock("react-toastify", () => ({
  toast: {
    info: (...args: unknown[]) => mockToastInfo(...args),
    error: vi.fn(),
    warning: vi.fn(),
    success: vi.fn(),
  },
}));

vi.mock("@/components/chat/ReactionChips", () => ({
  ReactionChips: () => null,
}));

import { UserMessageBubble } from "@/components/chat/UserMessageBubble";

const PROJECT_ID = "11111111-1111-1111-1111-111111111111";

const messageWithAttachments: ChatMessage = {
  id: "msg-1",
  project_id: PROJECT_ID,
  sender_type: "user",
  sender_id: "user-1",
  ai_agent: null,
  content: "Here are the docs",
  message_type: "regular",
  created_at: "2026-01-01T12:00:00Z",
  attachments: [
    {
      id: "att-1",
      filename: "screenshot.png",
      content_type: "image/png",
      size_bytes: 204800,
      extraction_status: "completed",
      created_at: "2026-01-01T00:00:00Z",
      deleted_at: null,
      message_id: "msg-1",
    },
    {
      id: "att-2",
      filename: "requirements.pdf",
      content_type: "application/pdf",
      size_bytes: 1048576,
      extraction_status: "completed",
      created_at: "2026-01-01T00:00:00Z",
      deleted_at: null,
      message_id: "msg-1",
    },
  ],
};

const messageWithoutAttachments: ChatMessage = {
  id: "msg-2",
  project_id: PROJECT_ID,
  sender_type: "user",
  sender_id: "user-1",
  ai_agent: null,
  content: "Just a text message",
  message_type: "regular",
  created_at: "2026-01-01T12:00:00Z",
};

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

beforeEach(() => {
  vi.clearAllMocks();
});

describe("UserMessageBubble with attachments", () => {
  it("renders attachment boxes below message content", () => {
    render(
      <UserMessageBubble
        message={messageWithAttachments}
        projectId={PROJECT_ID}
        showSenderName={false}
        isOwnMessage={true}
      />,
    );

    expect(screen.getByText("Here are the docs")).toBeInTheDocument();
    expect(screen.getByTestId("message-attachments")).toBeInTheDocument();
    expect(screen.getByText("screenshot.png")).toBeInTheDocument();
    expect(screen.getByText("requirements.pdf")).toBeInTheDocument();
  });

  it("does not render attachment section for messages without attachments", () => {
    render(
      <UserMessageBubble
        message={messageWithoutAttachments}
        projectId={PROJECT_ID}
        showSenderName={false}
        isOwnMessage={true}
      />,
    );

    expect(screen.getByText("Just a text message")).toBeInTheDocument();
    expect(screen.queryByTestId("message-attachments")).not.toBeInTheDocument();
  });

  it("passes clickable=true when not readOnly", () => {
    render(
      <UserMessageBubble
        message={messageWithAttachments}
        projectId={PROJECT_ID}
        showSenderName={false}
        isOwnMessage={true}
        isReadOnly={false}
      />,
    );

    const boxes = screen.getAllByTestId("attachment-box");
    expect(boxes.length).toBe(2);
    // Boxes should have cursor-pointer class (clickable)
    boxes.forEach((box) => {
      expect(box.className).toContain("cursor-pointer");
    });
  });

  it("passes clickable=false when readOnly, shows toast on click", async () => {
    render(
      <UserMessageBubble
        message={messageWithAttachments}
        projectId={PROJECT_ID}
        showSenderName={false}
        isOwnMessage={true}
        isReadOnly={true}
      />,
    );

    const boxes = screen.getAllByTestId("attachment-box");
    expect(boxes.length).toBe(2);
    // Boxes should have cursor-not-allowed class
    boxes.forEach((box) => {
      expect(box.className).toContain("cursor-not-allowed");
    });

    // Click should show toast, not call getAttachmentUrl
    await userEvent.click(boxes[0]!);
    expect(mockToastInfo).toHaveBeenCalledWith("Download not available in read-only mode");
    expect(mockGetAttachmentUrl).not.toHaveBeenCalled();
  });

  it("renders two attachment boxes for message with two attachments", () => {
    render(
      <UserMessageBubble
        message={messageWithAttachments}
        projectId={PROJECT_ID}
        showSenderName={false}
        isOwnMessage={false}
      />,
    );

    const boxes = screen.getAllByTestId("attachment-box");
    expect(boxes.length).toBe(2);
  });
});
