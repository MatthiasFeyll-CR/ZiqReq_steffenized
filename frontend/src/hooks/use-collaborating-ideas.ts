import { useQuery } from "@tanstack/react-query";
import { fetchIdeas } from "@/api/ideas";

export function useCollaboratingIdeas() {
  return useQuery({
    queryKey: ["ideas", "collaborating"],
    queryFn: () => fetchIdeas("collaborating"),
  });
}
