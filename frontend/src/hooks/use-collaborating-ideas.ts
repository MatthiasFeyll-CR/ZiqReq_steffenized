import { useQuery } from "@tanstack/react-query";
import { fetchIdeas } from "@/api/ideas";
import type { IdeasFilters } from "@/hooks/use-ideas-filters";

export function useCollaboratingIdeas(filters?: IdeasFilters) {
  const params: Record<string, string> = {};
  if (filters?.search) params.search = filters.search;
  if (filters?.state) params.state = filters.state;

  return useQuery({
    queryKey: ["ideas", "collaborating", params],
    queryFn: () => fetchIdeas("collaborating", params),
  });
}
