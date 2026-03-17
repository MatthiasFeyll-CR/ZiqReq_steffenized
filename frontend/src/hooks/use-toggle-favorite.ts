import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toggleFavorite } from "@/api/projects";

export function useToggleFavorite() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: toggleFavorite,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });
}
