import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MonitoringTab } from "@/features/admin/MonitoringTab";
import type { MonitoringData, AlertConfig } from "@/api/admin";

const mockMonitoringData: MonitoringData = {
  active_connections: 42,
  projects_by_state: {
    open: 10,
    in_review: 5,
    accepted: 20,
    dropped: 2,
    rejected: 3,
  },
  active_users: 150,
  online_users: 30,
  ai_processing: {
    request_count: 1234,
    success_count: 1200,
    failure_count: 34,
  },
  system_health: {
    gateway: { status: "healthy", last_check: "2026-01-01T00:00:00Z" },
    ai: { status: "healthy", last_check: "2026-01-01T00:00:00Z" },
    pdf: { status: "unhealthy", last_check: "2026-01-01T00:00:00Z" },
    database: { status: "healthy", last_check: "2026-01-01T00:00:00Z" },
    redis: { status: "healthy", last_check: "2026-01-01T00:00:00Z" },
    broker: { status: "healthy", last_check: "2026-01-01T00:00:00Z" },
  },
};

const mockAlertConfig: AlertConfig = {
  user_id: "user-1",
  is_active: false,
};

vi.mock("@/api/admin", () => ({
  fetchMonitoringData: vi.fn(),
  fetchAlertConfig: vi.fn(),
  patchAlertConfig: vi.fn(),
}));

vi.mock("react-toastify", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

import { fetchMonitoringData, fetchAlertConfig } from "@/api/admin";

beforeEach(() => {
  vi.mocked(fetchMonitoringData).mockReset();
  vi.mocked(fetchAlertConfig).mockReset();
});

describe("MonitoringTab — UI-ADMIN.03: Monitoring dashboard renders stats", () => {
  it("renders KPI cards with correct values", async () => {
    vi.mocked(fetchMonitoringData).mockResolvedValue(mockMonitoringData);
    vi.mocked(fetchAlertConfig).mockResolvedValue(mockAlertConfig);
    render(<MonitoringTab />);

    await waitFor(() => {
      expect(screen.getByTestId("kpi-active-connections")).toBeInTheDocument();
    });

    expect(screen.getByTestId("kpi-active-connections")).toHaveTextContent("42");
    expect(screen.getByTestId("kpi-active-users")).toHaveTextContent("150");
    expect(screen.getByTestId("kpi-ai-requests")).toHaveTextContent("1234");
  });

  it("renders service health table with status dots", async () => {
    vi.mocked(fetchMonitoringData).mockResolvedValue(mockMonitoringData);
    vi.mocked(fetchAlertConfig).mockResolvedValue(mockAlertConfig);
    render(<MonitoringTab />);

    await waitFor(() => {
      expect(screen.getByTestId("service-health-table")).toBeInTheDocument();
    });

    // Check green dot for healthy service
    const gatewayDot = screen.getByTestId("health-dot-gateway");
    expect(gatewayDot).toHaveClass("bg-green-500");

    // Check red dot for unhealthy service
    const pdfDot = screen.getByTestId("health-dot-pdf");
    expect(pdfDot).toHaveClass("bg-red-500");
  });

  it("renders projects by state breakdown", async () => {
    vi.mocked(fetchMonitoringData).mockResolvedValue(mockMonitoringData);
    vi.mocked(fetchAlertConfig).mockResolvedValue(mockAlertConfig);
    render(<MonitoringTab />);

    await waitFor(() => {
      expect(screen.getAllByText("Projects by State").length).toBeGreaterThanOrEqual(1);
    });

    expect(screen.getByText("10")).toBeInTheDocument();
    expect(screen.getByText("20")).toBeInTheDocument();
  });

  it("renders alert toggle", async () => {
    vi.mocked(fetchMonitoringData).mockResolvedValue(mockMonitoringData);
    vi.mocked(fetchAlertConfig).mockResolvedValue(mockAlertConfig);
    render(<MonitoringTab />);

    await waitFor(() => {
      expect(screen.getByTestId("alert-toggle")).toBeInTheDocument();
    });

    expect(screen.getByText("Receive monitoring alerts")).toBeInTheDocument();
    expect(screen.getByTestId("alert-toggle-switch")).toHaveAttribute("aria-checked", "false");
  });

  it("shows loading state initially", () => {
    vi.mocked(fetchMonitoringData).mockReturnValue(new Promise(() => {}));
    vi.mocked(fetchAlertConfig).mockReturnValue(new Promise(() => {}));
    render(<MonitoringTab />);

    expect(screen.getByText("Loading monitoring data...")).toBeInTheDocument();
  });
});
