import { Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface LoadingSpinnerProps {
  size?: "sm" | "default" | "lg"
  className?: string
  label?: string
}

const sizeClasses = {
  sm: "h-4 w-4",
  default: "h-8 w-8",
  lg: "h-12 w-12",
} as const

function LoadingSpinner({ size = "default", className, label }: LoadingSpinnerProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center gap-2", className)} role="status">
      <Loader2
        className={cn(
          sizeClasses[size],
          "text-primary motion-safe:animate-spin"
        )}
      />
      {label && (
        <span className="text-sm text-text-secondary">{label}</span>
      )}
      <span className="sr-only">{label || "Loading..."}</span>
    </div>
  )
}

export { LoadingSpinner }
export type { LoadingSpinnerProps }
