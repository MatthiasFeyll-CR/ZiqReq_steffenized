import { useMutation, useQueryClient } from "@tanstack/react-query";
import { deleteIdea } from "@/api/ideas";

export function useDeleteIdea() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => deleteIdea(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ideas"] });
    },
  });
}
