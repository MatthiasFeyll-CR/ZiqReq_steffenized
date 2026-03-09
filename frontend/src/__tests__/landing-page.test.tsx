import { describe, it, expect, vi, beforeAll } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createElement } from "react";
import { MemoryRouter } from "react-router-dom";
import { AuthContext } from "@/hooks/use-auth";
import type { AuthContextValue } from "@/hooks/use-auth";
import LandingPage from "@/pages/LandingPage";
import i18n from "@/i18n/config";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

function createAuthValue(): AuthContextValue {
  return {
    user: {
      id: "00000000-0000-0000-0000-000000000001",
      email: "alice@dev.local",
      first_name: "Alice",
      last_name: "Admin",
      display_name: "Alice Admin",
      roles: ["admin", "reviewer", "user"],
    },
    isAuthenticated: true,
    isDevBypass: true,
    hasRole: () => true,
    logout: vi.fn(),
    setUser: vi.fn(),
  };
}

function renderLandingPage(props = {}) {
  const authValue = createAuthValue();
  return render(
    <MemoryRouter>
      {createElement(
        AuthContext.Provider,
        { value: authValue },
        <LandingPage {...props} />,
      )}
    </MemoryRouter>,
  );
}

describe("T-9.1.01: Landing page renders all 4 lists", () => {
  it("renders hero section with heading, subtext, input, and submit button", () => {
    renderLandingPage();

    expect(screen.getByText("Start a new brainstorm")).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText("Describe your idea..."),
    ).toBeInTheDocument();
    expect(screen.getByText("Begin")).toBeInTheDocument();
  });

  it("renders all 4 section headings", () => {
    renderLandingPage();

    expect(screen.getByText("My Ideas")).toBeInTheDocument();
    expect(screen.getByText("Collaborating")).toBeInTheDocument();
    expect(screen.getByText("Invitations")).toBeInTheDocument();
    expect(screen.getByText("Trash")).toBeInTheDocument();
  });

  it("renders empty states when no data provided", () => {
    renderLandingPage();

    expect(screen.getByText("Start your first brainstorm")).toBeInTheDocument();
    expect(screen.getByText("No collaborations yet")).toBeInTheDocument();
    expect(screen.getByText("No pending invitations")).toBeInTheDocument();
    expect(screen.getByText("Trash is empty")).toBeInTheDocument();
  });

  it("renders count badges showing 0 for empty lists", () => {
    renderLandingPage();

    const zeros = screen.getAllByText("0");
    expect(zeros.length).toBe(4);
  });

  it("renders ideas in My Ideas list with correct count", () => {
    renderLandingPage({
      myIdeas: [
        { id: "1", title: "First idea", state: "open", updatedAt: "2024-01-01" },
        { id: "2", title: "Second idea", state: "open", updatedAt: "2024-01-02" },
      ],
    });

    expect(screen.getByText("First idea")).toBeInTheDocument();
    expect(screen.getByText("Second idea")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
  });

  it("renders invitations in Invitations list", () => {
    renderLandingPage({
      invitations: [
        {
          id: "inv-1",
          ideaId: "idea-1",
          ideaTitle: "Collab idea",
          inviterName: "Bob",
          createdAt: "2024-01-01",
        },
      ],
    });

    expect(screen.getByText("Collab idea")).toBeInTheDocument();
    expect(screen.getByText("From Bob")).toBeInTheDocument();
  });

  it("clicking an idea card navigates to /idea/:uuid", async () => {
    const user = userEvent.setup();
    renderLandingPage({
      myIdeas: [
        { id: "abc-123", title: "Navigate me", state: "open", updatedAt: "2024-01-01" },
      ],
    });

    await user.click(screen.getByText("Navigate me"));
    expect(mockNavigate).toHaveBeenCalledWith("/idea/abc-123");
  });

  it("uses PageShell layout with Navbar", () => {
    renderLandingPage();

    // Navbar renders ZiqReq brand text
    expect(screen.getByText("ZiqReq")).toBeInTheDocument();
  });
});
