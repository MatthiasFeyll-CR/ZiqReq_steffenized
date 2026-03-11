import { describe, it, expect, beforeAll } from "vitest";
import { render, screen, act } from "@testing-library/react";
import { AIProcessingIndicator } from "@/components/chat/AIProcessingIndicator";
import i18n from "@/i18n/config";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

const IDEA_ID = "11111111-1111-1111-1111-111111111111";

function dispatchAiProcessing(ideaId: string, state: string) {
  window.dispatchEvent(
    new CustomEvent("ws:ai_processing", {
      detail: { idea_id: ideaId, state },
    }),
  );
}

describe("T-2.12.01: AI processing indicator shows", () => {
  it("is hidden by default", () => {
    render(<AIProcessingIndicator ideaId={IDEA_ID} />);
    expect(screen.queryByTestId("ai-processing-indicator")).not.toBeInTheDocument();
  });

  it("becomes visible on ai_processing {state: started}", () => {
    render(<AIProcessingIndicator ideaId={IDEA_ID} />);

    act(() => {
      dispatchAiProcessing(IDEA_ID, "started");
    });

    const indicator = screen.getByTestId("ai-processing-indicator");
    expect(indicator).toBeInTheDocument();
    expect(indicator).toHaveTextContent("AI is processing");
  });

  it("shows animated dots with motion-safe class", () => {
    render(<AIProcessingIndicator ideaId={IDEA_ID} />);

    act(() => {
      dispatchAiProcessing(IDEA_ID, "started");
    });

    const dots = screen.getByTestId("ai-processing-indicator").querySelectorAll("span > span");
    expect(dots).toHaveLength(3);
    dots.forEach((dot) => {
      expect(dot.className).toContain("motion-safe:animate-bounce");
    });
  });

  it("ignores events for different idea_id", () => {
    render(<AIProcessingIndicator ideaId={IDEA_ID} />);

    act(() => {
      dispatchAiProcessing("other-idea-id", "started");
    });

    expect(screen.queryByTestId("ai-processing-indicator")).not.toBeInTheDocument();
  });
});

describe("T-2.12.02: AI processing indicator hides", () => {
  it("hides on ai_processing {state: completed}", () => {
    render(<AIProcessingIndicator ideaId={IDEA_ID} />);

    act(() => {
      dispatchAiProcessing(IDEA_ID, "started");
    });
    expect(screen.getByTestId("ai-processing-indicator")).toBeInTheDocument();

    act(() => {
      dispatchAiProcessing(IDEA_ID, "completed");
    });
    expect(screen.queryByTestId("ai-processing-indicator")).not.toBeInTheDocument();
  });

  it("hides on ai_processing {state: failed}", () => {
    render(<AIProcessingIndicator ideaId={IDEA_ID} />);

    act(() => {
      dispatchAiProcessing(IDEA_ID, "started");
    });
    expect(screen.getByTestId("ai-processing-indicator")).toBeInTheDocument();

    act(() => {
      dispatchAiProcessing(IDEA_ID, "failed");
    });
    expect(screen.queryByTestId("ai-processing-indicator")).not.toBeInTheDocument();
  });
});
