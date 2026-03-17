import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { ProjectCard } from "@/components/landing/ProjectCard";
import type { ProjectCardProps, ProjectState } from "@/components/landing/ProjectCard";
import i18n from "@/i18n/config";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

function renderProjectCard(props: Partial<ProjectCardProps> = {}) {
  const defaultProps: ProjectCardProps = {
    id: "test-uuid-123",
    title: "My Test Project",
    state: "open",
    updatedAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    ...props,
  };
  return render(
    <MemoryRouter>
      <ProjectCard {...defaultProps} />
    </MemoryRouter>,
  );
}

describe("ProjectCard component", () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  it("renders state dot with correct color for open state", () => {
    renderProjectCard({ state: "open" });
    const dot = screen.getByLabelText("Open");
    expect(dot).toBeInTheDocument();
    expect(dot.style.backgroundColor).toBe("rgb(2, 132, 199)");
    expect(dot.style.width).toBe("8px");
    expect(dot.style.height).toBe("8px");
  });

  it("renders state dot with correct color for each state", () => {
    const states: { state: ProjectState; label: string; color: string }[] = [
      { state: "open", label: "Open", color: "rgb(2, 132, 199)" },
      { state: "in_review", label: "In Review", color: "rgb(245, 158, 11)" },
      { state: "accepted", label: "Accepted", color: "rgb(22, 163, 74)" },
      { state: "dropped", label: "Dropped", color: "rgb(156, 163, 175)" },
      { state: "rejected", label: "Rejected", color: "rgb(249, 115, 22)" },
    ];

    for (const { state, label, color } of states) {
      const { unmount } = renderProjectCard({ state });
      const dot = screen.getByLabelText(label);
      expect(dot.style.backgroundColor).toBe(color);
      unmount();
    }
  });

  it("renders title with ellipsis truncation class", () => {
    renderProjectCard({ title: "My Test Project" });
    const title = screen.getByText("My Test Project");
    expect(title).toBeInTheDocument();
    expect(title.className).toContain("truncate");
  });

  it("renders 'Untitled project' when title is empty", () => {
    renderProjectCard({ title: "" });
    expect(screen.getByText("Untitled project")).toBeInTheDocument();
  });

  it("renders relative timestamp", () => {
    renderProjectCard({
      updatedAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    });
    expect(screen.getByText("Last updated 30 minutes ago")).toBeInTheDocument();
  });

  it("renders state badge with correct text", () => {
    renderProjectCard({ state: "in_review" });
    expect(screen.getByText("In Review")).toBeInTheDocument();
  });

  it("renders Delete option in menu for active projects", async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    renderProjectCard({ onDelete, deletedAt: null });

    const triggers = screen.getAllByRole("button");
    await user.click(triggers[triggers.length - 1]!);

    expect(screen.getByText("Delete")).toBeInTheDocument();
  });

  it("renders Restore option in menu for trashed projects", async () => {
    const user = userEvent.setup();
    const onRestore = vi.fn();
    renderProjectCard({
      deletedAt: "2024-01-01T00:00:00Z",
      onRestore,
    });

    const triggers = screen.getAllByRole("button");
    await user.click(triggers[triggers.length - 1]!);

    expect(screen.getByText("Restore")).toBeInTheDocument();
  });

  it("clicking card navigates to /project/:uuid", async () => {
    const user = userEvent.setup();
    renderProjectCard({ id: "abc-123" });

    const card = screen.getByText("My Test Project").closest("button");
    expect(card).not.toBeNull();
    await user.click(card!);
    expect(mockNavigate).toHaveBeenCalledWith("/project/abc-123");
  });

  it("clicking three-dot menu does not trigger navigation", async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    renderProjectCard({ onDelete });

    const triggers = screen.getAllByRole("button");
    await user.click(triggers[triggers.length - 1]!);

    const deleteItem = screen.getByText("Delete");
    await user.click(deleteItem);

    expect(onDelete).toHaveBeenCalledWith("test-uuid-123");
    expect(mockNavigate).not.toHaveBeenCalled();
  });
});
