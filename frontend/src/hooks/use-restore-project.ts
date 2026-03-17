import { useMutation, useQueryClient } from "@tanstack/react-query";
import { restoreProject } from "@/api/projects";

export function useRestoreProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => restoreProject(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });
}
