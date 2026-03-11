import { useCallback, useState } from "react"

const DEFAULT_MAX_RETRIES = 3

interface UseErrorHandlerOptions {
  /** The operation to retry on failure */
  retryOperation?: () => void | Promise<void>
  /** Max retry attempts (default: 3, configurable via admin_parameters.max_retry_attempts) */
  maxRetries?: number
  /** Called when "Show Logs" is clicked */
  onShowLogs?: () => void
}

interface UseErrorHandlerReturn {
  retryCount: number
  maxRetries: number
  maxRetriesReached: boolean
  handleRetry: () => void
  handleShowLogs: () => void
  reset: () => void
}

function useErrorHandler({
  retryOperation,
  maxRetries = DEFAULT_MAX_RETRIES,
  onShowLogs,
}: UseErrorHandlerOptions = {}): UseErrorHandlerReturn {
  const [retryCount, setRetryCount] = useState(0)

  const maxRetriesReached = retryCount >= maxRetries

  const handleRetry = useCallback(() => {
    if (retryCount >= maxRetries) return
    setRetryCount((prev) => prev + 1)
    retryOperation?.()
  }, [retryCount, maxRetries, retryOperation])

  const handleShowLogs = useCallback(() => {
    onShowLogs?.()
  }, [onShowLogs])

  const reset = useCallback(() => {
    setRetryCount(0)
  }, [])

  return {
    retryCount,
    maxRetries,
    maxRetriesReached,
    handleRetry,
    handleShowLogs,
    reset,
  }
}

export { useErrorHandler, DEFAULT_MAX_RETRIES }
export type { UseErrorHandlerOptions, UseErrorHandlerReturn }
