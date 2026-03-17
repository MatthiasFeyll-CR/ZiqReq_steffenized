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

function createQueryClient() {
  return new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
}

const mockIdeas = [
  { id: "id-1", title: "First Idea", state: "open", visibility: "private", role: "owner", owner: null, collaborator_count: 0, updated_at: new Date().toISOString(), deleted_at: null },
  { id: "id-2", title: "Second Idea", state: "open", visibility: "private", role: "owner", owner: null, collaborator_count: 0, updated_at: new Date().toISOString(), deleted_at: null },
];

function mockHookReturn(ideas = mockIdeas, isLoading = false) {
  return { data: { results: ideas, count: ideas.length, next: null, previous: null }, isLoading, isError: false, error: null } as never;
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
  });

  it("renders all 4 tabs", () => {
    renderFloating();
    expect(screen.getByRole("tab", { name: "Active" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "In Review" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Accepted" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Closed" })).toBeInTheDocument();
  });

  it("renders ideas in the active tab by default", () => {
    renderFloating();
    expect(screen.getByText("First Idea")).toBeInTheDocument();
    expect(screen.getByText("Second Idea")).toBeInTheDocument();
  });

  it("shows empty message when no ideas", () => {
    vi.mocked(useProjectsByState).mockReturnValue(mockHookReturn([]));
    renderFloating();
    expect(screen.getByText(/No active ideas/)).toBeInTheDocument();
  });

  it("shows loading state", () => {
    vi.mocked(useProjectsByState).mockReturnValue(mockHookReturn([], true));
    renderFloating();
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("navigates to idea and closes on click", async () => {
    const user = userEvent.setup();
    const onClose = renderFloating();
    await user.click(screen.getByText("First Idea"));
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
