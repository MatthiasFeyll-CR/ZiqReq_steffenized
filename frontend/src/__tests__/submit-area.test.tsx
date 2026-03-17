import { describe, it, expect, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import i18n from "@/i18n/config";
import { SubmitArea } from "@/components/review/SubmitArea";

beforeAll(async () => {
  await i18n.changeLanguage("en");
});

const { mockSubmitIdea, mockFetchReviewerUsers, mockToastSuccess, mockToastError } = vi.hoisted(() => {
  return {
    mockSubmitIdea: vi.fn(),
    mockFetchReviewerUsers: vi.fn(),
    mockToastSuccess: vi.fn(),
    mockToastError: vi.fn(),
  };
});

vi.mock("@/api/projects", async () => {
  const actual = await vi.importActual("@/api/projects");
  return {
    ...actual,
    submitProject: mockSubmitIdea,
  };
});

vi.mock("@/api/review", async () => {
  const actual = await vi.importActual("@/api/review");
  return {
    ...actual,
    fetchReviewerUsers: mockFetchReviewerUsers,
  };
});

vi.mock("react-toastify", () => ({
  toast: Object.assign(vi.fn(), {
    success: mockToastSuccess,
    error: mockToastError,
  }),
  ToastContainer: () => null,
}));

const PROJECT_ID = "00000000-0000-0000-0000-000000000001";

const MOCK_REVIEWERS = [
  { id: "rev-1", display_name: "Alice Reviewer", email: "alice@test.com" },
  { id: "rev-2", display_name: "Bob Reviewer", email: "bob@test.com" },
];

function createQueryClient() {
  return new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
}

function renderSubmitArea(projectState = "open", onSubmitted?: () => void) {
  const qc = createQueryClient();
  return render(
    <QueryClientProvider client={qc}>
      <SubmitArea projectId={PROJECT_ID} projectState={projectState} onSubmitted={onSubmitted} />
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  vi.resetAllMocks();
  mockFetchReviewerUsers.mockResolvedValue(MOCK_REVIEWERS);
});

describe("SubmitArea visibility", () => {
  it("renders when state is open", async () => {
    renderSubmitArea("open");
    expect(screen.getByTestId("submit-area")).toBeInTheDocument();
  });

  it("renders when state is rejected", async () => {
    renderSubmitArea("rejected");
    expect(screen.getByTestId("submit-area")).toBeInTheDocument();
  });

  it("does not render when state is in_review", () => {
    renderSubmitArea("in_review");
    expect(screen.queryByTestId("submit-area")).not.toBeInTheDocument();
  });

  it("does not render when state is accepted", () => {
    renderSubmitArea("accepted");
    expect(screen.queryByTestId("submit-area")).not.toBeInTheDocument();
  });
});

describe("UI-SUBMIT.01: Submit with message and reviewers", () => {
  it("submits with message and selected reviewers", async () => {
    const user = userEvent.setup();
    mockSubmitIdea.mockResolvedValue({
      version_number: 1,
      pdf_url: "/api/projects/1/brd/versions/1/pdf",
      state: "in_review",
    });

    renderSubmitArea("open");

    // Wait for reviewers to load
    await waitFor(() => {
      expect(screen.getByText("Alice Reviewer")).toBeInTheDocument();
    });

    // Fill message
    const textarea = screen.getByTestId("submit-message");
    await user.type(textarea, "Please review this idea");

    // Select reviewers
    const checkboxes = screen.getAllByRole("checkbox");
    await user.click(checkboxes[0]!); // Alice
    await user.click(checkboxes[1]!); // Bob

    // Click submit
    await user.click(screen.getByTestId("submit-button"));

    await waitFor(() => {
      expect(mockSubmitIdea).toHaveBeenCalledWith(PROJECT_ID, {
        message: "Please review this idea",
        reviewer_ids: ["rev-1", "rev-2"],
      });
    });

    expect(mockToastSuccess).toHaveBeenCalledWith("Project submitted");
  });
});

describe("UI-SUBMIT.02: Submit without optional fields", () => {
  it("submits with no message and no reviewers", async () => {
    const user = userEvent.setup();
    mockSubmitIdea.mockResolvedValue({
      version_number: 1,
      pdf_url: "/api/projects/1/brd/versions/1/pdf",
      state: "in_review",
    });

    renderSubmitArea("open");

    await user.click(screen.getByTestId("submit-button"));

    await waitFor(() => {
      expect(mockSubmitIdea).toHaveBeenCalledWith(PROJECT_ID, {
        message: undefined,
        reviewer_ids: undefined,
      });
    });

    expect(mockToastSuccess).toHaveBeenCalledWith("Project submitted");
  });
});

describe("UI-SUBMIT.03: Submit error handling", () => {
  it("shows error toast on API failure", async () => {
    const user = userEvent.setup();
    mockSubmitIdea.mockRejectedValue(new Error("Invalid state"));

    renderSubmitArea("open");

    await user.click(screen.getByTestId("submit-button"));

    await waitFor(() => {
      expect(mockToastError).toHaveBeenCalled();
    });
  });
});

describe("SubmitArea callbacks", () => {
  it("calls onSubmitted callback on success", async () => {
    const user = userEvent.setup();
    const onSubmitted = vi.fn();
    mockSubmitIdea.mockResolvedValue({
      version_number: 1,
      pdf_url: "/url",
      state: "in_review",
    });

    renderSubmitArea("open", onSubmitted);

    await user.click(screen.getByTestId("submit-button"));

    await waitFor(() => {
      expect(onSubmitted).toHaveBeenCalled();
    });
  });
});

describe("SubmitArea reviewer selector", () => {
  it("shows reviewer list from API", async () => {
    renderSubmitArea("open");

    await waitFor(() => {
      expect(screen.getByText("Alice Reviewer")).toBeInTheDocument();
      expect(screen.getByText("Bob Reviewer")).toBeInTheDocument();
    });
  });

  it("hides reviewer selector when no reviewers available", async () => {
    mockFetchReviewerUsers.mockResolvedValue([]);
    renderSubmitArea("open");

    // Wait a tick for query to resolve
    await waitFor(() => {
      expect(mockFetchReviewerUsers).toHaveBeenCalled();
    });

    expect(screen.queryByTestId("reviewer-selector")).not.toBeInTheDocument();
  });
});
