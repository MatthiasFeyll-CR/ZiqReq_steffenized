import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { CollapsibleSection } from "@/components/workspace/CollapsibleSection";

describe("CollapsibleSection", () => {
  it("renders title", () => {
    render(
      <CollapsibleSection title="Advanced Options">
        <p>Content</p>
      </CollapsibleSection>,
    );
    expect(screen.getByText("Advanced Options")).toBeInTheDocument();
  });

  it("renders summary when provided", () => {
    render(
      <CollapsibleSection title="Options" summary="2 items selected">
        <p>Content</p>
      </CollapsibleSection>,
    );
    expect(screen.getByText("2 items selected")).toBeInTheDocument();
  });

  it("sets aria-expanded=false when collapsed", () => {
    render(
      <CollapsibleSection title="Options" expanded={false} onExpandedChange={vi.fn()}>
        <p>Content</p>
      </CollapsibleSection>,
    );
    const button = screen.getByRole("button");
    expect(button).toHaveAttribute("aria-expanded", "false");
  });

  it("sets aria-expanded=true when expanded", () => {
    render(
      <CollapsibleSection title="Options" expanded={true} onExpandedChange={vi.fn()}>
        <p>Content</p>
      </CollapsibleSection>,
    );
    const button = screen.getByRole("button");
    expect(button).toHaveAttribute("aria-expanded", "true");
  });

  it("calls onExpandedChange when clicked", async () => {
    const onExpandedChange = vi.fn();
    render(
      <CollapsibleSection title="Options" expanded={false} onExpandedChange={onExpandedChange}>
        <p>Content</p>
      </CollapsibleSection>,
    );

    await userEvent.click(screen.getByRole("button"));
    expect(onExpandedChange).toHaveBeenCalledWith(true);
  });

  it("toggles on Enter key", async () => {
    const onExpandedChange = vi.fn();
    render(
      <CollapsibleSection title="Options" expanded={false} onExpandedChange={onExpandedChange}>
        <p>Content</p>
      </CollapsibleSection>,
    );

    const button = screen.getByRole("button");
    button.focus();
    await userEvent.keyboard("{Enter}");
    expect(onExpandedChange).toHaveBeenCalledWith(true);
  });

  it("toggles on Space key", async () => {
    const onExpandedChange = vi.fn();
    render(
      <CollapsibleSection title="Options" expanded={false} onExpandedChange={onExpandedChange}>
        <p>Content</p>
      </CollapsibleSection>,
    );

    const button = screen.getByRole("button");
    button.focus();
    await userEvent.keyboard(" ");
    expect(onExpandedChange).toHaveBeenCalledWith(true);
  });

  it("applies success variant class", () => {
    const { container } = render(
      <CollapsibleSection title="Submit" variant="success">
        <p>Content</p>
      </CollapsibleSection>,
    );
    expect(container.firstElementChild?.className).toContain("bg-green");
  });

  it("renders children inside the collapsible region", () => {
    render(
      <CollapsibleSection title="Options" expanded={true} onExpandedChange={vi.fn()}>
        <p>Inner content</p>
      </CollapsibleSection>,
    );
    const region = screen.getByRole("region");
    expect(region).toBeInTheDocument();
    expect(screen.getByText("Inner content")).toBeInTheDocument();
  });

  it("has proper aria-controls linking", () => {
    render(
      <CollapsibleSection title="Options" expanded={true} onExpandedChange={vi.fn()}>
        <p>Content</p>
      </CollapsibleSection>,
    );
    const button = screen.getByRole("button");
    const region = screen.getByRole("region");
    expect(button.getAttribute("aria-controls")).toBe(region.id);
  });
});
