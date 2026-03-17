import { useQuery } from "@tanstack/react-query";
import { fetchProjects } from "@/api/projects";

export function useProjectsByState(state: string) {
  return useQuery({
    queryKey: ["projects", "by_state", state],
    queryFn: () => fetchProjects(undefined, { state }),
  });
}
