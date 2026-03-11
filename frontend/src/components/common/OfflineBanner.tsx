import { useSelector } from "react-redux";
import { WifiOff } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import {
  selectConnectionState,
  selectReconnectCountdown,
  selectIsIdleDisconnected,
} from "@/store/websocket-slice";
import { useWsReconnect } from "@/app/providers";

export function OfflineBanner() {
  const connectionState = useSelector(selectConnectionState);
  const countdown = useSelector(selectReconnectCountdown);
  const isIdleDisconnected = useSelector(selectIsIdleDisconnected);
  const reconnect = useWsReconnect();

  const isOffline = connectionState === "offline";

  return (
    <AnimatePresence>
      {isOffline && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.2, ease: "easeOut" }}
          className="overflow-hidden"
          data-testid="offline-banner"
        >
          <div className="flex items-center gap-3 bg-amber-50 dark:bg-amber-950 border border-amber-400 dark:border-amber-600 rounded-md p-4 mx-0">
            <WifiOff className="h-5 w-5 text-amber-600 dark:text-amber-400 flex-shrink-0" />
            <p className="text-sm text-foreground flex-1">
              {isIdleDisconnected
                ? "Connection closed due to inactivity. Move your mouse to reconnect."
                : <>
                    Currently offline.
                    {countdown !== null && countdown > 0
                      ? ` Retrying in ${countdown} seconds`
                      : " Attempting to reconnect\u2026"}
                  </>
              }
            </p>
            {!isIdleDisconnected && (
              <Button
                variant="primary"
                size="sm"
                onClick={reconnect}
                data-testid="reconnect-button"
              >
                Reconnect
              </Button>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
