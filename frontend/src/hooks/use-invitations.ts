import { useQuery } from "@tanstack/react-query";
import { fetchInvitations } from "@/api/projects";

export function useInvitations() {
  return useQuery({
    queryKey: ["invitations"],
    queryFn: fetchInvitations,
  });
}
