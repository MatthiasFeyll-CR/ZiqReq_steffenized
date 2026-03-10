import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import i18n from "@/i18n/config";
import { ChatInput } from "@/components/chat/ChatInput";
import type { Idea } from "@/api/ideas";

// Mock sendChatMessage
vi.mock("@/api/chat", async () => {
  const actual = await vi.importActual("@/api/chat");
  return {
    ...actual,
    sendChatMessage: vi.fn(),
  };
});

beforeAll(async () => {
  await i18n.changeLanguage("en");
  Element.prototype.scrollIntoView = () => {};
});

const MOCK_IDEA: Idea = {
  id: "11111111-1111-1111-1111-111111111111",
  title: "Test Brainstorm",
  state: "open",
  agent_mode: "interactive",
  visibility: "private",
  owner_id: "00000000-0000-0000-0000-000000000001",
  co_owner_id: null,
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
  collaborators: [],
};

function renderChatInput() {
  const onMessageSent = vi.fn();
  return {
    onMessageSent,
    ...render(
      <ChatInput
        ideaId={MOCK_IDEA.id}
        idea={MOCK_IDEA}
        onMessageSent={onMessageSent}
      />,
    ),
  };
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("T-3.8.02: ChatInput listens for board:reference and inserts @board[uuid]", () => {
  it("inserts @board[uuid] into empty textarea on board:reference event", () => {
    renderChatInput();

    const textarea = screen.getByTestId("chat-input-textarea") as HTMLTextAreaElement;

    act(() => {
      window.dispatchEvent(
        new CustomEvent("board:reference", { detail: "@board[abc-123]" }),
      );
    });

    expect(textarea.value).toBe("@board[abc-123] ");
  });

  it("inserts @board[uuid] at cursor position preserving existing text", () => {
    renderChatInput();

    const textarea = screen.getByTestId("chat-input-textarea") as HTMLTextAreaElement;

    // Set initial value
    fireEvent.change(textarea, { target: { value: "Hello world" } });
    expect(textarea.value).toBe("Hello world");

    // Set cursor position to after "Hello "
    textarea.selectionStart = 6;
    textarea.selectionEnd = 6;

    act(() => {
      window.dispatchEvent(
        new CustomEvent("board:reference", { detail: "@board[node-456]" }),
      );
    });

    expect(textarea.value).toBe("Hello @board[node-456] world");
  });

  it("replaces selected text with @board[uuid]", () => {
    renderChatInput();

    const textarea = screen.getByTestId("chat-input-textarea") as HTMLTextAreaElement;

    fireEvent.change(textarea, { target: { value: "Hello world" } });

    // Select "world"
    textarea.selectionStart = 6;
    textarea.selectionEnd = 11;

    act(() => {
      window.dispatchEvent(
        new CustomEvent("board:reference", { detail: "@board[node-789]" }),
      );
    });

    expect(textarea.value).toBe("Hello @board[node-789] ");
  });

  it("handles multiple reference insertions", () => {
    renderChatInput();

    const textarea = screen.getByTestId("chat-input-textarea") as HTMLTextAreaElement;

    act(() => {
      window.dispatchEvent(
        new CustomEvent("board:reference", { detail: "@board[first]" }),
      );
    });

    expect(textarea.value).toBe("@board[first] ");

    // Move cursor to end
    textarea.selectionStart = textarea.value.length;
    textarea.selectionEnd = textarea.value.length;

    act(() => {
      window.dispatchEvent(
        new CustomEvent("board:reference", { detail: "@board[second]" }),
      );
    });

    expect(textarea.value).toBe("@board[first] @board[second] ");
  });
});
