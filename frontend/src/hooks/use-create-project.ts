import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { createProject } from "@/api/projects";
import { markAiProcessing } from "@/lib/ai-processing-flag";

export function useCreateProject() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (firstMessage: string) => createProject(firstMessage),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      // Mark that AI processing is in progress for this project — the backend
      // broadcast happens before the client subscribes to the WebSocket group.
      markAiProcessing(data.id);
      navigate(`/project/${data.id}`);
    },
  });
}
