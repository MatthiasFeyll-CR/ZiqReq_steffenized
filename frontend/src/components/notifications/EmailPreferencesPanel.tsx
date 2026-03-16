import { useCallback, useEffect, useMemo, useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useTranslation } from "react-i18next"
import { toast } from "react-toastify"
import { Minus } from "lucide-react"
import { useAuth } from "@/hooks/use-auth"
import { Switch } from "@/components/ui/switch"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"
import {
  fetchEmailPreferences,
  updateEmailPreferences,
} from "@/api/notifications"

interface PreferenceGroup {
  label: string
  requiredRole?: string
  items: { key: string; label: string }[]
}

const PREFERENCE_GROUPS: PreferenceGroup[] = [
  {
    label: "Collaboration",
    items: [
      { key: "collaboration_invitation", label: "Invitation received" },
      { key: "collaborator_joined", label: "Collaborator joined" },
      { key: "collaborator_left", label: "Collaborator left" },
      { key: "removed_from_idea", label: "Removed from idea" },
      { key: "ownership_transferred", label: "Ownership transferred" },
    ],
  },
  {
    label: "Review",
    items: [
      { key: "review_state_changed", label: "Review state changed" },
      { key: "review_comment", label: "Review comment" },
    ],
  },
  {
    label: "Chat",
    items: [{ key: "chat_mention", label: "@mention in chat" }],
  },
  {
    label: "Similarity",
    items: [
      { key: "similarity_alert", label: "Similarity alert" },
      { key: "merge_request_received", label: "Merge request received" },
      { key: "merge_accepted", label: "Merge accepted" },
      { key: "merge_declined", label: "Merge declined" },
      { key: "idea_closed_append", label: "Idea closed (append)" },
    ],
  },
  {
    label: "Review Management",
    requiredRole: "reviewer",
    items: [
      { key: "idea_submitted", label: "Idea submitted" },
      { key: "idea_assigned", label: "Idea assigned" },
      { key: "idea_resubmitted", label: "Idea resubmitted" },
      { key: "append_request_received", label: "Append request received" },
    ],
  },
  {
    label: "System",
    requiredRole: "admin",
    items: [{ key: "monitoring_alert", label: "Monitoring alert" }],
  },
]

interface EmailPreferencesPanelProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

// Event types that default to OFF (opt-in). Must match backend.
const DEFAULT_DISABLED_KEYS = new Set<string>([])

function defaultFor(key: string): boolean {
  return !DEFAULT_DISABLED_KEYS.has(key)
}

const groupLabelKey: Record<string, string> = {
  Collaboration: "collaboration",
  Review: "review",
  Chat: "chat",
  Similarity: "similarity",
  "Review Management": "reviewManagement",
  System: "system",
}

export function EmailPreferencesPanel({
  open,
  onOpenChange,
}: EmailPreferencesPanelProps) {
  const { t } = useTranslation()
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [localPrefs, setLocalPrefs] = useState<Record<string, boolean>>({})
  const [dirty, setDirty] = useState(false)

  const { data } = useQuery({
    queryKey: ["emailPreferences"],
    queryFn: fetchEmailPreferences,
    enabled: open,
  })

  // Sync fetched data into local state when it arrives
  useEffect(() => {
    if (!data) return
    const flat: Record<string, boolean> = {}
    for (const cat of Object.values(data.categories)) {
      for (const [key, val] of Object.entries(cat.preferences)) {
        flat[key] = val
      }
    }
    setLocalPrefs(flat)
    setDirty(false)
  }, [data])

  const visibleGroups = useMemo(
    () =>
      PREFERENCE_GROUPS.filter(
        (g) =>
          !g.requiredRole ||
          (user?.roles ?? []).includes(g.requiredRole),
      ),
    [user],
  )

  const mutation = useMutation({
    mutationFn: updateEmailPreferences,
    onSuccess: () => {
      toast.success(t("emailPrefs.saved"))
      queryClient.invalidateQueries({ queryKey: ["emailPreferences"] })
      setDirty(false)
      onOpenChange(false)
    },
    onError: () => {
      toast.error(t("emailPrefs.failedToSave"))
    },
  })

  const handleToggle = useCallback((key: string, checked: boolean) => {
    setLocalPrefs((prev) => ({ ...prev, [key]: checked }))
    setDirty(true)
  }, [])

  const handleGroupToggle = useCallback(
    (group: PreferenceGroup, checked: boolean) => {
      setLocalPrefs((prev) => {
        const next = { ...prev }
        for (const item of group.items) {
          next[item.key] = checked
        }
        return next
      })
      setDirty(true)
    },
    [],
  )

  const getGroupState = useCallback(
    (group: PreferenceGroup): "all" | "none" | "indeterminate" => {
      const vals = group.items.map((i) => localPrefs[i.key] ?? defaultFor(i.key))
      const allOn = vals.every(Boolean)
      const allOff = vals.every((v) => !v)
      if (allOn) return "all"
      if (allOff) return "none"
      return "indeterminate"
    },
    [localPrefs],
  )

  const handleSave = useCallback(() => {
    mutation.mutate(localPrefs)
  }, [mutation, localPrefs])

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className="w-[480px] max-w-[90vw]"
        onKeyDown={(e: React.KeyboardEvent) => {
          if (e.key === "Enter") {
            e.preventDefault();
            handleSave();
          }
        }}
      >
        <DialogHeader>
          <DialogTitle>{t("emailPrefs.title")}</DialogTitle>
          <DialogDescription>
            {t("emailPrefs.description")}
          </DialogDescription>
        </DialogHeader>

        <div className="max-h-[60vh] space-y-4 overflow-y-auto pr-1">
          {visibleGroups.map((group) => {
            const state = getGroupState(group)
            return (
              <div key={group.label} className="space-y-2">
                <div className="flex items-center gap-2">
                  <Checkbox
                    checked={state === "all" ? true : state === "none" ? false : "indeterminate"}
                    onCheckedChange={(checked) =>
                      handleGroupToggle(group, !!checked)
                    }
                    aria-label={`Toggle all ${group.label}`}
                  />
                  {state === "indeterminate" && (
                    <Minus className="pointer-events-none absolute h-3 w-3 text-current" />
                  )}
                  <span className="text-sm font-semibold text-foreground">
                    {t(`emailPrefs.groups.${groupLabelKey[group.label]}`)}
                  </span>
                </div>
                <div className="ml-6 space-y-1.5">
                  {group.items.map((item) => (
                    <div
                      key={item.key}
                      className="flex items-center justify-between"
                    >
                      <label
                        htmlFor={`pref-${item.key}`}
                        className="text-sm text-muted-foreground"
                      >
                        {t(`emailPrefs.items.${item.key}`, item.label)}
                      </label>
                      <Switch
                        id={`pref-${item.key}`}
                        checked={localPrefs[item.key] ?? defaultFor(item.key)}
                        onCheckedChange={(checked) =>
                          handleToggle(item.key, checked)
                        }
                      />
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>

        <DialogFooter>
          <button
            type="button"
            className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 disabled:pointer-events-none disabled:opacity-50"
            onClick={handleSave}
            disabled={!dirty || mutation.isPending}
          >
            {mutation.isPending ? t("common.saving") : t("common.save")}
          </button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
