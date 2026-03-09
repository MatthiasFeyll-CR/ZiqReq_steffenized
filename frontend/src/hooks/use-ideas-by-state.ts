import { useQuery } from "@tanstack/react-query";
import { fetchIdeas } from "@/api/ideas";

export function useIdeasByState(state: string) {
  return useQuery({
    queryKey: ["ideas", "by_state", state],
    queryFn: () => fetchIdeas(undefined, { state }),
  });
}
