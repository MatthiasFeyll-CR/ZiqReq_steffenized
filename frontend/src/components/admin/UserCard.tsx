import { useTranslation } from "react-i18next";
import type { AdminUser } from "@/api/admin";

interface UserCardProps {
  user: AdminUser;
}

const roleBadgeColors: Record<string, string> = {
  admin: "bg-red-100 text-red-800",
  reviewer: "bg-blue-100 text-blue-800",
  user: "bg-gray-100 text-gray-800",
};

export function UserCard({ user }: UserCardProps) {
  const { t } = useTranslation();
  const initials = `${user.first_name.charAt(0)}${user.last_name.charAt(0)}`.toUpperCase();

  return (
    <div className="rounded-md border bg-card p-4" data-testid={`user-card-${user.id}`}>
      <div className="flex items-start gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-muted text-sm font-medium">
          {initials}
        </div>
        <div className="min-w-0 flex-1">
          <p className="truncate font-medium">{user.display_name}</p>
          <p className="truncate text-sm text-muted-foreground">{user.email}</p>
          <div className="mt-1 flex flex-wrap gap-1">
            {user.roles.map((role) => (
              <span
                key={role}
                className={`rounded-full px-2 py-0.5 text-xs ${roleBadgeColors[role] || "bg-gray-100 text-gray-800"}`}
              >
                {role}
              </span>
            ))}
          </div>
          <p className="mt-2 text-sm text-muted-foreground">
            {t("admin.userStats", { projects: user.project_count, reviews: user.review_count, contributions: user.contribution_count })}
          </p>
        </div>
      </div>
    </div>
  );
}
