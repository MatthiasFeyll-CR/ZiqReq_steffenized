import { describe, it, expect, beforeAll } from "vitest";
import { render, screen, act } from "@testing-library/react";
import { AIProcessingIndicator } from "@/components/chat/AIProcessingIndicator";
import i18n from "@/i18n/config";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

const PROJECT_ID = "11111111-1111-1111-1111-111111111111";

function dispatchAiProcessing(projectId: string, state: string) {
  window.dispatchEvent(
    new CustomEvent("ws:ai_processing", {
      detail: { project_id: projectId, state },
    }),
  );
}

describe("T-2.12.01: AI processing indicator shows", () => {
  it("is hidden by default", () => {
    render(<AIProcessingIndicator projectId={PROJECT_ID} />);
    expect(screen.queryByTestId("ai-processing-indicator")).not.toBeInTheDocument();
  });

  it("becomes visible on ai_processing {state: started}", () => {
    render(<AIProcessingIndicator projectId={PROJECT_ID} />);

    act(() => {
      dispatchAiProcessing(PROJECT_ID, "started");
    });

    const indicator = screen.getByTestId("ai-processing-indicator");
    expect(indicator).toBeInTheDocument();
    expect(indicator).toHaveTextContent("thinking");
  });

  it("shows animated dots with typing-dot class", () => {
    render(<AIProcessingIndicator projectId={PROJECT_ID} />);

    act(() => {
      dispatchAiProcessing(PROJECT_ID, "started");
    });

    const indicator = screen.getByTestId("ai-processing-indicator");
    const dots = indicator.querySelectorAll(".typing-dot");
    expect(dots).toHaveLength(3);
    dots.forEach((dot) => {
      expect(dot.className).toContain("typing-dot");
      expect(dot.className).toContain("rounded-full");
    });
  });

  it("ignores events for different project_id", () => {
    render(<AIProcessingIndicator projectId={PROJECT_ID} />);

    act(() => {
      dispatchAiProcessing("other-idea-id", "started");
    });

    expect(screen.queryByTestId("ai-processing-indicator")).not.toBeInTheDocument();
  });
});

describe("T-2.12.02: AI processing indicator hides", () => {
  it("hides on ai_processing {state: completed}", () => {
    render(<AIProcessingIndicator projectId={PROJECT_ID} />);

    act(() => {
      dispatchAiProcessing(PROJECT_ID, "started");
    });
    expect(screen.getByTestId("ai-processing-indicator")).toBeInTheDocument();

    act(() => {
      dispatchAiProcessing(PROJECT_ID, "completed");
    });
    expect(screen.queryByTestId("ai-processing-indicator")).not.toBeInTheDocument();
  });

  it("hides on ai_processing {state: failed}", () => {
    render(<AIProcessingIndicator projectId={PROJECT_ID} />);

    act(() => {
      dispatchAiProcessing(PROJECT_ID, "started");
    });
    expect(screen.getByTestId("ai-processing-indicator")).toBeInTheDocument();

    act(() => {
      dispatchAiProcessing(PROJECT_ID, "failed");
    });
    expect(screen.queryByTestId("ai-processing-indicator")).not.toBeInTheDocument();
  });
});
