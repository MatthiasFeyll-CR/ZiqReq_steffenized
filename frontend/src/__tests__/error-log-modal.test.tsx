import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { ErrorLogModal } from "@/components/common/ErrorLogModal";
import {
  startCapturing,
  stopCapturing,
  getConsoleLogs,
  clearConsoleLogs,
  buildTechnicalDetails,
  buildNetworkResponse,
  buildErrorLogData,
} from "@/utils/errorLogger";
import type {
  ConsoleLogEntry,
  NetworkResponseInfo,
  TechnicalDetails,
} from "@/utils/errorLogger";

describe("T-14.1.02: Show Logs opens modal with details", () => {
  it("renders modal with all four sections", () => {
    const consoleLogs: ConsoleLogEntry[] = [
      { message: "Test error 1", timestamp: "2026-01-01T00:00:00.000Z" },
      { message: "Test error 2", timestamp: "2026-01-01T00:01:00.000Z" },
    ];
    const networkResponse: NetworkResponseInfo = {
      status: 500,
      statusText: "Internal Server Error",
      body: '{"error":"something broke"}',
    };
    const technicalDetails: TechnicalDetails = {
      errorCode: "ERR_API_FAIL",
      timestamp: "2026-01-01T00:00:00.000Z",
      userAgent: "TestAgent/1.0",
      url: "http://localhost:3000/test",
    };

    render(
      <ErrorLogModal
        open={true}
        onOpenChange={vi.fn()}
        consoleLogs={consoleLogs}
        networkResponse={networkResponse}
        technicalDetails={technicalDetails}
      />,
    );

    // Modal is present
    expect(screen.getByTestId("error-log-modal")).toBeInTheDocument();

    // Console log section shows entries
    expect(screen.getByTestId("console-log-section")).toBeInTheDocument();
    expect(screen.getByText("Test error 1")).toBeInTheDocument();
    expect(screen.getByText("Test error 2")).toBeInTheDocument();

    // Network response section
    expect(screen.getByTestId("network-response-section")).toBeInTheDocument();
    expect(screen.getByTestId("network-status").textContent).toContain("500");
    expect(screen.getByTestId("network-status").textContent).toContain(
      "Internal Server Error",
    );
    expect(screen.getByTestId("network-body").textContent).toContain(
      "something broke",
    );

    // Technical details section
    expect(
      screen.getByTestId("technical-details-section"),
    ).toBeInTheDocument();
    expect(screen.getByTestId("error-code").textContent).toBe("ERR_API_FAIL");
    expect(screen.getByTestId("error-timestamp").textContent).toBe(
      "2026-01-01T00:00:00.000Z",
    );
    expect(screen.getByTestId("error-user-agent").textContent).toBe(
      "TestAgent/1.0",
    );
    expect(screen.getByTestId("error-url").textContent).toBe(
      "http://localhost:3000/test",
    );

    // Support contact section
    expect(screen.getByTestId("support-contact-section")).toBeInTheDocument();
    expect(
      screen.getByText(/contact support at/i),
    ).toBeInTheDocument();
    expect(screen.getByText("support@commerzreal.de")).toBeInTheDocument();
  });

  it("shows empty state messages when no data provided", () => {
    render(
      <ErrorLogModal open={true} onOpenChange={vi.fn()} />,
    );

    expect(
      screen.getByText("No console errors recorded."),
    ).toBeInTheDocument();
    expect(
      screen.getByText("No network response data."),
    ).toBeInTheDocument();
    expect(
      screen.getByText("No technical details available."),
    ).toBeInTheDocument();
    // Support contact always shows
    expect(screen.getByText("support@commerzreal.de")).toBeInTheDocument();
  });

  it("displays legacy errors array in console log section", () => {
    render(
      <ErrorLogModal
        open={true}
        onOpenChange={vi.fn()}
        errors={[
          { id: "1", message: "Legacy error", timestamp: "2026-01-01T00:00:00Z" },
        ]}
      />,
    );

    expect(screen.getByText("Legacy error")).toBeInTheDocument();
  });
});

describe("errorLogger utility", () => {
  beforeEach(() => {
    clearConsoleLogs();
  });

  afterEach(() => {
    stopCapturing();
    clearConsoleLogs();
  });

  it("captures console.error messages (max 20)", () => {
    startCapturing();

    for (let i = 0; i < 25; i++) {
      console.error(`Error ${i}`);
    }

    const logs = getConsoleLogs();
    expect(logs).toHaveLength(20);
    // First 5 should have been evicted
    expect(logs[0]!.message).toBe("Error 5");
    expect(logs[19]!.message).toBe("Error 24");
  });

  it("stopCapturing restores original console.error", () => {
    const originalError = console.error;
    startCapturing();
    expect(console.error).not.toBe(originalError);

    stopCapturing();
    expect(console.error).toBe(originalError);
  });

  it("buildTechnicalDetails returns correct structure", () => {
    const details = buildTechnicalDetails("ERR_TEST");
    expect(details.errorCode).toBe("ERR_TEST");
    expect(details.timestamp).toBeTruthy();
    expect(details.userAgent).toBeTruthy();
    expect(details.url).toBeTruthy();
  });

  it("buildNetworkResponse returns correct structure", () => {
    const resp = buildNetworkResponse(404, "Not Found", "page not found");
    expect(resp.status).toBe(404);
    expect(resp.statusText).toBe("Not Found");
    expect(resp.body).toBe("page not found");
  });

  it("buildErrorLogData assembles all data", () => {
    startCapturing();
    console.error("test error");

    const data = buildErrorLogData({
      errorCode: "ERR_500",
      networkStatus: 500,
      networkStatusText: "Internal Server Error",
      networkBody: "server error",
    });

    expect(data.consoleLogs.length).toBeGreaterThanOrEqual(1);
    expect(data.networkResponse).not.toBeNull();
    expect(data.networkResponse!.status).toBe(500);
    expect(data.technicalDetails.errorCode).toBe("ERR_500");
  });
});
