import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import i18n from "@/i18n/config";
import { ChatInput } from "@/components/chat/ChatInput";
import type { Project } from "@/api/projects";

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

const MOCK_PROJECT: Project = {
  id: "11111111-1111-1111-1111-111111111111",
  title: "Test Brainstorm",
  project_type: "software",
  state: "open",
  agent_mode: "interactive",
  visibility: "private",
  owner_id: "00000000-0000-0000-0000-000000000001",
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
  collaborators: [
    { user_id: "u1", display_name: "Alice Adams" },
    { user_id: "u2", display_name: "Bob Baker" },
  ],
};

function renderChatInput(ideaOverride?: Partial<Project>) {
  const idea = { ...MOCK_PROJECT, ...ideaOverride };
  const onMessageSent = vi.fn();
  return {
    onMessageSent,
    ...render(
      <ChatInput
        projectId={idea.id}
        project={idea}
        onMessageSent={onMessageSent}
      />,
    ),
  };
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("T-2.9.01: @ opens dropdown", () => {
  it("shows mention dropdown when @ is typed", async () => {
    renderChatInput();

    const textarea = screen.getByTestId("chat-input-textarea");
    // Type @ to trigger dropdown
    fireEvent.change(textarea, { target: { value: "@", selectionStart: 1 } });
    // Manually set selectionStart since fireEvent.change doesn't set it
    Object.defineProperty(textarea, "selectionStart", { value: 1, writable: true });
    fireEvent.change(textarea, { target: { value: "@", selectionStart: 1 } });

    expect(screen.getByTestId("mention-dropdown")).toBeInTheDocument();
  });

  it("shows @ai as the first item with Bot icon", async () => {
    renderChatInput();

    const textarea = screen.getByTestId("chat-input-textarea");
    Object.defineProperty(textarea, "selectionStart", { value: 1, writable: true });
    fireEvent.change(textarea, { target: { value: "@", selectionStart: 1 } });

    const aiItem = screen.getByTestId("mention-item-ai");
    expect(aiItem).toBeInTheDocument();
    expect(aiItem).toHaveTextContent("ai");
    // ai item should be the first in the list
    const dropdown = screen.getByTestId("mention-dropdown");
    const firstButton = dropdown.querySelector("button");
    expect(firstButton).toBe(aiItem);
  });

  it("closes dropdown on Escape key", async () => {
    renderChatInput();

    const textarea = screen.getByTestId("chat-input-textarea");
    Object.defineProperty(textarea, "selectionStart", { value: 1, writable: true });
    fireEvent.change(textarea, { target: { value: "@", selectionStart: 1 } });

    expect(screen.getByTestId("mention-dropdown")).toBeInTheDocument();

    fireEvent.keyDown(textarea, { key: "Escape" });

    expect(screen.queryByTestId("mention-dropdown")).not.toBeInTheDocument();
  });

  it("filters items when typing after @", async () => {
    renderChatInput();

    const textarea = screen.getByTestId("chat-input-textarea");
    Object.defineProperty(textarea, "selectionStart", { value: 4, writable: true });
    fireEvent.change(textarea, { target: { value: "@ali", selectionStart: 4 } });

    // Should show Alice Adams but not Bob Baker or ai
    expect(screen.getByTestId("mention-item-u1")).toBeInTheDocument();
    expect(screen.queryByTestId("mention-item-u2")).not.toBeInTheDocument();
    expect(screen.queryByTestId("mention-item-ai")).not.toBeInTheDocument();
  });
});

describe("T-2.9.02: select inserts @username", () => {
  it("inserts @username when clicking a mention item", async () => {
    renderChatInput();

    const textarea = screen.getByTestId("chat-input-textarea");
    Object.defineProperty(textarea, "selectionStart", { value: 1, writable: true });
    fireEvent.change(textarea, { target: { value: "@", selectionStart: 1 } });

    // Click on Alice Adams
    const aliceItem = screen.getByTestId("mention-item-u1");
    fireEvent.mouseDown(aliceItem);

    // The textarea value should now contain @Alice Adams
    expect(textarea).toHaveValue("@Alice Adams ");
    // Dropdown should be closed
    expect(screen.queryByTestId("mention-dropdown")).not.toBeInTheDocument();
  });

  it("inserts @ai when selecting the ai item", async () => {
    renderChatInput();

    const textarea = screen.getByTestId("chat-input-textarea");
    Object.defineProperty(textarea, "selectionStart", { value: 1, writable: true });
    fireEvent.change(textarea, { target: { value: "@", selectionStart: 1 } });

    const aiItem = screen.getByTestId("mention-item-ai");
    fireEvent.mouseDown(aiItem);

    expect(textarea).toHaveValue("@ai ");
    expect(screen.queryByTestId("mention-dropdown")).not.toBeInTheDocument();
  });

  it("inserts mention via Enter key on active item", async () => {
    renderChatInput();

    const textarea = screen.getByTestId("chat-input-textarea");
    Object.defineProperty(textarea, "selectionStart", { value: 1, writable: true });
    fireEvent.change(textarea, { target: { value: "@", selectionStart: 1 } });

    // Press Enter to select the first item (ai)
    fireEvent.keyDown(textarea, { key: "Enter" });

    expect(textarea).toHaveValue("@ai ");
    expect(screen.queryByTestId("mention-dropdown")).not.toBeInTheDocument();
  });

  it("navigates with arrow keys and selects with Enter", async () => {
    renderChatInput();

    const textarea = screen.getByTestId("chat-input-textarea");
    Object.defineProperty(textarea, "selectionStart", { value: 1, writable: true });
    fireEvent.change(textarea, { target: { value: "@", selectionStart: 1 } });

    // Press ArrowDown to move to Alice Adams (index 1)
    fireEvent.keyDown(textarea, { key: "ArrowDown" });
    // Press Enter to select
    fireEvent.keyDown(textarea, { key: "Enter" });

    expect(textarea).toHaveValue("@Alice Adams ");
  });
});

describe("T-2.9.03: renders display_name", () => {
  it("renders collaborator display names in the dropdown", async () => {
    renderChatInput();

    const textarea = screen.getByTestId("chat-input-textarea");
    Object.defineProperty(textarea, "selectionStart", { value: 1, writable: true });
    fireEvent.change(textarea, { target: { value: "@", selectionStart: 1 } });

    expect(screen.getByTestId("mention-item-u1")).toHaveTextContent("Alice Adams");
    expect(screen.getByTestId("mention-item-u2")).toHaveTextContent("Bob Baker");
  });

  it("shows collaborators in alphabetical order after @ai", async () => {
    renderChatInput();

    const textarea = screen.getByTestId("chat-input-textarea");
    Object.defineProperty(textarea, "selectionStart", { value: 1, writable: true });
    fireEvent.change(textarea, { target: { value: "@", selectionStart: 1 } });

    const dropdown = screen.getByTestId("mention-dropdown");
    const buttons = dropdown.querySelectorAll("button");
    // Order: @ai, Alice Adams, Bob Baker
    expect(buttons).toHaveLength(3);
    expect(buttons[0]).toHaveTextContent("ai");
    expect(buttons[1]).toHaveTextContent("Alice Adams");
    expect(buttons[2]).toHaveTextContent("Bob Baker");
  });

  it("renders initials avatar for collaborators", async () => {
    renderChatInput();

    const textarea = screen.getByTestId("chat-input-textarea");
    Object.defineProperty(textarea, "selectionStart", { value: 1, writable: true });
    fireEvent.change(textarea, { target: { value: "@", selectionStart: 1 } });

    const aliceItem = screen.getByTestId("mention-item-u1");
    // Should show "AA" initials for Alice Adams
    expect(aliceItem).toHaveTextContent("AA");
  });
});
