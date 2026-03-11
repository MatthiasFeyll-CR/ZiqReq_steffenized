import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { GitMerge } from "lucide-react";
import { Link } from "react-router-dom";
import type { IdeaRef } from "@/api/ideas";

interface MergedIdeaBannerProps {
  mergedIdeaRef: IdeaRef;
}

export function MergedIdeaBanner({ mergedIdeaRef }: MergedIdeaBannerProps) {
  const prefersReducedMotion = useReducedMotion();

  return (
    <AnimatePresence>
      <motion.div
        initial={prefersReducedMotion ? false : { height: 0, opacity: 0 }}
        animate={{ height: "auto", opacity: 1 }}
        exit={prefersReducedMotion ? { opacity: 0 } : { height: 0, opacity: 0 }}
        transition={{ duration: prefersReducedMotion ? 0 : 0.2 }}
        data-testid="merged-idea-banner"
      >
        <div className="border-b bg-primary/5 px-4 py-3 flex items-center gap-2">
          <GitMerge className="h-4 w-4 text-muted-foreground" />
          <p className="text-sm text-foreground">
            This idea was merged. View merged idea:{" "}
            <Link
              to={mergedIdeaRef.url}
              className="font-medium text-primary underline"
              data-testid="merged-idea-link"
            >
              {mergedIdeaRef.title || "Untitled"}
            </Link>
          </p>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
