import { useQuery } from "@tanstack/react-query";
import { fetchIdeas } from "@/api/ideas";

export function useMyIdeas() {
  return useQuery({
    queryKey: ["ideas", "my_ideas"],
    queryFn: () => fetchIdeas("my_ideas"),
  });
}
