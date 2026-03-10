import { describe, it, expect, vi, beforeAll } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import i18n from "@/i18n/config";

// Mock @xyflow/react
vi.mock("@xyflow/react", () => ({
  BaseEdge: ({
    id,
    path,
    style,
    ...props
  }: Record<string, unknown> & { style?: Record<string, unknown> }) => (
    <div
      data-testid={`base-edge-${id}`}
      data-path={path as string}
      data-stroke={style?.stroke as string}
      data-stroke-width={style?.strokeWidth as string}
      {...props}
    />
  ),
  getSmoothStepPath: () => ["M0,0 L100,100", 50, 50],
  EdgeLabelRenderer: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="edge-label-renderer">{children}</div>
  ),
  Position: { Top: "top", Bottom: "bottom", Left: "left", Right: "right" },
}));

import { ConnectionEdge } from "@/components/board/ConnectionEdge";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

function renderConnectionEdge(
  overrides: Record<string, unknown> = {},
  id = "test-edge",
) {
  const defaultProps = {
    id,
    sourceX: 0,
    sourceY: 0,
    targetX: 100,
    targetY: 100,
    sourcePosition: "bottom" as const,
    targetPosition: "top" as const,
    selected: false,
    data: { label: "test" },
    ...overrides,
  } as Parameters<typeof ConnectionEdge>[0];

  return render(<ConnectionEdge {...defaultProps} />);
}

describe("T-3.2.05: ConnectionEdge renders BaseEdge with correct styles", () => {
  it("renders with stroke gray and strokeWidth 1.5 when not selected", () => {
    renderConnectionEdge({ selected: false });
    const edge = screen.getByTestId("base-edge-test-edge");
    expect(edge.getAttribute("data-stroke")).toBe("gray");
    expect(edge.getAttribute("data-stroke-width")).toBe("1.5");
  });

  it("renders with stroke var(--primary) and strokeWidth 2.5 when selected", () => {
    renderConnectionEdge({ selected: true });
    const edge = screen.getByTestId("base-edge-test-edge");
    expect(edge.getAttribute("data-stroke")).toBe("var(--primary)");
    expect(edge.getAttribute("data-stroke-width")).toBe("2.5");
  });
});

describe("T-3.2.06: Double-click on edge label opens input editor", () => {
  it("shows label as span before double-click", () => {
    renderConnectionEdge({ data: { label: "Hello" } });
    const label = screen.getByTestId("edge-label-test-edge");
    expect(label.querySelector("span")).toBeInTheDocument();
    expect(label.querySelector("input")).not.toBeInTheDocument();
  });

  it("opens input editor on double-click", () => {
    renderConnectionEdge({ data: { label: "Hello" } });
    const label = screen.getByTestId("edge-label-test-edge");
    fireEvent.doubleClick(label);
    expect(label.querySelector("input")).toBeInTheDocument();
  });

  it("Enter key commits edit and closes input", () => {
    renderConnectionEdge({ data: { label: "Hello" } });
    const label = screen.getByTestId("edge-label-test-edge");
    fireEvent.doubleClick(label);
    const input = label.querySelector("input")!;
    expect(input).toBeInTheDocument();
    fireEvent.keyDown(input, { key: "Enter" });
    expect(label.querySelector("input")).not.toBeInTheDocument();
  });
});
