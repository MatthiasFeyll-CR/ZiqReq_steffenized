import { cn } from "@/lib/utils"

interface SkipLinkProps {
  targetId?: string
  className?: string
}

function SkipLink({ targetId = "main-content", className }: SkipLinkProps) {
  return (
    <a
      href={`#${targetId}`}
      className={cn(
        "sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[100] focus:rounded focus:bg-primary focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:text-primary-foreground focus:shadow-lg focus:outline-none",
        className
      )}
    >
      Skip to main content
    </a>
  )
}

export { SkipLink }
export type { SkipLinkProps }
