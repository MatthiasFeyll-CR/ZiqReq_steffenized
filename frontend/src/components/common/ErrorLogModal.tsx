import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog"

interface ErrorLogEntry {
  id: string
  message: string
  timestamp: string
}

interface ErrorLogModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  errors?: ErrorLogEntry[]
}

function ErrorLogModal({ open, onOpenChange, errors = [] }: ErrorLogModalProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Error Log</DialogTitle>
          <DialogDescription>
            Recent errors encountered during this session.
          </DialogDescription>
        </DialogHeader>
        <div className="max-h-80 overflow-y-auto">
          {errors.length === 0 ? (
            <p className="py-4 text-center text-sm text-text-secondary">
              No errors recorded.
            </p>
          ) : (
            <ul className="space-y-2">
              {errors.map((entry) => (
                <li
                  key={entry.id}
                  className="rounded border border-border p-3 text-sm"
                >
                  <p className="font-medium text-foreground">{entry.message}</p>
                  <p className="mt-1 text-xs text-text-secondary">
                    {entry.timestamp}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}

export { ErrorLogModal }
export type { ErrorLogModalProps, ErrorLogEntry }
