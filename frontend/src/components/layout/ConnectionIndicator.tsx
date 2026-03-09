import { useTranslation } from "react-i18next"

export function ConnectionIndicator() {
  const { t } = useTranslation()

  return (
    <div className="flex items-center gap-1.5 text-xs text-white/80">
      <span className="h-2 w-2 rounded-full bg-green-400" />
      <span className="hidden sm:inline">{t("common.online")}</span>
    </div>
  )
}
