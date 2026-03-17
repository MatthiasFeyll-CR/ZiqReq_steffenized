import { useQuery } from "@tanstack/react-query";
import { fetchProjects } from "@/api/projects";

export function useTrash() {
  return useQuery({
    queryKey: ["projects", "trash"],
    queryFn: () => fetchProjects("trash"),
  });
}
