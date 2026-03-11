import { useTranslation } from "react-i18next"
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
  title,
  message,
  onClose,
  onShowLogs,
  onRetry,
  retryCount = 0,
  maxRetries = 3,
}: ErrorToastProps) {
  const { t } = useTranslation()
  const maxRetriesReached = retryCount >= maxRetries

  return (
    <Toast variant="error" onClose={onClose} data-testid="error-toast" role="alert" aria-live="assertive">
      <ToastTitle>{title ?? t("errors.title")}</ToastTitle>
      <ToastDescription>{message}</ToastDescription>
      <div className="mt-2 flex gap-2">
        {onShowLogs && (
          <Button
            variant="outline"
            size="sm"
            onClick={onShowLogs}
            data-testid="show-logs-button"
          >
            {t("errors.showLogs")}
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
            {maxRetriesReached ? t("errors.maxRetriesReached") : t("common.retry")}
          </Button>
        )}
      </div>
    </Toast>
  )
}

export { ErrorToast }
export type { ErrorToastProps }
