import { useTranslation } from "react-i18next";
import { Search, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface FilterBarProps {
  searchInput: string;
  onSearchChange: (value: string) => void;
  stateFilter: string;
  onStateChange: (value: string) => void;
  ownershipFilter: string;
  onOwnershipChange: (value: string) => void;
  hasActiveFilters: boolean;
  onClear: () => void;
}

const STATE_OPTIONS = [
  { value: "open", labelKey: "landing.filter.stateOpen" },
  { value: "in_review", labelKey: "landing.filter.stateInReview" },
  { value: "accepted", labelKey: "landing.filter.stateAccepted" },
  { value: "dropped", labelKey: "landing.filter.stateDropped" },
  { value: "rejected", labelKey: "landing.filter.stateRejected" },
] as const;

const OWNERSHIP_OPTIONS = [
  { value: "my_projects", labelKey: "landing.filter.ownershipMyProjects" },
  { value: "collaborating", labelKey: "landing.filter.ownershipCollaborating" },
] as const;

export function FilterBar({
  searchInput,
  onSearchChange,
  stateFilter,
  onStateChange,
  ownershipFilter,
  onOwnershipChange,
  hasActiveFilters,
  onClear,
}: FilterBarProps) {
  const { t } = useTranslation();

  return (
    <div className="flex flex-wrap items-center gap-3 rounded-lg border border-border bg-surface p-3 shadow-sm dark:shadow-md dark:shadow-black/20">
      <div className="relative min-w-48 flex-1">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-secondary" />
        <Input
          type="text"
          placeholder={t("landing.filter.searchPlaceholder")}
          aria-label={t("landing.filter.searchPlaceholder")}
          value={searchInput}
          onChange={(e) => onSearchChange(e.target.value)}
          className="pl-9 pr-9"
        />
        {searchInput && (
          <button
            type="button"
            onClick={() => onSearchChange("")}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-text-secondary hover:text-foreground"
            aria-label={t("landing.filter.clearSearch")}
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      <Select
        value={stateFilter || "__all__"}
        onValueChange={(v) => onStateChange(v === "__all__" ? "" : v)}
      >
        <SelectTrigger className="w-40">
          <SelectValue placeholder={t("landing.filter.statePlaceholder")} />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="__all__">
            {t("landing.filter.stateAll")}
          </SelectItem>
          {STATE_OPTIONS.map((opt) => (
            <SelectItem key={opt.value} value={opt.value}>
              {t(opt.labelKey)}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select
        value={ownershipFilter || "__all__"}
        onValueChange={(v) => onOwnershipChange(v === "__all__" ? "" : v)}
      >
        <SelectTrigger className="w-40">
          <SelectValue
            placeholder={t("landing.filter.ownershipPlaceholder")}
          />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="__all__">
            {t("landing.filter.ownershipAll")}
          </SelectItem>
          {OWNERSHIP_OPTIONS.map((opt) => (
            <SelectItem key={opt.value} value={opt.value}>
              {t(opt.labelKey)}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {hasActiveFilters && (
        <Button variant="ghost" size="sm" onClick={onClear}>
          {t("landing.filter.clearAll")}
        </Button>
      )}
    </div>
  );
}
