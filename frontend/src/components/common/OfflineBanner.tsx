import { useWsReconnect } from "@/app/providers";
import { Button } from "@/components/ui/button";
import {
  selectConnectionState,
  selectIsIdleDisconnected,
  selectReconnectCountdown,
} from "@/store/websocket-slice";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { WifiOff } from "lucide-react";
import { useTranslation } from "react-i18next";
import { useSelector } from "react-redux";

export function OfflineBanner() {
  const { t } = useTranslation();
  const connectionState = useSelector(selectConnectionState);
  const countdown = useSelector(selectReconnectCountdown);
  const isIdleDisconnected = useSelector(selectIsIdleDisconnected);
  const reconnect = useWsReconnect();

  const isOffline = connectionState === "offline";
  const prefersReducedMotion = useReducedMotion();

  return (
    <AnimatePresence>
      {isOffline && (
        <motion.div
          initial={prefersReducedMotion ? false : { height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          exit={prefersReducedMotion ? { opacity: 0 } : { height: 0, opacity: 0 }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.2, ease: "easeOut" }}
          className="overflow-hidden"
          data-testid="offline-banner"
        >
          <div
            className="shrink-0 border-b border-l-4 border-l-amber-400 dark:border-l-amber-500 bg-amber-50 dark:bg-amber-950/20 px-6 py-3 flex items-center gap-3"
            role="alert"
            aria-live="assertive"
          >
              <WifiOff className="h-4 w-4 text-amber-600 dark:text-amber-400 shrink-0" />
              <p className="text-sm text-amber-700 dark:text-amber-400">
                {isIdleDisconnected ? (
                  t("offline.idleDisconnected")
                ) : (
                  <>
                    {t("offline.currentlyOffline")}
                    {countdown !== null && countdown > 0
                      ? ` ${t("offline.retryingIn", { countdown })}`
                      : ` ${t("offline.attemptingReconnect")}`}
                  </>
                )}
              </p>
              {!isIdleDisconnected && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={reconnect}
                  data-testid="reconnect-button"
                  className="ml-3 shrink-0 border-amber-300 text-amber-700 hover:bg-amber-100 dark:border-amber-800 dark:text-amber-400 dark:hover:bg-amber-950/40"
                >
                  {t("offline.reconnect")}
                </Button>
              )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
