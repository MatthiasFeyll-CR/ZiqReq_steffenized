import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ParametersTab } from "@/features/admin/ParametersTab";
import type { AdminParameter } from "@/api/admin";

const mockParameters: AdminParameter[] = [
  {
    key: "debounce_timer",
    value: "3",
    default_value: "3",
    description: "Seconds after last chat before AI processes",
    data_type: "integer",
    category: "Application",
    updated_by: null,
    updated_at: "2026-01-01T00:00:00Z",
  },
  {
    key: "max_retry_attempts",
    value: "5",
    default_value: "3",
    description: "Max retry attempts for failed operations",
    data_type: "integer",
    category: "Infrastructure",
    updated_by: "user-1",
    updated_at: "2026-01-02T00:00:00Z",
  },
  {
    key: "default_app_language",
    value: "de",
    default_value: "de",
    description: "Default language for new users",
    data_type: "string",
    category: "Application",
    updated_by: null,
    updated_at: "2026-01-01T00:00:00Z",
  },
];

vi.mock("@/api/admin", () => ({
  fetchParameters: vi.fn(),
  patchParameter: vi.fn(),
}));

// suppress react-toastify in tests
vi.mock("react-toastify", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

import { fetchParameters, patchParameter } from "@/api/admin";

beforeEach(() => {
  vi.mocked(fetchParameters).mockReset();
  vi.mocked(patchParameter).mockReset();
});

describe("ParametersTab — UI-ADMIN.02: Parameters tab shows editable fields", () => {
  it("renders parameter table with all columns", async () => {
    vi.mocked(fetchParameters).mockResolvedValue(mockParameters);
    render(<ParametersTab />);

    await waitFor(() => {
      expect(screen.getByTestId("parameters-table")).toBeInTheDocument();
    });

    // Check headers
    expect(screen.getByText("Key")).toBeInTheDocument();
    expect(screen.getByText("Value")).toBeInTheDocument();
    expect(screen.getByText("Default")).toBeInTheDocument();
    expect(screen.getByText("Description")).toBeInTheDocument();
    expect(screen.getByText("Category")).toBeInTheDocument();

    // Check data rows
    expect(screen.getByText("debounce_timer")).toBeInTheDocument();
    expect(screen.getByText("max_retry_attempts")).toBeInTheDocument();
    expect(screen.getByText("default_app_language")).toBeInTheDocument();
  });

  it("shows gold indicator for modified parameters (value != default_value)", async () => {
    vi.mocked(fetchParameters).mockResolvedValue(mockParameters);
    render(<ParametersTab />);

    await waitFor(() => {
      expect(screen.getByTestId("parameters-table")).toBeInTheDocument();
    });

    // max_retry_attempts has value "5" but default "3" — should show indicator
    expect(screen.getByTestId("modified-indicator-max_retry_attempts")).toBeInTheDocument();

    // debounce_timer has same value and default — no indicator
    expect(screen.queryByTestId("modified-indicator-debounce_timer")).not.toBeInTheDocument();
    expect(screen.queryByTestId("modified-indicator-default_app_language")).not.toBeInTheDocument();
  });

  it("enters edit mode on double-click and shows input with current value", async () => {
    vi.mocked(fetchParameters).mockResolvedValue(mockParameters);
    const user = userEvent.setup();
    render(<ParametersTab />);

    await waitFor(() => {
      expect(screen.getByTestId("value-debounce_timer")).toBeInTheDocument();
    });

    await user.dblClick(screen.getByTestId("value-debounce_timer"));

    const input = screen.getByTestId("edit-input-debounce_timer");
    expect(input).toBeInTheDocument();
    expect(input).toHaveValue("3");
  });

  it("saves parameter on Enter key", async () => {
    vi.mocked(fetchParameters).mockResolvedValue(mockParameters);
    vi.mocked(patchParameter).mockResolvedValue({
      key: "debounce_timer",
      value: "10",
      default_value: "3",
      description: "Seconds after last chat before AI processes",
      data_type: "integer",
      category: "Application",
      updated_by: null,
      updated_at: "2026-01-01T00:00:00Z",
    });
    const user = userEvent.setup();
    render(<ParametersTab />);

    await waitFor(() => {
      expect(screen.getByTestId("value-debounce_timer")).toBeInTheDocument();
    });

    await user.dblClick(screen.getByTestId("value-debounce_timer"));

    const input = screen.getByTestId("edit-input-debounce_timer");
    await user.clear(input);
    await user.type(input, "10{Enter}");

    await waitFor(() => {
      expect(patchParameter).toHaveBeenCalledWith("debounce_timer", "10");
    });
  });

  it("cancels editing on Escape key", async () => {
    vi.mocked(fetchParameters).mockResolvedValue(mockParameters);
    const user = userEvent.setup();
    render(<ParametersTab />);

    await waitFor(() => {
      expect(screen.getByTestId("value-debounce_timer")).toBeInTheDocument();
    });

    await user.dblClick(screen.getByTestId("value-debounce_timer"));
    expect(screen.getByTestId("edit-input-debounce_timer")).toBeInTheDocument();

    await user.keyboard("{Escape}");

    // Should exit edit mode — no more input
    expect(screen.queryByTestId("edit-input-debounce_timer")).not.toBeInTheDocument();
    // Original value still shown
    expect(screen.getByTestId("value-debounce_timer")).toHaveTextContent("3");
  });

  it("displays current values in the table cells", async () => {
    vi.mocked(fetchParameters).mockResolvedValue(mockParameters);
    render(<ParametersTab />);

    await waitFor(() => {
      expect(screen.getByTestId("parameters-table")).toBeInTheDocument();
    });

    expect(screen.getByTestId("value-debounce_timer")).toHaveTextContent("3");
    expect(screen.getByTestId("value-max_retry_attempts")).toHaveTextContent("5");
    expect(screen.getByTestId("value-default_app_language")).toHaveTextContent("de");
  });
});
