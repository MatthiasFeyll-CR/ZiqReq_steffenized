import { useState, useEffect, useRef } from "react";
import { toast } from "react-toastify";
import { UserCard } from "@/components/admin/UserCard";
import { searchUsers, type AdminUser } from "@/api/admin";

export function UsersTab() {
  const [query, setQuery] = useState("");
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  useEffect(() => {
    // Initial load
    setLoading(true);
    searchUsers("")
      .then(setUsers)
      .catch((err) => toast.error(`Failed to load users: ${err.message}`))
      .finally(() => setLoading(false));
  }, []);

  function handleSearch(value: string) {
    setQuery(value);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setLoading(true);
      searchUsers(value)
        .then(setUsers)
        .catch((err) => toast.error(`Failed to search users: ${err.message}`))
        .finally(() => setLoading(false));
    }, 300);
  }

  return (
    <div className="space-y-4 py-6">
      <input
        type="text"
        value={query}
        onChange={(e) => handleSearch(e.target.value)}
        placeholder="Search users by name or email..."
        className="w-full rounded-md border border-border bg-background px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
        data-testid="user-search-input"
      />

      {loading ? (
        <p className="text-sm text-muted-foreground">Searching...</p>
      ) : users.length === 0 ? (
        <p className="text-sm text-muted-foreground">No users found.</p>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3" data-testid="user-card-grid">
          {users.map((user) => (
            <UserCard key={user.id} user={user} />
          ))}
        </div>
      )}
    </div>
  );
}
