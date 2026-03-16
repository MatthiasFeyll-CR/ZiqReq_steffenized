import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { createIdea } from "@/api/ideas";
import { markAiProcessing } from "@/lib/ai-processing-flag";

export function useCreateIdea() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (firstMessage: string) => createIdea(firstMessage),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["ideas"] });
      // Mark that AI processing is in progress for this idea — the backend
      // broadcast happens before the client subscribes to the WebSocket group.
      markAiProcessing(data.id);
      navigate(`/idea/${data.id}`);
    },
  });
}
