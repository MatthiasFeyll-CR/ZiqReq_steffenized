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

  it("navigates to /project/new?type=software on click", async () => {
    renderHero();
    const user = userEvent.setup();

    await user.click(screen.getByTestId("new-project-software"));

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/project/new?type=software");
    });
  });

  it("navigates to /project/new?type=non_software when Non-Software card is clicked", async () => {
    renderHero();
    const user = userEvent.setup();

    await user.click(screen.getByTestId("new-project-non_software"));

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/project/new?type=non_software");
    });
  });
});
