import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { createIdea } from "@/api/ideas";

export function useCreateIdea() {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (firstMessage: string) => createIdea(firstMessage),
    onSuccess: (data) => {
      navigate(`/idea/${data.id}`);
    },
  });
}
