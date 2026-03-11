import { AnimatePresence, motion } from "framer-motion";
import { GitMerge } from "lucide-react";
import { Link } from "react-router-dom";
import type { IdeaRef } from "@/api/ideas";

interface AppendedIdeaBannerProps {
  appendedIdeaRef: IdeaRef;
}

export function AppendedIdeaBanner({ appendedIdeaRef }: AppendedIdeaBannerProps) {
  return (
    <AnimatePresence>
      <motion.div
        initial={{ height: 0, opacity: 0 }}
        animate={{ height: "auto", opacity: 1 }}
        exit={{ height: 0, opacity: 0 }}
        transition={{ duration: 0.2 }}
        data-testid="appended-idea-banner"
      >
        <div className="border-b bg-primary/5 px-4 py-3 flex items-center gap-2">
          <GitMerge className="h-4 w-4 text-muted-foreground" />
          <p className="text-sm text-foreground">
            This idea was appended. View target:{" "}
            <Link
              to={appendedIdeaRef.url}
              className="font-medium text-primary underline"
              data-testid="appended-idea-link"
            >
              {appendedIdeaRef.title || "Untitled"}
            </Link>
          </p>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
