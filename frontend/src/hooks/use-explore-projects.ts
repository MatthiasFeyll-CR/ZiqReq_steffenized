import { useQuery, keepPreviousData } from "@tanstack/react-query";
import { fetchProjects } from "@/api/projects";

interface ExploreFilters {
  search?: string;
  state?: string;
  projectType?: string;
  page?: number;
}

export function useExploreProjects(filters: ExploreFilters = {}) {
  const params: Record<string, string> = {};
  if (filters.search) params.search = filters.search;
  if (filters.state) params.state = filters.state;
  if (filters.projectType) params.project_type = filters.projectType;
  if (filters.page && filters.page > 1) params.page = String(filters.page);

  return useQuery({
    queryKey: ["projects", "explore", params],
    queryFn: () => fetchProjects("explore", params),
    placeholderData: keepPreviousData,
    staleTime: 30_000,
  });
}
