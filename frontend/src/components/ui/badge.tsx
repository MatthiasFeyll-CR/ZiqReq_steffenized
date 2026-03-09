import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "bg-muted text-foreground",
        // Idea state badges
        open: "bg-sky-100 text-sky-700 dark:bg-sky-900/30 dark:text-sky-400",
        in_review:
          "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
        accepted:
          "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
        dropped: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
        rejected:
          "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
        // Role badges
        user: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
        reviewer:
          "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
        admin: "bg-teal-100 text-teal-700 dark:bg-teal-900/30 dark:text-teal-400",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
