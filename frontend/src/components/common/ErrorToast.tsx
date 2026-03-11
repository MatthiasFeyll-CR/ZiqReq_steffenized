import { Toast, ToastTitle, ToastDescription } from "@/components/ui/toast"
import { Button } from "@/components/ui/button"

interface ErrorToastProps {
  title?: string
  message: string
  onClose?: () => void
  onShowLogs?: () => void
  onRetry?: () => void
  retryCount?: number
  maxRetries?: number
}

function ErrorToast({
  title = "Error",
  message,
  onClose,
  onShowLogs,
  onRetry,
  retryCount = 0,
  maxRetries = 3,
}: ErrorToastProps) {
  const maxRetriesReached = retryCount >= maxRetries

  return (
    <Toast variant="error" onClose={onClose} data-testid="error-toast">
      <ToastTitle>{title}</ToastTitle>
      <ToastDescription>{message}</ToastDescription>
      <div className="mt-2 flex gap-2">
        {onShowLogs && (
          <Button
            variant="outline"
            size="sm"
            onClick={onShowLogs}
            data-testid="show-logs-button"
          >
            Show Logs
          </Button>
        )}
        {onRetry && (
          <Button
            variant="primary"
            size="sm"
            onClick={onRetry}
            disabled={maxRetriesReached}
            data-testid="retry-button"
          >
            {maxRetriesReached ? "Max retries reached" : "Retry"}
          </Button>
        )}
      </div>
    </Toast>
  )
}

export { ErrorToast }
export type { ErrorToastProps }
