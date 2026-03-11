const MAX_LOG_ENTRIES = 20

interface ConsoleLogEntry {
  message: string
  timestamp: string
}

interface NetworkResponseInfo {
  status: number | null
  statusText: string
  body: string
}

interface TechnicalDetails {
  errorCode: string
  timestamp: string
  userAgent: string
  url: string
}

interface ErrorLogData {
  consoleLogs: ConsoleLogEntry[]
  networkResponse: NetworkResponseInfo | null
  technicalDetails: TechnicalDetails
}

const consoleLogs: ConsoleLogEntry[] = []
let originalConsoleError: (typeof console)["error"] | null = null

function startCapturing(): void {
  if (originalConsoleError) return
  originalConsoleError = console.error

  console.error = (...args: unknown[]) => {
    const message = args.map((a) => (typeof a === "string" ? a : JSON.stringify(a))).join(" ")
    consoleLogs.push({
      message,
      timestamp: new Date().toISOString(),
    })
    if (consoleLogs.length > MAX_LOG_ENTRIES) {
      consoleLogs.shift()
    }
    originalConsoleError?.apply(console, args)
  }
}

function stopCapturing(): void {
  if (originalConsoleError) {
    console.error = originalConsoleError
    originalConsoleError = null
  }
}

function getConsoleLogs(): ConsoleLogEntry[] {
  return [...consoleLogs]
}

function clearConsoleLogs(): void {
  consoleLogs.length = 0
}

function buildTechnicalDetails(errorCode?: string): TechnicalDetails {
  return {
    errorCode: errorCode ?? "UNKNOWN",
    timestamp: new Date().toISOString(),
    userAgent: typeof navigator !== "undefined" ? navigator.userAgent : "N/A",
    url: typeof window !== "undefined" ? window.location.href : "N/A",
  }
}

function buildNetworkResponse(
  status: number | null,
  statusText: string,
  body: string,
): NetworkResponseInfo {
  return { status, statusText, body }
}

function buildErrorLogData(options?: {
  errorCode?: string
  networkStatus?: number | null
  networkStatusText?: string
  networkBody?: string
}): ErrorLogData {
  return {
    consoleLogs: getConsoleLogs(),
    networkResponse: options?.networkStatus != null
      ? buildNetworkResponse(
          options.networkStatus,
          options.networkStatusText ?? "",
          options.networkBody ?? "",
        )
      : null,
    technicalDetails: buildTechnicalDetails(options?.errorCode),
  }
}

export {
  startCapturing,
  stopCapturing,
  getConsoleLogs,
  clearConsoleLogs,
  buildTechnicalDetails,
  buildNetworkResponse,
  buildErrorLogData,
  MAX_LOG_ENTRIES,
}
export type {
  ConsoleLogEntry,
  NetworkResponseInfo,
  TechnicalDetails,
  ErrorLogData,
}
