import { useQuery } from "@tanstack/react-query";
import { fetchProjects } from "@/api/projects";

export function useHighlightedProjects() {
  return useQuery({
    queryKey: ["projects", "highlighted"],
    queryFn: () => fetchProjects("highlighted"),
  });
}
