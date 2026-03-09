import { useQuery } from "@tanstack/react-query";
import { fetchInvitations } from "@/api/ideas";

export function useInvitations() {
  return useQuery({
    queryKey: ["invitations"],
    queryFn: fetchInvitations,
  });
}
