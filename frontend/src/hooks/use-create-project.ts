import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { ProjectType } from "@/api/projects";

export function useCreateProject() {
  const navigate = useNavigate();
  const [isPending, setIsPending] = useState(false);
  const [variables, setVariables] = useState<ProjectType | undefined>();

  const mutate = useCallback(
    (projectType: ProjectType, options?: { onSuccess?: () => void }) => {
      setIsPending(true);
      setVariables(projectType);
      // Navigate to draft workspace — project is created lazily on first user action
      navigate(`/project/new?type=${projectType}`);
      options?.onSuccess?.();
    },
    [navigate],
  );

  const reset = useCallback(() => {
    setIsPending(false);
    setVariables(undefined);
  }, []);

  return { mutate, isPending, variables, reset };
}
