import { useQuery } from "@tanstack/react-query";
import { fetchProjects } from "@/api/projects";
import type { ProjectsFilters } from "@/hooks/use-projects-filters";

export function useMyProjects(filters?: ProjectsFilters) {
  const params: Record<string, string> = {};
  if (filters?.search) params.search = filters.search;
  if (filters?.state) params.state = filters.state;

  return useQuery({
    queryKey: ["projects", "my_projects", params],
    queryFn: () => fetchProjects("my_projects", params),
  });
}
