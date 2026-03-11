import { useTranslation } from "react-i18next"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog"
import type {
  ConsoleLogEntry,
  NetworkResponseInfo,
  TechnicalDetails,
} from "@/utils/errorLogger"

interface ErrorLogEntry {
  id: string
  message: string
  timestamp: string
}

interface ErrorLogModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  errors?: ErrorLogEntry[]
  consoleLogs?: ConsoleLogEntry[]
  networkResponse?: NetworkResponseInfo | null
  technicalDetails?: TechnicalDetails | null
}

const SUPPORT_EMAIL = "support@commerzreal.de"

function ErrorLogModal({
  open,
  onOpenChange,
  errors = [],
  consoleLogs = [],
  networkResponse = null,
  technicalDetails = null,
}: ErrorLogModalProps) {
  const { t } = useTranslation()

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent data-testid="error-log-modal" aria-describedby="error-log-description">
        <DialogHeader>
          <DialogTitle>{t("errorLog.title")}</DialogTitle>
          <DialogDescription id="error-log-description">
            {t("errorLog.description")}
          </DialogDescription>
        </DialogHeader>
        <div className="max-h-96 space-y-4 overflow-y-auto">
          {/* Console Log Section */}
          <section data-testid="console-log-section">
            <h3 className="mb-2 text-sm font-semibold text-foreground">
              {t("errorLog.consoleLog")}
            </h3>
            {consoleLogs.length === 0 && errors.length === 0 ? (
              <p className="text-sm text-text-secondary">
                {t("errorLog.noConsoleErrors")}
              </p>
            ) : (
              <ul className="space-y-1">
                {consoleLogs.map((entry, index) => (
                  <li
                    key={`console-${index}`}
                    className="rounded border border-border p-2 text-xs font-mono"
                  >
                    <span className="text-text-secondary">
                      {entry.timestamp}
                    </span>{" "}
                    <span className="text-foreground">{entry.message}</span>
                  </li>
                ))}
                {errors.map((entry) => (
                  <li
                    key={entry.id}
                    className="rounded border border-border p-2 text-xs font-mono"
                  >
                    <span className="text-text-secondary">
                      {entry.timestamp}
                    </span>{" "}
                    <span className="text-foreground">{entry.message}</span>
                  </li>
                ))}
              </ul>
            )}
          </section>

          {/* Network Response Section */}
          <section data-testid="network-response-section">
            <h3 className="mb-2 text-sm font-semibold text-foreground">
              {t("errorLog.networkResponse")}
            </h3>
            {networkResponse ? (
              <div className="rounded border border-border p-2 text-xs font-mono space-y-1">
                <p>
                  <span className="text-text-secondary">{t("errorLog.httpStatus")}</span>{" "}
                  <span data-testid="network-status">
                    {networkResponse.status} {networkResponse.statusText}
                  </span>
                </p>
                <p>
                  <span className="text-text-secondary">{t("errorLog.body")}</span>{" "}
                  <span data-testid="network-body">
                    {networkResponse.body}
                  </span>
                </p>
              </div>
            ) : (
              <p className="text-sm text-text-secondary">
                {t("errorLog.noNetworkData")}
              </p>
            )}
          </section>

          {/* Technical Details Section */}
          <section data-testid="technical-details-section">
            <h3 className="mb-2 text-sm font-semibold text-foreground">
              {t("errorLog.technicalDetails")}
            </h3>
            {technicalDetails ? (
              <div className="rounded border border-border p-2 text-xs font-mono space-y-1">
                <p>
                  <span className="text-text-secondary">{t("errorLog.errorCode")}</span>{" "}
                  <span data-testid="error-code">
                    {technicalDetails.errorCode}
                  </span>
                </p>
                <p>
                  <span className="text-text-secondary">{t("errorLog.timestamp")}</span>{" "}
                  <span data-testid="error-timestamp">
                    {technicalDetails.timestamp}
                  </span>
                </p>
                <p>
                  <span className="text-text-secondary">{t("errorLog.userAgent")}</span>{" "}
                  <span data-testid="error-user-agent">
                    {technicalDetails.userAgent}
                  </span>
                </p>
                <p>
                  <span className="text-text-secondary">{t("errorLog.url")}</span>{" "}
                  <span data-testid="error-url">
                    {technicalDetails.url}
                  </span>
                </p>
              </div>
            ) : (
              <p className="text-sm text-text-secondary">
                {t("errorLog.noTechnicalDetails")}
              </p>
            )}
          </section>

          {/* Support Contact Section */}
          <section data-testid="support-contact-section">
            <p className="text-sm text-text-secondary">
              {t("errorLog.supportContact")}{" "}
              <a
                href={`mailto:${SUPPORT_EMAIL}`}
                className="text-primary underline"
              >
                {SUPPORT_EMAIL}
              </a>
            </p>
          </section>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export { ErrorLogModal, SUPPORT_EMAIL }
export type { ErrorLogModalProps, ErrorLogEntry }
