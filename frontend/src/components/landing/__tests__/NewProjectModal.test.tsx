import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import i18n from "@/i18n/config";
import { NewProjectModal } from "../NewProjectModal";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

function renderModal(props: { open?: boolean; onOpenChange?: (v: boolean) => void } = {}) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  const onOpenChange = props.onOpenChange ?? vi.fn();
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <NewProjectModal open={props.open ?? true} onOpenChange={onOpenChange} />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("T-3.1.01: NewProjectModal shows two type options", () => {
  it("renders Software and Non-Software cards when open", () => {
    renderModal();

    expect(screen.getByTestId("project-type-software")).toBeInTheDocument();
    expect(screen.getByTestId("project-type-non_software")).toBeInTheDocument();
    expect(screen.getByText("Software Project")).toBeInTheDocument();
    expect(screen.getByText("Non-Software Project")).toBeInTheDocument();
    expect(screen.getByText("Epics & User Stories")).toBeInTheDocument();
    expect(screen.getByText("Milestones & Work Packages")).toBeInTheDocument();
  });

  it("shows modal title and description", () => {
    renderModal();

    expect(screen.getByText("Create New Project")).toBeInTheDocument();
    expect(
      screen.getByText("Choose the type of project you want to create."),
    ).toBeInTheDocument();
  });
});

describe("T-3.1.02: Create button disabled until selection", () => {
  it("disables Create button when no type is selected", () => {
    renderModal();

    const createBtn = screen.getByTestId("create-project-button");
    expect(createBtn).toBeDisabled();
  });

  it("enables Create button after selecting a type", async () => {
    renderModal();
    const user = userEvent.setup();

    await user.click(screen.getByTestId("project-type-software"));

    const createBtn = screen.getByTestId("create-project-button");
    expect(createBtn).not.toBeDisabled();
  });
});

describe("T-3.1.03: Project created with selected type", () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  it("sends project_type in POST and navigates to /project/:id", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          id: "new-project-uuid",
          title: "",
          project_type: "software",
          state: "open",
          visibility: "private",
          agent_mode: "interactive",
          owner: null,
          created_at: "2026-03-17T00:00:00Z",
        }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const onOpenChange = vi.fn();
    renderModal({ onOpenChange });
    const user = userEvent.setup();

    await user.click(screen.getByTestId("project-type-software"));
    await user.click(screen.getByTestId("create-project-button"));

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/project/new-project-uuid");
    });

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/projects/"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ project_type: "software" }),
      }),
    );

    vi.unstubAllGlobals();
  });

  it("sends non_software type when Non-Software card is selected", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          id: "ns-project-uuid",
          title: "",
          project_type: "non_software",
          state: "open",
          visibility: "private",
          agent_mode: "interactive",
          owner: null,
          created_at: "2026-03-17T00:00:00Z",
        }),
    });
    vi.stubGlobal("fetch", mockFetch);

    renderModal();
    const user = userEvent.setup();

    await user.click(screen.getByTestId("project-type-non_software"));
    await user.click(screen.getByTestId("create-project-button"));

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("/projects/"),
        expect.objectContaining({
          body: JSON.stringify({ project_type: "non_software" }),
        }),
      );
    });

    vi.unstubAllGlobals();
  });
});
