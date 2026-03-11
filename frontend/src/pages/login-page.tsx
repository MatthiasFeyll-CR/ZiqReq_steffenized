import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "@/hooks/use-auth";
import type { AuthUser } from "@/hooks/use-auth";
import { apiClient } from "@/lib/api-client";

interface DevUser {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  display_name: string;
  roles: string[];
}

const FALLBACK_USERS: DevUser[] = [
  { id: "00000000-0000-0000-0000-000000000001", email: "alice@dev.local", first_name: "Alice", last_name: "Admin", display_name: "Alice Admin", roles: ["admin", "reviewer", "user"] },
  { id: "00000000-0000-0000-0000-000000000002", email: "bob@dev.local", first_name: "Bob", last_name: "Reviewer", display_name: "Bob Reviewer", roles: ["reviewer", "user"] },
  { id: "00000000-0000-0000-0000-000000000003", email: "carol@dev.local", first_name: "Carol", last_name: "User", display_name: "Carol User", roles: ["user"] },
  { id: "00000000-0000-0000-0000-000000000004", email: "dave@dev.local", first_name: "Dave", last_name: "User", display_name: "Dave User", roles: ["user"] },
];

export default function LoginPage() {
  const { isAuthenticated, isDevBypass, setUser } = useAuth();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [devUsers, setDevUsers] = useState<DevUser[]>([]);

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    if (!isDevBypass) return;
    apiClient<{ users: DevUser[] }>("/auth/dev-users")
      .then((data) => setDevUsers(data.users))
      .catch(() => setDevUsers(FALLBACK_USERS));
  }, [isDevBypass]);

  const handleSelect = async (devUser: DevUser) => {
    try {
      await apiClient("/auth/dev-login", {
        method: "POST",
        body: JSON.stringify({ user_id: devUser.id }),
      });
    } catch {
      // Fallback: proceed without session if API unavailable
    }
    setUser(devUser as AuthUser);
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="w-full max-w-sm text-center">
        <h1 className="mb-2 text-3xl font-bold text-gray-900 dark:text-gray-100">
          ZiqReq
        </h1>
        {isDevBypass ? (
          <>
            <p className="mb-6 text-sm text-gray-500 dark:text-gray-400">
              {t("dev.userSwitcher", "Development Login")}
            </p>
            <div className="rounded-lg border border-amber-500/50 bg-amber-50 p-4 shadow-lg dark:bg-amber-950/80">
              <p className="mb-3 text-xs font-bold uppercase tracking-wider text-amber-700 dark:text-amber-400">
                Select a user
              </p>
              <div className="flex flex-col gap-2">
                {devUsers.map((du) => (
                  <button
                    key={du.id}
                    onClick={() => handleSelect(du)}
                    className="rounded px-4 py-2 text-left text-sm transition-colors text-amber-800 hover:bg-amber-100 dark:text-amber-300 dark:hover:bg-amber-900/50"
                  >
                    <span className="font-medium">{du.display_name}</span>
                    <span className="ml-2 text-xs text-amber-600 dark:text-amber-500">
                      {du.roles.join(", ")}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </>
        ) : (
          <p className="text-gray-600 dark:text-gray-400">
            Redirecting to login...
          </p>
        )}
      </div>
    </div>
  );
}
