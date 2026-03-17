import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import i18n from "@/i18n/config";
import { HeroSection } from "../HeroSection";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

function renderHero() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <HeroSection />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("T-3.1.01: HeroSection shows two type options", () => {
  it("renders Software and Non-Software cards", () => {
    renderHero();

    expect(screen.getByTestId("new-project-software")).toBeInTheDocument();
    expect(screen.getByTestId("new-project-non_software")).toBeInTheDocument();
    expect(screen.getByText("Software Project")).toBeInTheDocument();
    expect(screen.getByText("Non-Software Project")).toBeInTheDocument();
    expect(screen.getByText("Epics & User Stories")).toBeInTheDocument();
    expect(screen.getByText("Milestones & Work Packages")).toBeInTheDocument();
  });
});

describe("T-3.1.03: Project created with selected type on single click", () => {
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
          owner: null,
          created_at: "2026-03-17T00:00:00Z",
        }),
    });
    vi.stubGlobal("fetch", mockFetch);

    renderHero();
    const user = userEvent.setup();

    await user.click(screen.getByTestId("new-project-software"));

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

  it("sends non_software type when Non-Software card is clicked", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          id: "ns-project-uuid",
          title: "",
          project_type: "non_software",
          state: "open",
          visibility: "private",
          owner: null,
          created_at: "2026-03-17T00:00:00Z",
        }),
    });
    vi.stubGlobal("fetch", mockFetch);

    renderHero();
    const user = userEvent.setup();

    await user.click(screen.getByTestId("new-project-non_software"));

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
