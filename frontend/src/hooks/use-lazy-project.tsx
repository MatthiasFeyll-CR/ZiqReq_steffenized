import { createContext, useCallback, useContext, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { createProject, type Project, type ProjectType } from "@/api/projects";

interface LazyProjectContextValue {
  /** Returns the real project ID — creates the project first if still in draft. */
  ensureProject: () => Promise<string>;
  /** Whether the project is still a local draft (not yet persisted). */
  isDraft: boolean;
}

const LazyProjectContext = createContext<LazyProjectContextValue>({
  ensureProject: () => Promise.reject(new Error("LazyProjectContext not provided")),
  isDraft: false,
});

export function useLazyProject() {
  return useContext(LazyProjectContext);
}

/**
 * Provider for lazy project creation.
 *
 * When projectId is "new", the project hasn't been created yet.
 * `ensureProject()` will create it on first call, update the URL silently,
 * and call `onCreated` with the real project so the parent can update state.
 */
export function LazyProjectProvider({
  projectId,
  projectType,
  onCreated,
  children,
}: {
  projectId: string;
  projectType: ProjectType;
  onCreated: (project: Project) => void;
  children: React.ReactNode;
}) {
  const isDraft = projectId === "new";
  const creatingRef = useRef<Promise<string> | null>(null);
  const queryClient = useQueryClient();

  const ensureProject = useCallback(async (): Promise<string> => {
    if (projectId !== "new") return projectId;

    // Deduplicate concurrent calls — only one creation request
    if (creatingRef.current) return creatingRef.current;

    creatingRef.current = (async () => {
      const response = await createProject(projectType);
      const realProject: Project = {
        id: response.id,
        title: response.title,
        project_type: response.project_type as ProjectType,
        state: response.state as Project["state"],
        visibility: response.visibility as Project["visibility"],
        owner: response.owner ?? { id: "", display_name: "" },
        created_at: response.created_at,
        updated_at: response.created_at,
        collaborators: [],
      };

      // Silently replace URL without triggering React Router re-mount
      window.history.replaceState(null, "", `/project/${response.id}`);

      // Invalidate project list so landing page shows the new project
      queryClient.invalidateQueries({ queryKey: ["projects"] });

      onCreated(realProject);
      return response.id;
    })();

    return creatingRef.current;
  }, [projectId, projectType, onCreated, queryClient]);

  return (
    <LazyProjectContext.Provider value={{ ensureProject, isDraft }}>
      {children}
    </LazyProjectContext.Provider>
  );
}
