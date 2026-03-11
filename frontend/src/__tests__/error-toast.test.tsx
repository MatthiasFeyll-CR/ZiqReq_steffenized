import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { renderHook, act } from "@testing-library/react";
import { ErrorToast } from "@/components/common/ErrorToast";
import { useErrorHandler } from "@/hooks/useErrorHandler";

describe("T-14.1.01: Error toast with buttons", () => {
  it("renders toast with Show Logs and Retry buttons", () => {
    const onShowLogs = vi.fn();
    const onRetry = vi.fn();

    render(
      <ErrorToast
        message="Something went wrong"
        onShowLogs={onShowLogs}
        onRetry={onRetry}
      />,
    );

    expect(screen.getByTestId("error-toast")).toBeInTheDocument();
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();

    const showLogsBtn = screen.getByTestId("show-logs-button");
    expect(showLogsBtn).toBeInTheDocument();
    expect(showLogsBtn.textContent).toBe("Show Logs");

    const retryBtn = screen.getByTestId("retry-button");
    expect(retryBtn).toBeInTheDocument();
    expect(retryBtn.textContent).toBe("Retry");
  });

  it("Show Logs button uses outline variant", () => {
    render(
      <ErrorToast
        message="Error"
        onShowLogs={vi.fn()}
        onRetry={vi.fn()}
      />,
    );
    const showLogsBtn = screen.getByTestId("show-logs-button");
    expect(showLogsBtn.className).toContain("border");
  });

  it("does not render buttons when callbacks are not provided", () => {
    render(<ErrorToast message="Error" />);
    expect(screen.queryByTestId("show-logs-button")).not.toBeInTheDocument();
    expect(screen.queryByTestId("retry-button")).not.toBeInTheDocument();
  });
});

describe("T-14.1.03: Retry triggers operation", () => {
  it("clicking Retry calls the onRetry callback", () => {
    const onRetry = vi.fn();

    render(
      <ErrorToast
        message="Error"
        onRetry={onRetry}
        retryCount={0}
        maxRetries={3}
      />,
    );

    fireEvent.click(screen.getByTestId("retry-button"));
    expect(onRetry).toHaveBeenCalledOnce();
  });

  it("useErrorHandler increments retry count and calls operation", () => {
    const retryOp = vi.fn();
    const { result } = renderHook(() =>
      useErrorHandler({ retryOperation: retryOp, maxRetries: 3 }),
    );

    expect(result.current.retryCount).toBe(0);

    act(() => result.current.handleRetry());
    expect(result.current.retryCount).toBe(1);
    expect(retryOp).toHaveBeenCalledOnce();

    act(() => result.current.handleRetry());
    expect(result.current.retryCount).toBe(2);
    expect(retryOp).toHaveBeenCalledTimes(2);
  });
});

describe("T-14.1.04: Max retries disables button", () => {
  it("disables Retry button and shows 'Max retries reached' when max retries exhausted", () => {
    render(
      <ErrorToast
        message="Error"
        onRetry={vi.fn()}
        retryCount={3}
        maxRetries={3}
      />,
    );

    const retryBtn = screen.getByTestId("retry-button");
    expect(retryBtn).toBeDisabled();
    expect(retryBtn.textContent).toBe("Max retries reached");
  });

  it("useErrorHandler stops retrying after max retries", () => {
    const retryOp = vi.fn();
    const { result } = renderHook(() =>
      useErrorHandler({ retryOperation: retryOp, maxRetries: 2 }),
    );

    act(() => result.current.handleRetry());
    act(() => result.current.handleRetry());
    expect(result.current.retryCount).toBe(2);
    expect(result.current.maxRetriesReached).toBe(true);

    // Further retries should be no-ops
    act(() => result.current.handleRetry());
    expect(result.current.retryCount).toBe(2);
    expect(retryOp).toHaveBeenCalledTimes(2);
  });

  it("Retry button is enabled when retries remain", () => {
    render(
      <ErrorToast
        message="Error"
        onRetry={vi.fn()}
        retryCount={1}
        maxRetries={3}
      />,
    );

    const retryBtn = screen.getByTestId("retry-button");
    expect(retryBtn).not.toBeDisabled();
    expect(retryBtn.textContent).toBe("Retry");
  });
});
