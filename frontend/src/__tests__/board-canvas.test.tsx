import { describe, it, expect, vi, beforeAll } from "vitest";
import { render, screen } from "@testing-library/react";
import i18n from "@/i18n/config";

// Mock @xyflow/react since jsdom lacks DOM measurement APIs
vi.mock("@xyflow/react", () => {
  const BackgroundVariant = { Dots: "dots", Lines: "lines", Cross: "cross" };
  return {
    ReactFlow: ({ children, minZoom, maxZoom, ...props }: Record<string, unknown>) => (
      <div data-testid="react-flow" data-min-zoom={minZoom} data-max-zoom={maxZoom} {...props}>
        {children as React.ReactNode}
      </div>
    ),
    Background: ({ variant, gap, ...props }: Record<string, unknown>) => (
      <div data-testid="rf-background" data-variant={variant} data-gap={gap} {...props} />
    ),
    BackgroundVariant,
    MiniMap: (props: Record<string, unknown>) => <div data-testid="rf-minimap" {...props} />,
    Controls: (props: Record<string, unknown>) => <div data-testid="rf-controls" {...props} />,
    useNodesState: (init: unknown[]) => [init, vi.fn(), vi.fn()],
    useEdgesState: (init: unknown[]) => [init, vi.fn(), vi.fn()],
  };
});

import { BoardCanvas } from "@/components/board/BoardCanvas";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

describe("T-3.3.01: Board canvas with dot grid background", () => {
  it("renders React Flow canvas with dot background at 20px gap", () => {
    render(<BoardCanvas />);

    expect(screen.getByTestId("board-canvas")).toBeInTheDocument();
    expect(screen.getByTestId("react-flow")).toBeInTheDocument();

    const bg = screen.getByTestId("rf-background");
    expect(bg).toHaveAttribute("data-variant", "dots");
    expect(bg).toHaveAttribute("data-gap", "20");
  });

  it("configures zoom range 25%-200%", () => {
    render(<BoardCanvas />);

    const flow = screen.getByTestId("react-flow");
    expect(flow).toHaveAttribute("data-min-zoom", "0.25");
    expect(flow).toHaveAttribute("data-max-zoom", "2");
  });
});

describe("T-3.3.02: Minimap and zoom controls render", () => {
  it("renders minimap placeholder", () => {
    render(<BoardCanvas />);
    expect(screen.getByTestId("board-minimap")).toBeInTheDocument();
  });

  it("renders zoom controls placeholder", () => {
    render(<BoardCanvas />);
    expect(screen.getByTestId("board-zoom-controls")).toBeInTheDocument();
  });
});
