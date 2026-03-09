import { useMutation, useQueryClient } from "@tanstack/react-query";
import { restoreIdea } from "@/api/ideas";

export function useRestoreIdea() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => restoreIdea(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ideas"] });
    },
  });
}
