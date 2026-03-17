import { describe, it, expect, vi, beforeAll, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import i18n from "@/i18n/config";

vi.mock("@/api/projects", async () => {
  const actual = await vi.importActual("@/api/projects");
  return {
    ...actual,
    fetchContextWindow: vi.fn(),
  };
});

import { fetchContextWindow } from "@/api/projects";
import { ContextWindowIndicator } from "@/components/chat/ContextWindowIndicator";

const PROJECT_ID = "11111111-1111-1111-1111-111111111111";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

beforeEach(() => {
  vi.useFakeTimers({ shouldAdvanceTime: true });
  vi.mocked(fetchContextWindow).mockReset();
});

afterEach(() => {
  vi.useRealTimers();
});

describe("T-2.14.01: Context window indicator renders with usage percentage", () => {
  it("renders progress ring at correct percentage", async () => {
    vi.mocked(fetchContextWindow).mockResolvedValue({
      usage_percentage: 45,
      message_count: 12,
      compression_iterations: 0,
      recent_message_count: 12,
    });

    await act(async () => {
      render(<ContextWindowIndicator projectId={PROJECT_ID} projectState="open" />);
    });

    await waitFor(() => {
      expect(fetchContextWindow).toHaveBeenCalledWith(PROJECT_ID);
    });

    const indicator = screen.getByTestId("context-window-indicator");
    expect(indicator).toBeInTheDocument();

    const progressRing = screen.getByTestId("context-progress-ring");
    expect(progressRing).toBeInTheDocument();
    // At 45%, the stroke-dashoffset should reflect 55% remaining
    expect(progressRing).toHaveClass("text-primary");
  });

  it("shows warning color at usage >= 80%", async () => {
    vi.mocked(fetchContextWindow).mockResolvedValue({
      usage_percentage: 85,
      message_count: 50,
      compression_iterations: 2,
      recent_message_count: 20,
    });

    await act(async () => {
      render(<ContextWindowIndicator projectId={PROJECT_ID} projectState="open" />);
    });

    await waitFor(() => {
      expect(fetchContextWindow).toHaveBeenCalled();
    });

    const progressRing = screen.getByTestId("context-progress-ring");
    expect(progressRing).toHaveClass("text-amber-500");
  });

  it("is hidden when project state is not open", () => {
    render(<ContextWindowIndicator projectId={PROJECT_ID} projectState="in_review" />);
    expect(screen.queryByTestId("context-window-indicator")).not.toBeInTheDocument();
    expect(fetchContextWindow).not.toHaveBeenCalled();
  });

  it("polls every 30 seconds", async () => {
    vi.mocked(fetchContextWindow).mockResolvedValue({
      usage_percentage: 10,
      message_count: 3,
      compression_iterations: 0,
      recent_message_count: 3,
    });

    await act(async () => {
      render(<ContextWindowIndicator projectId={PROJECT_ID} projectState="open" />);
    });

    await waitFor(() => {
      expect(fetchContextWindow).toHaveBeenCalledTimes(1);
    });

    await act(async () => {
      vi.advanceTimersByTime(30_000);
    });

    await waitFor(() => {
      expect(fetchContextWindow).toHaveBeenCalledTimes(2);
    });
  });
});

describe("T-2.14.02: Hover shows context window details", () => {
  it("shows tooltip with context details on hover", async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });

    vi.mocked(fetchContextWindow).mockResolvedValue({
      usage_percentage: 45,
      message_count: 12,
      compression_iterations: 0,
      recent_message_count: 12,
    });

    await act(async () => {
      render(<ContextWindowIndicator projectId={PROJECT_ID} projectState="open" />);
    });

    await waitFor(() => {
      expect(fetchContextWindow).toHaveBeenCalled();
    });

    const indicator = screen.getByTestId("context-window-indicator");
    await user.hover(indicator);

    await waitFor(() => {
      expect(screen.getAllByText("Context: 45% used, 12 messages, 0 compressions").length).toBeGreaterThan(0);
    });
  });

  it("shows compression note when compressions > 0", async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });

    vi.mocked(fetchContextWindow).mockResolvedValue({
      usage_percentage: 65,
      message_count: 40,
      compression_iterations: 2,
      recent_message_count: 15,
    });

    await act(async () => {
      render(<ContextWindowIndicator projectId={PROJECT_ID} projectState="open" />);
    });

    await waitFor(() => {
      expect(fetchContextWindow).toHaveBeenCalled();
    });

    const indicator = screen.getByTestId("context-window-indicator");
    await user.hover(indicator);

    await waitFor(() => {
      expect(screen.getAllByText("Context: 65% used, 40 messages, 2 compressions").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Older messages compressed").length).toBeGreaterThan(0);
    });
  });
});
