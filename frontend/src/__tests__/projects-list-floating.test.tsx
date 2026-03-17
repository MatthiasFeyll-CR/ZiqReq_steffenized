import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ProjectsListFloating } from "@/components/layout/ProjectsListFloating";
import { useProjectsByState } from "@/hooks/use-projects-by-state";
import i18n from "@/i18n/config";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

vi.mock("@/hooks/use-projects-by-state");
vi.mock("@/hooks/use-highlighted-projects");

import { useHighlightedProjects } from "@/hooks/use-highlighted-projects";

function createQueryClient() {
  return new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
}

const mockProjects = [
  { id: "id-1", title: "First Project", state: "open", visibility: "private", role: "owner", owner: null, collaborator_count: 0, updated_at: new Date().toISOString(), deleted_at: null },
  { id: "id-2", title: "Second Project", state: "open", visibility: "private", role: "owner", owner: null, collaborator_count: 0, updated_at: new Date().toISOString(), deleted_at: null },
];

function mockHookReturn(projects = mockProjects, isLoading = false) {
  return { data: { results: projects, count: projects.length, next: null, previous: null }, isLoading, isError: false, error: null } as never;
}

function renderFloating(onClose = vi.fn()) {
  const qc = createQueryClient();
  render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <ProjectsListFloating onClose={onClose} />
      </MemoryRouter>
    </QueryClientProvider>,
  );
  return onClose;
}

describe("ProjectsListFloating", () => {
  beforeEach(() => {
    mockNavigate.mockClear();
    vi.mocked(useProjectsByState).mockReturnValue(mockHookReturn());
    vi.mocked(useHighlightedProjects).mockReturnValue({ data: { results: [] }, isLoading: false } as never);
  });

  it("renders all 4 tabs", () => {
    renderFloating();
    expect(screen.getByRole("tab", { name: "Active" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "In Review" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Accepted" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Closed" })).toBeInTheDocument();
  });

  it("renders projects in the active tab after switching", async () => {
    const user = userEvent.setup();
    renderFloating();
    await user.click(screen.getByRole("tab", { name: "Active" }));
    expect(screen.getByText("First Project")).toBeInTheDocument();
    expect(screen.getByText("Second Project")).toBeInTheDocument();
  });

  it("shows empty message when no projects in active tab", async () => {
    vi.mocked(useProjectsByState).mockReturnValue(mockHookReturn([]));
    const user = userEvent.setup();
    renderFloating();
    await user.click(screen.getByRole("tab", { name: "Active" }));
    expect(screen.getByText(/No active projects/)).toBeInTheDocument();
  });

  it("shows loading state", async () => {
    vi.mocked(useProjectsByState).mockReturnValue(mockHookReturn([], true));
    const user = userEvent.setup();
    renderFloating();
    await user.click(screen.getByRole("tab", { name: "Active" }));
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("navigates to project and closes on click", async () => {
    const user = userEvent.setup();
    const onClose = renderFloating();
    await user.click(screen.getByRole("tab", { name: "Active" }));
    await user.click(screen.getByText("First Project"));
    expect(mockNavigate).toHaveBeenCalledWith("/project/id-1");
    expect(onClose).toHaveBeenCalled();
  });

  it("closes on Escape key", () => {
    const onClose = renderFloating();
    fireEvent.keyDown(document, { key: "Escape" });
    expect(onClose).toHaveBeenCalled();
  });

  it("closes on click outside", () => {
    const onClose = renderFloating();
    fireEvent.mouseDown(document.body);
    expect(onClose).toHaveBeenCalled();
  });

  it("switches tabs", async () => {
    const user = userEvent.setup();
    renderFloating();
    await user.click(screen.getByRole("tab", { name: "Closed" }));
    expect(useProjectsByState).toHaveBeenCalledWith("dropped");
  });
});
