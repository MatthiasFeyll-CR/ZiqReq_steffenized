import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { createIdea } from "@/api/ideas";

export function useCreateIdea() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (firstMessage: string) => createIdea(firstMessage),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["ideas"] });
      navigate(`/idea/${data.id}`);
    },
  });
}
