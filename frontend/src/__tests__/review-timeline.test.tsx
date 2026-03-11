import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReviewTimeline } from "@/components/review/ReviewTimeline";
import type { TimelineEntry } from "@/api/review";
import i18n from "@/i18n/config";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

const { mockPostComment, mockToastError } = vi.hoisted(() => ({
  mockPostComment: vi.fn(),
  mockToastError: vi.fn(),
}));

vi.mock("@/api/review", async () => {
  const actual = await vi.importActual("@/api/review");
  return {
    ...actual,
    postComment: mockPostComment,
  };
});

vi.mock("react-toastify", () => ({
  toast: Object.assign(vi.fn(), { error: mockToastError }),
  ToastContainer: () => null,
}));

const IDEA_ID = "11111111-1111-1111-1111-111111111111";

function makeEntry(overrides: Partial<TimelineEntry> & { id: string }): TimelineEntry {
  return {
    entry_type: "comment",
    author: { id: "u1", display_name: "Alice" },
    content: "Test comment",
    parent_entry_id: null,
    old_state: null,
    new_state: null,
    old_version_id: null,
    new_version_id: null,
    created_at: "2026-03-01T10:00:00Z",
    ...overrides,
  };
}

function renderTimeline(entries: TimelineEntry[], ideaId?: string) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <ReviewTimeline entries={entries} ideaId={ideaId} />
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  mockPostComment.mockReset();
  mockToastError.mockReset();
});

describe("UI-TIMELINE.01: Timeline renders entries", () => {
  it("renders all three entry types correctly", () => {
    const entries: TimelineEntry[] = [
      makeEntry({
        id: "e1",
        entry_type: "state_change",
        content: "Submitted for review",
        old_state: "open",
        new_state: "in_review",
      }),
      makeEntry({
        id: "e2",
        entry_type: "comment",
        content: "Looks good!",
        author: { id: "u1", display_name: "Bob" },
      }),
      makeEntry({
        id: "e3",
        entry_type: "resubmission",
        content: null,
        old_version_id: "v1-uuid-abcd",
        new_version_id: "v2-uuid-efgh",
      }),
    ];

    renderTimeline(entries);

    expect(screen.getByTestId("review-timeline")).toBeInTheDocument();
    expect(screen.getAllByTestId("timeline-entry-state_change")).toHaveLength(1);
    expect(screen.getAllByTestId("timeline-entry-comment")).toHaveLength(1);
    expect(screen.getAllByTestId("timeline-entry-resubmission")).toHaveLength(1);

    // State change shows italic text
    expect(screen.getByText("Submitted for review")).toBeInTheDocument();

    // Comment shows author and content
    expect(screen.getByText("Bob")).toBeInTheDocument();
    expect(screen.getByText("Looks good!")).toBeInTheDocument();

    // Resubmission shows download buttons
    expect(screen.getByTestId("download-old-version")).toBeInTheDocument();
    expect(screen.getByTestId("download-new-version")).toBeInTheDocument();
  });

  it("renders chronologically (oldest first)", () => {
    const entries: TimelineEntry[] = [
      makeEntry({ id: "e1", content: "First", created_at: "2026-01-01T00:00:00Z" }),
      makeEntry({ id: "e2", content: "Second", created_at: "2026-02-01T00:00:00Z" }),
      makeEntry({ id: "e3", content: "Third", created_at: "2026-03-01T00:00:00Z" }),
    ];

    renderTimeline(entries);

    const commentEntries = screen.getAllByTestId("timeline-entry-comment");
    expect(commentEntries).toHaveLength(3);
    expect(commentEntries[0]).toHaveTextContent("First");
    expect(commentEntries[1]).toHaveTextContent("Second");
    expect(commentEntries[2]).toHaveTextContent("Third");
  });

  it("shows empty state when no entries", () => {
    renderTimeline([]);

    expect(screen.getByTestId("timeline-empty")).toBeInTheDocument();
    expect(screen.getByText("No timeline entries yet")).toBeInTheDocument();
  });

  it("shows comment input at bottom when ideaId is provided", () => {
    renderTimeline([], IDEA_ID);

    expect(screen.getByTestId("top-level-comment-input")).toBeInTheDocument();
    expect(screen.getByTestId("comment-textarea")).toBeInTheDocument();
  });

  it("shows avatar, author name, timestamp on comment entries", () => {
    const entries = [
      makeEntry({
        id: "e1",
        author: { id: "u1", display_name: "Charlie" },
        content: "Great work",
        created_at: "2026-03-01T10:00:00Z",
      }),
    ];

    renderTimeline(entries);

    expect(screen.getByText("Charlie")).toBeInTheDocument();
    expect(screen.getByText("Great work")).toBeInTheDocument();
    // Timestamp rendered
    expect(screen.getByText(new Date("2026-03-01T10:00:00Z").toLocaleString())).toBeInTheDocument();
  });
});

describe("UI-TIMELINE.02: Nested replies indented", () => {
  it("indents nested comment by 24px", () => {
    const entries: TimelineEntry[] = [
      makeEntry({ id: "parent", content: "Parent comment" }),
      makeEntry({
        id: "reply",
        content: "Reply comment",
        parent_entry_id: "parent",
      }),
    ];

    renderTimeline(entries);

    const replyEntry = screen.getAllByTestId("timeline-entry-comment")[1]!;
    expect(replyEntry.style.marginLeft).toBe("24px");
  });

  it("does not indent top-level comment", () => {
    const entries = [makeEntry({ id: "top", content: "Top-level" })];

    renderTimeline(entries);

    const topEntry = screen.getByTestId("timeline-entry-comment");
    expect(topEntry.style.marginLeft).toBe("");
  });
});

describe("UI-TIMELINE.03: Post comment", () => {
  it("calls POST API when filling CommentInput and clicking send", async () => {
    const user = userEvent.setup();
    const newEntry = makeEntry({ id: "new-1", content: "Hello world" });
    mockPostComment.mockResolvedValue(newEntry);

    renderTimeline([], IDEA_ID);

    const textarea = screen.getByTestId("comment-textarea");
    await user.type(textarea, "Hello world");

    const sendButton = screen.getByTestId("comment-send-button");
    await user.click(sendButton);

    await waitFor(() => {
      expect(mockPostComment).toHaveBeenCalledWith(IDEA_ID, { content: "Hello world" });
    });
  });

  it("disables send button when textarea is empty", () => {
    renderTimeline([], IDEA_ID);

    const sendButton = screen.getByTestId("comment-send-button");
    expect(sendButton).toBeDisabled();
  });

  it("clears textarea after successful submit", async () => {
    const user = userEvent.setup();
    mockPostComment.mockResolvedValue(makeEntry({ id: "new-1" }));

    renderTimeline([], IDEA_ID);

    const textarea = screen.getByTestId("comment-textarea");
    await user.type(textarea, "Test message");
    await user.click(screen.getByTestId("comment-send-button"));

    await waitFor(() => {
      expect((textarea as HTMLTextAreaElement).value).toBe("");
    });
  });
});

describe("UI-TIMELINE.04: Reply to comment", () => {
  it("shows reply input when clicking reply button", async () => {
    const user = userEvent.setup();
    const entries = [makeEntry({ id: "e1", content: "Original comment" })];

    renderTimeline(entries, IDEA_ID);

    const replyButton = screen.getByTestId("reply-button-e1");
    await user.click(replyButton);

    await waitFor(() => {
      expect(screen.getByTestId("reply-input-e1")).toBeInTheDocument();
    });
  });

  it("posts reply with parent_entry_id", async () => {
    const user = userEvent.setup();
    const entries = [makeEntry({ id: "e1", content: "Original comment" })];
    const replyEntry = makeEntry({ id: "reply-1", parent_entry_id: "e1", content: "My reply" });
    mockPostComment.mockResolvedValue(replyEntry);

    renderTimeline(entries, IDEA_ID);

    // Click reply button
    await user.click(screen.getByTestId("reply-button-e1"));

    // Find the reply input area and type
    const replyInput = screen.getByTestId("reply-input-e1");
    const textarea = replyInput.querySelector("textarea")!;
    await user.type(textarea, "My reply");

    // Click the send button within the reply input
    const sendButton = replyInput.querySelector('[data-testid="comment-send-button"]')!;
    await user.click(sendButton);

    await waitFor(() => {
      expect(mockPostComment).toHaveBeenCalledWith(IDEA_ID, {
        content: "My reply",
        parent_entry_id: "e1",
      });
    });
  });

  it("hides reply input when cancel is clicked", async () => {
    const user = userEvent.setup();
    const entries = [makeEntry({ id: "e1", content: "Original comment" })];

    renderTimeline(entries, IDEA_ID);

    await user.click(screen.getByTestId("reply-button-e1"));

    await waitFor(() => {
      expect(screen.getByTestId("reply-input-e1")).toBeInTheDocument();
    });

    const cancelButton = screen.getByTestId("comment-cancel-button");
    await user.click(cancelButton);

    await waitFor(() => {
      expect(screen.queryByTestId("reply-input-e1")).not.toBeInTheDocument();
    });
  });

  it("reply button shows 'Reply' text", () => {
    const entries = [makeEntry({ id: "e1", content: "Comment" })];

    renderTimeline(entries, IDEA_ID);

    expect(screen.getByTestId("reply-button-e1")).toHaveTextContent("Reply");
  });
});
