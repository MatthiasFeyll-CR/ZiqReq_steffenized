import { useQuery } from "@tanstack/react-query";
import { fetchIdeas } from "@/api/ideas";

export function useTrash() {
  return useQuery({
    queryKey: ["ideas", "trash"],
    queryFn: () => fetchIdeas("trash"),
  });
}
