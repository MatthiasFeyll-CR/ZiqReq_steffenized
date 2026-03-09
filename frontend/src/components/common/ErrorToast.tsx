import { Toast, ToastTitle, ToastDescription } from "@/components/ui/toast"

interface ErrorToastProps {
  title?: string
  message: string
  onClose?: () => void
}

function ErrorToast({ title = "Error", message, onClose }: ErrorToastProps) {
  return (
    <Toast variant="error" onClose={onClose}>
      <ToastTitle>{title}</ToastTitle>
      <ToastDescription>{message}</ToastDescription>
    </Toast>
  )
}

export { ErrorToast }
export type { ErrorToastProps }
