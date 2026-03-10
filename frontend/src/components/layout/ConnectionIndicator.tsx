import { useSelector } from "react-redux"
import { useTranslation } from "react-i18next"
import { selectConnectionState } from "@/store/websocket-slice"

export function ConnectionIndicator() {
  const { t } = useTranslation()
  const connectionState = useSelector(selectConnectionState)
  const isOnline = connectionState === "online"

  return (
    <div className="flex items-center gap-1.5 text-xs text-white/80">
      <span
        className={`h-2 w-2 rounded-full transition-colors duration-200 ${
          isOnline ? "bg-green-400" : "bg-red-400"
        }`}
      />
      <span className="hidden sm:inline">
        {isOnline ? t("common.online") : t("common.offline")}
      </span>
    </div>
  )
}
