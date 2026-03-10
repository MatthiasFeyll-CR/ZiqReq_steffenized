import { describe, it, expect, vi, beforeAll } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import i18n from "@/i18n/config";

// Mock @xyflow/react
vi.mock("@xyflow/react", () => ({
  Handle: ({ type, position, ...props }: Record<string, unknown>) => (
    <div data-testid={`handle-${type}`} data-position={position} {...props} />
  ),
  Position: { Top: "top", Bottom: "bottom", Left: "left", Right: "right" },
}));

import { FreeTextNode } from "@/components/board/FreeTextNode";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

function renderFreeTextNode(
  dataOverrides: Record<string, unknown> = {},
  id = "test-node-id",
) {
  const defaultData = {
    body: "Some text",
    ...dataOverrides,
  };

  const props = {
    id,
    data: defaultData,
    type: "free_text" as const,
    selected: false,
    isConnectable: true,
    zIndex: 0,
    positionAbsoluteX: 0,
    positionAbsoluteY: 0,
    dragging: false,
    deletable: true,
    selectable: true,
    parentId: undefined,
    dragHandle: undefined,
    sourcePosition: undefined,
    targetPosition: undefined,
    width: 200,
    height: 100,
  } as Parameters<typeof FreeTextNode>[0];

  return render(<FreeTextNode {...props} />);
}

describe("T-3.1.03: FreeTextNode renders without border", () => {
  it("renders with transparent background", () => {
    renderFreeTextNode({ body: "Some text" });
    const node = screen.getByTestId("free-text-node");
    expect(node.className).toContain("bg-transparent");
  });

  it("has no border class", () => {
    renderFreeTextNode({ body: "Some text" });
    const node = screen.getByTestId("free-text-node");
    const classes = node.className.split(/\s+/);
    expect(classes).not.toContain("border");
  });

  it("renders body text visible", () => {
    renderFreeTextNode({ body: "Some text" });
    expect(screen.getByText("Some text")).toBeInTheDocument();
  });
});

describe("T-3.2.04: Click opens content editor", () => {
  it("shows display mode before click", () => {
    renderFreeTextNode({ body: "Editable text" });
    expect(screen.getByTestId("free-text-display")).toBeInTheDocument();
    expect(screen.queryByTestId("free-text-textarea")).not.toBeInTheDocument();
  });

  it("enters edit mode with textarea on click", () => {
    renderFreeTextNode({ body: "Editable text" });
    const node = screen.getByTestId("free-text-node");
    fireEvent.click(node);
    expect(screen.getByTestId("free-text-textarea")).toBeInTheDocument();
  });
});
