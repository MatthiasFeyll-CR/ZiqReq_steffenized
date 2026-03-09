import { useQuery } from "@tanstack/react-query";
import { fetchIdeas } from "@/api/ideas";
import type { IdeasFilters } from "@/hooks/use-ideas-filters";

export function useMyIdeas(filters?: IdeasFilters) {
  const params: Record<string, string> = {};
  if (filters?.search) params.search = filters.search;
  if (filters?.state) params.state = filters.state;

  return useQuery({
    queryKey: ["ideas", "my_ideas", params],
    queryFn: () => fetchIdeas("my_ideas", params),
  });
}
