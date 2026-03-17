import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AIContextTab } from "@/features/admin/AIContextTab";

// Mock react-i18next
vi.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (key: string, fallback?: string) => {
      const translations: Record<string, string> = {
        "admin.facilitatorTitle": "Facilitator Context (Table of Contents)",
        "admin.companyTitle": "Company Context",
        "admin.facilitatorPlaceholder": "Enter facilitator context...",
        "admin.freeTextPlaceholder": "Enter free text...",
        "admin.sectionsJson": "Sections (JSON)",
        "admin.freeText": "Free Text",
        "admin.saveFacilitator": "Save Facilitator",
        "admin.saveCompany": "Save Company",
        "admin.facilitatorSaved": "Facilitator context saved",
        "admin.companySaved": "Company context saved",
        "admin.failedLoadFacilitator": "Failed to load facilitator context",
        "admin.failedLoadCompany": "Failed to load company context",
        "admin.failedSaveFacilitator": "Failed to save facilitator context",
        "admin.failedSaveCompany": "Failed to save company context",
        "admin.invalidJson": "Invalid JSON",
        "common.loading": "Loading...",
        "common.saving": "Saving...",
      };
      return translations[key] || fallback || key;
    },
  }),
}));

// Mock toast
vi.mock("react-toastify", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

// Mock API functions
const mockFetchFacilitator = vi.fn();
const mockPatchFacilitator = vi.fn();
const mockFetchCompany = vi.fn();
const mockPatchCompany = vi.fn();

vi.mock("@/api/admin", () => ({
  fetchFacilitatorContext: (...args: unknown[]) => mockFetchFacilitator(...args),
  patchFacilitatorContext: (...args: unknown[]) => mockPatchFacilitator(...args),
  fetchCompanyContext: (...args: unknown[]) => mockFetchCompany(...args),
  patchCompanyContext: (...args: unknown[]) => mockPatchCompany(...args),
}));

beforeEach(() => {
  vi.clearAllMocks();
  mockFetchFacilitator.mockResolvedValue({
    id: "fac-1",
    context_type: "global",
    content: "Global facilitator content",
    updated_by: null,
    updated_at: "2026-01-01T00:00:00Z",
  });
  mockFetchCompany.mockResolvedValue({
    id: "comp-1",
    context_type: "global",
    content: "",
    sections: {},
    free_text: "",
    updated_by: null,
    updated_at: "2026-01-01T00:00:00Z",
  });
});

describe("AIContextTab — US-004: Segmented control", () => {
  it("renders three context type tabs: Global, Software, Non-Software", async () => {
    render(<AIContextTab />);

    const tabs = screen.getByTestId("context-type-tabs");
    expect(tabs).toBeInTheDocument();

    expect(screen.getByTestId("context-tab-global")).toHaveTextContent("Global");
    expect(screen.getByTestId("context-tab-software")).toHaveTextContent("Software");
    expect(screen.getByTestId("context-tab-non_software")).toHaveTextContent("Non-Software");
  });

  it("Global tab is active by default", async () => {
    render(<AIContextTab />);

    const globalTab = screen.getByTestId("context-tab-global");
    expect(globalTab).toHaveAttribute("aria-selected", "true");
  });

  it("fetches global context on initial render", async () => {
    render(<AIContextTab />);

    await waitFor(() => {
      expect(mockFetchFacilitator).toHaveBeenCalledWith("global");
      expect(mockFetchCompany).toHaveBeenCalledWith("global");
    });
  });

  it("switches to Software tab and fetches software context", async () => {
    render(<AIContextTab />);
    const user = userEvent.setup();

    await waitFor(() => {
      expect(mockFetchFacilitator).toHaveBeenCalledWith("global");
    });

    mockFetchFacilitator.mockResolvedValue({
      id: "fac-2",
      context_type: "software",
      content: "Software facilitator content",
      updated_by: null,
      updated_at: "2026-01-01T00:00:00Z",
    });
    mockFetchCompany.mockResolvedValue({
      id: "comp-2",
      context_type: "software",
      sections: {},
      free_text: "",
      updated_by: null,
      updated_at: "2026-01-01T00:00:00Z",
    });

    await user.click(screen.getByTestId("context-tab-software"));

    await waitFor(() => {
      expect(mockFetchFacilitator).toHaveBeenCalledWith("software");
      expect(mockFetchCompany).toHaveBeenCalledWith("software");
    });

    expect(screen.getByTestId("context-tab-software")).toHaveAttribute(
      "aria-selected",
      "true",
    );
  });

  it("switches to Non-Software tab and fetches non_software context", async () => {
    render(<AIContextTab />);
    const user = userEvent.setup();

    await waitFor(() => {
      expect(mockFetchFacilitator).toHaveBeenCalledWith("global");
    });

    mockFetchFacilitator.mockResolvedValue({
      id: "fac-3",
      context_type: "non_software",
      content: "",
      updated_by: null,
      updated_at: "2026-01-01T00:00:00Z",
    });
    mockFetchCompany.mockResolvedValue({
      id: "comp-3",
      context_type: "non_software",
      sections: {},
      free_text: "",
      updated_by: null,
      updated_at: "2026-01-01T00:00:00Z",
    });

    await user.click(screen.getByTestId("context-tab-non_software"));

    await waitFor(() => {
      expect(mockFetchFacilitator).toHaveBeenCalledWith("non_software");
      expect(mockFetchCompany).toHaveBeenCalledWith("non_software");
    });
  });

  it("saves facilitator context with the active context type", async () => {
    mockPatchFacilitator.mockResolvedValue({
      id: "fac-1",
      context_type: "global",
      content: "Updated content",
      updated_by: "user-1",
      updated_at: "2026-01-01T00:00:00Z",
    });

    render(<AIContextTab />);
    const user = userEvent.setup();

    await waitFor(() => {
      expect(screen.getByTestId("facilitator-textarea")).toBeInTheDocument();
    });

    await user.click(screen.getByText("Save Facilitator"));

    await waitFor(() => {
      // Should save with whatever content was loaded (from mock) and with global type
      expect(mockPatchFacilitator).toHaveBeenCalledWith(
        expect.any(String),
        "global",
      );
    });
  });

  it("saves company context with the active context type", async () => {
    mockPatchCompany.mockResolvedValue({
      id: "comp-1",
      context_type: "global",
      sections: { key: "val" },
      free_text: "notes",
      updated_by: "user-1",
      updated_at: "2026-01-01T00:00:00Z",
    });

    render(<AIContextTab />);
    const user = userEvent.setup();

    await waitFor(() => {
      expect(screen.getByTestId("sections-textarea")).toBeInTheDocument();
    });

    const sectionsTextarea = screen.getByTestId("sections-textarea");
    await user.clear(sectionsTextarea);
    await user.type(sectionsTextarea, '{{"key":"val"}}');

    const freeTextarea = screen.getByTestId("freetext-textarea");
    await user.type(freeTextarea, "notes");

    await user.click(screen.getByText("Save Company"));

    await waitFor(() => {
      expect(mockPatchCompany).toHaveBeenCalledWith(
        expect.any(Object),
        expect.any(String),
        "global",
      );
    });
  });
});
