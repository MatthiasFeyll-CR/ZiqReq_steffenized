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
            className="flex flex-col items-center gap-3 bg-amber-50 dark:bg-amber-950 border border-amber-400 dark:border-amber-600 rounded-md p-4 mx-0"
            role="alert"
            aria-live="assertive"
          >
            <div className="flex items-center gap-2">
              <WifiOff className="h-5 w-5 text-amber-600 dark:text-amber-400 flex-shrink-0" />
              <p className="text-sm text-foreground">
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
                  variant="primary"
                  size="sm"
                  onClick={reconnect}
                  data-testid="reconnect-button"
                >
                  {t("offline.reconnect")}
                </Button>
              )}
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
